import sqlite3
import hashlib
import secrets
import os
import threading
import time
import random

from datetime import datetime, timedelta

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash,
    send_file,
    g
)

from flask_socketio import SocketIO

from config import Config

from station_locations import STATIONS

from tickets.utils.pdf_generator import generate_ticket_pdf
from tickets.utils.email_service import (
    send_booking_confirmation,
    send_password_reset,
    send_cancellation_notification,
    send_waitlist_notification,
)

from tickets.utils.payment import process_payment

PROMO_CODES = {
    'RAIL10': 0.10,
    'FIRST5': 0.05,
    'BRIDGE20': 0.20,
}

app = Flask(__name__)
app.secret_key = Config.SECRET_KEY

# Use threading mode so Flask-SocketIO does not auto-select Eventlet.
# This avoids the Eventlet deprecation warning when Eventlet is installed.
socketio = SocketIO(app, async_mode='threading')

# ════════════════════════════════════════════════════════════
#  DATABASE
# ════════════════════════════════════════════════════════════
def get_db():
    db = getattr(g, '_db', None)
    if db is None:
        db = g._db = sqlite3.connect(Config.DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_db(exc):
    db = getattr(g, '_db', None)
    if db: db.close()

def init_db():
    db = sqlite3.connect(Config.DATABASE)
    db.row_factory = sqlite3.Row
    db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            username      TEXT    UNIQUE NOT NULL,
            email         TEXT    UNIQUE NOT NULL,
            password      TEXT    NOT NULL,
            is_admin      INTEGER DEFAULT 0,
            reset_token   TEXT,
            token_expiry  TEXT,
            created_at    TEXT    DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS trains (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            train_no        TEXT    UNIQUE NOT NULL,
            train_name      TEXT    NOT NULL,
            from_station    TEXT    NOT NULL,
            to_station      TEXT    NOT NULL,
            departure       TEXT    NOT NULL,
            arrival         TEXT    NOT NULL,
            total_seats     INTEGER NOT NULL,
            available_seats INTEGER NOT NULL,
            price_per_seat  REAL    NOT NULL,
            train_type      TEXT    DEFAULT "Express",
            image           TEXT    DEFAULT "rajdhani.jpg"
        );
        CREATE TABLE IF NOT EXISTS bookings (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            pnr             TEXT    UNIQUE NOT NULL,
            user_id         INTEGER NOT NULL,
            train_id        INTEGER NOT NULL,
            seats           TEXT    NOT NULL,
            journey_date    TEXT    NOT NULL,
            total_price     REAL    NOT NULL,
            seat_class      TEXT    DEFAULT 'Sleeper',
            passenger_name  TEXT,
            passenger_age   INTEGER,
            passenger_gender TEXT,
            passenger_mobile TEXT,
            status          TEXT    DEFAULT "confirmed",
            transaction_id  TEXT,
            booked_at       TEXT,
            FOREIGN KEY (user_id)  REFERENCES users(id),
            FOREIGN KEY (train_id) REFERENCES trains(id)
        );
    ''')

    existing = [row['name'] for row in db.execute('PRAGMA table_info(users)').fetchall()]
    if 'points' not in existing:
        db.execute('ALTER TABLE users ADD COLUMN points INTEGER DEFAULT 0')

    db.executescript('''
        CREATE TABLE IF NOT EXISTS passengers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            full_name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            mobile TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    ''')

    # Admin
    hpw = hashlib.sha256('admin123'.encode()).hexdigest()
    if not db.execute("SELECT id FROM users WHERE username='admin'").fetchone():
        db.execute("INSERT INTO users (username,email,password,is_admin) VALUES (?,?,?,?)",
                   ('admin','admin@railbook.com', hpw, 1))

    # Sample trains
    if db.execute("SELECT COUNT(*) FROM trains").fetchone()[0] == 0:
        trains = [
            ('12001','Rajdhani Express',  'NDLS','MAS','16:30','10:30',72,72,2100.0,'Rajdhani',   'rajdhani.jpg'),
            ('12002','Shatabdi Express',  'NDLS','BCT','06:00','16:00',60,60,1200.0,'Shatabdi',   'shatabdi.jpg'),
            ('12003','Vande Bharat',      'NDLS','LKO','06:00','12:00',50,50,1500.0,'Vande Bharat','vande_bharat.jpg'),
            ('12004','Duronto Express',   'BCT', 'NDLS','08:00','22:00',80,80, 950.0,'Duronto',    'duronto.jpg'),
            ('12005','Garib Rath',        'BCT', 'MAS','20:00','18:00',90,90, 600.0,'Express',     'rajdhani.jpg'),
            ('12006','Jan Shatabdi',      'MAS', 'NDLS','05:30','21:00',64,64, 850.0,'Shatabdi',   'shatabdi.jpg'),
            ('12007','Humsafar Express',  'HWH', 'NDLS','07:00','05:30',80,80,1100.0,'Express',    'duronto.jpg'),
            ('12008','Tejas Express',     'BCT', 'HWH','14:00','08:00',56,56,1800.0,'Tejas',       'vande_bharat.jpg'),
        ]
        db.executemany(
            'INSERT INTO trains (train_no,train_name,from_station,to_station,'
            'departure,arrival,total_seats,available_seats,price_per_seat,train_type,image)'
            ' VALUES (?,?,?,?,?,?,?,?,?,?,?)', trains)
    db.commit()
    db.close()

# ════════════════════════════════════════════════════════════
#  HELPERS
# ════════════════════════════════════════════════════════════
def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()
def gen_pnr():
    ts  = datetime.now().strftime('%d%H%M')
    rnd = secrets.token_hex(2).upper()
    return f'PNR{ts}{rnd}'

def format_duration(departure, arrival):
    try:
        d = datetime.strptime(departure, '%H:%M')
        a = datetime.strptime(arrival, '%H:%M')
        if a <= d:
            a += timedelta(days=1)
        diff = a - d
        hours, minutes = divmod(diff.seconds // 60, 60)
        return f'{hours}h {minutes}m'
    except Exception:
        return 'N/A'

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*a, **kw):
        if 'user_id' not in session:
            flash('Please login first.', 'warning')
            return redirect(url_for('login'))
        return f(*a, **kw)
    return decorated

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*a, **kw):
        if not session.get('is_admin'):
            flash('Admin access required.', 'error')
            return redirect(url_for('index'))
        return f(*a, **kw)
    return decorated

# ════════════════════════════════════════════════════════════
#  ROUTES – PUBLIC
# ════════════════════════════════════════════════════════════
@app.route('/')
def index():
    db     = get_db()
    trains = db.execute('SELECT * FROM trains ORDER BY id LIMIT 8').fetchall()
    return render_template('index.html', trains=trains)

# ── Register ─────────────────────────────────────────────────
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email    = request.form['email'].strip()
        password = request.form['password']
        confirm  = request.form['confirm_password']
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('register'))
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return redirect(url_for('register'))
        db = get_db()
        if db.execute('SELECT id FROM users WHERE username=? OR email=?',
                      (username, email)).fetchone():
            flash('Username or email already exists.', 'error')
            return redirect(url_for('register'))
        db.execute('INSERT INTO users (username,email,password) VALUES (?,?,?)',
                   (username, email, hash_pw(password)))
        db.commit()
        flash('Account created! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# ── Login ────────────────────────────────────────────────────
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        db   = get_db()
        user = db.execute('SELECT * FROM users WHERE username=?', (username,)).fetchone()
        if user and user['password'] == hash_pw(password):
            session['user_id']  = user['id']
            session['username'] = user['username']
            session['is_admin'] = user['is_admin']
            flash(f'Welcome back, {username}!', 'success')
            return redirect(url_for('admin') if user['is_admin'] else url_for('dashboard'))
        flash('Invalid credentials.', 'error')
    return render_template('login.html')

# ── Logout ────────────────────────────────────────────────────
@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('index'))

# ── Forgot Password ───────────────────────────────────────────
@app.route('/forgot_password', methods=['GET','POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email'].strip()
        db    = get_db()
        user  = db.execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
        if user:
            token   = secrets.token_urlsafe(32)
            expiry  = (datetime.now() + timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
            db.execute('UPDATE users SET reset_token=?, token_expiry=? WHERE email=?',
                       (token, expiry, email))
            db.commit()
            try:
                send_password_reset(email, token)
            except Exception:
                pass
        # Always show success (security best practice)
        flash('If that email exists, a reset link has been sent.', 'success')
        return redirect(url_for('login'))
    return render_template('forgot_password.html')

# ── Reset Password ────────────────────────────────────────────
@app.route('/reset_password/<token>', methods=['GET','POST'])
def reset_password(token):
    db   = get_db()
    user = db.execute('SELECT * FROM users WHERE reset_token=?', (token,)).fetchone()
    if not user:
        flash('Invalid or expired reset link.', 'error')
        return redirect(url_for('login'))
    if datetime.now() > datetime.strptime(user['token_expiry'], '%Y-%m-%d %H:%M:%S'):
        flash('Reset link has expired. Please request a new one.', 'error')
        return redirect(url_for('forgot_password'))
    if request.method == 'POST':
        password = request.form['password']
        confirm  = request.form['confirm_password']
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return redirect(request.url)
        if len(password) < 6:
            flash('Password must be at least 6 characters.', 'error')
            return redirect(request.url)
        db.execute('UPDATE users SET password=?, reset_token=NULL, token_expiry=NULL WHERE id=?',
                   (hash_pw(password), user['id']))
        db.commit()
        flash('Password reset successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('reset_password.html', token=token)

# ── PNR Status (public) ───────────────────────────────────────
@app.route('/pnr', methods=['GET','POST'])
def pnr_status():
    booking = train = user = None
    if request.method == 'POST':
        pnr = request.form['pnr'].strip().upper()
        db  = get_db()
        booking = db.execute('SELECT * FROM bookings WHERE pnr=?', (pnr,)).fetchone()
        if booking:
            train = db.execute('SELECT * FROM trains WHERE id=?', (booking['train_id'],)).fetchone()
            user  = db.execute('SELECT username FROM users WHERE id=?', (booking['user_id'],)).fetchone()
        else:
            flash('PNR not found.', 'error')
    return render_template('pnr_status.html', booking=booking, train=train, user=user)

# ════════════════════════════════════════════════════════════
#  ROUTES – LOGGED-IN USER
# ════════════════════════════════════════════════════════════
@app.route('/dashboard')
@login_required
def dashboard():
    db = get_db()
    bookings = db.execute(
        '''SELECT b.*, t.train_name, t.train_no, t.from_station, t.to_station,
                  t.departure, t.arrival, t.image
           FROM bookings b JOIN trains t ON b.train_id=t.id
           WHERE b.user_id=? ORDER BY b.booked_at DESC''',
        (session['user_id'],)).fetchall()
    stats = {
        'total':     len(bookings),
        'confirmed': sum(1 for b in bookings if b['status']=='confirmed'),
        'cancelled': sum(1 for b in bookings if b['status']=='cancelled'),
        'spent':     sum(b['total_price'] for b in bookings if b['status']=='confirmed'),
    }
    return render_template('dashboard.html', bookings=bookings, stats=stats)

@app.route('/profile')
@login_required
def profile():
    db = get_db()
    user = db.execute('SELECT * FROM users WHERE id=?', (session['user_id'],)).fetchone()
    bookings = db.execute(
        '''SELECT b.*, t.train_name, t.train_no, t.from_station, t.to_station
           FROM bookings b JOIN trains t ON b.train_id=t.id
           WHERE b.user_id=? ORDER BY b.booked_at DESC LIMIT 5''',
        (session['user_id'],)).fetchall()
    top_routes = db.execute(
        '''SELECT t.from_station || ' → ' || t.to_station AS route,
                  COUNT(*) AS count
           FROM bookings b JOIN trains t ON b.train_id=t.id
           WHERE b.user_id=? AND b.status='confirmed'
           GROUP BY route ORDER BY count DESC LIMIT 5''',
        (session['user_id'],)).fetchall()
    passengers = db.execute('SELECT * FROM passengers WHERE user_id=? ORDER BY created_at DESC',
                            (session['user_id'],)).fetchall()
    recent_searches = session.get('recent_searches', [])
    return render_template('profile.html', user=user, bookings=bookings,
                           top_routes=top_routes, recent_searches=recent_searches,
                           passengers=passengers)

@app.route('/passengers/add', methods=['POST'])
@login_required
def add_passenger():
    full_name = request.form.get('full_name','').strip()
    age = request.form.get('age','').strip()
    gender = request.form.get('gender','').strip()
    mobile = request.form.get('mobile','').strip()
    if not full_name:
        flash('Passenger name is required.', 'error')
        return redirect(url_for('profile'))
    try:
        age_val = int(age) if age else None
    except ValueError:
        flash('Please enter a valid age.', 'error')
        return redirect(url_for('profile'))
    db = get_db()
    db.execute(
        'INSERT INTO passengers (user_id, full_name, age, gender, mobile) VALUES (?,?,?,?,?)',
        (session['user_id'], full_name, age_val, gender, mobile))
    db.commit()
    flash('Saved passenger profile.', 'success')
    return redirect(url_for('profile'))

# ── Trains list ───────────────────────────────────────────────
@app.route('/trains', methods=['GET','POST'])
@login_required
def trains():
    db = get_db()
    from_st = to_st = date = return_date = train_type = search_query = sort_by = min_price = max_price = ''
    results = []
    return_results = []
    all_trains = db.execute('SELECT * FROM trains').fetchall()
    train_types = ['All'] + sorted({t['train_type'] for t in all_trains if t['train_type']})
    sort_options = [
        ('departure', 'Departure time'),
        ('price_asc', 'Price low → high'),
        ('price_desc', 'Price high → low'),
        ('available', 'Availability'),
    ]

    form = request.form if request.method == 'POST' else request.args
    if request.method == 'POST' or form.get('from_station'):
        from_st      = form.get('from_station','').strip().upper()
        to_st        = form.get('to_station','').strip().upper()
        date         = form.get('journey_date','')
        return_date  = form.get('return_date','')
        train_type   = form.get('train_type', 'All')
        search_query = form.get('search_query', '').strip()
        sort_by      = form.get('sort_by', 'departure')
        min_price    = form.get('min_price','').strip()
        max_price    = form.get('max_price','').strip()

        query = 'SELECT * FROM trains WHERE from_station=? AND to_station=?'
        params = [from_st, to_st]
        if train_type != 'All':
            query += ' AND train_type=?'
            params.append(train_type)
        if search_query:
            query += ' AND (train_no LIKE ? OR train_name LIKE ?)'
            wildcard = f'%{search_query}%'
            params.extend([wildcard, wildcard])
        if min_price:
            try:
                query += ' AND price_per_seat>=?'
                params.append(float(min_price))
            except ValueError:
                pass
        if max_price:
            try:
                query += ' AND price_per_seat<=?'
                params.append(float(max_price))
            except ValueError:
                pass

        if sort_by == 'price_asc':
            query += ' ORDER BY price_per_seat ASC, departure ASC'
        elif sort_by == 'price_desc':
            query += ' ORDER BY price_per_seat DESC, departure ASC'
        elif sort_by == 'available':
            query += ' ORDER BY available_seats DESC, departure ASC'
        else:
            query += ' ORDER BY departure ASC'

        raw_results = db.execute(query, params).fetchall()
        results = [dict(r, duration=format_duration(r['departure'], r['arrival'])) for r in raw_results]

        if return_date:
            reverse_query = 'SELECT * FROM trains WHERE from_station=? AND to_station=?'
            reverse_params = [to_st, from_st]
            if train_type != 'All':
                reverse_query += ' AND train_type=?'
                reverse_params.append(train_type)
            if search_query:
                reverse_query += ' AND (train_no LIKE ? OR train_name LIKE ?)'
                reverse_params.extend([wildcard, wildcard])
            if min_price:
                try:
                    reverse_query += ' AND price_per_seat>=?'
                    reverse_params.append(float(min_price))
                except ValueError:
                    pass
            if max_price:
                try:
                    reverse_query += ' AND price_per_seat<=?'
                    reverse_params.append(float(max_price))
                except ValueError:
                    pass
            if sort_by == 'price_asc':
                reverse_query += ' ORDER BY price_per_seat ASC, departure ASC'
            elif sort_by == 'price_desc':
                reverse_query += ' ORDER BY price_per_seat DESC, departure ASC'
            elif sort_by == 'available':
                reverse_query += ' ORDER BY available_seats DESC, departure ASC'
            else:
                reverse_query += ' ORDER BY departure ASC'
            raw_return = db.execute(reverse_query, reverse_params).fetchall()
            return_results = [dict(r, duration=format_duration(r['departure'], r['arrival'])) for r in raw_return]

        if request.method == 'POST':
            history = session.get('recent_searches', [])
            history.insert(0, {
                'from_st': from_st,
                'to_st': to_st,
                'journey_date': date,
                'return_date': return_date,
                'train_type': train_type,
                'search_query': search_query,
                'sort_by': sort_by,
                'label': f"{from_st} → {to_st} | {date or 'Any date'} | {train_type if train_type!='All' else 'Any type'}"
            })
            session['recent_searches'] = history[:5]

    return render_template('trains.html', results=results, return_results=return_results,
                           all_trains=all_trains, from_st=from_st, to_st=to_st,
                           date=date, return_date=return_date,
                           train_type=train_type, search_query=search_query,
                           sort_by=sort_by, min_price=min_price, max_price=max_price,
                           train_types=train_types, sort_options=sort_options,
                           recent_searches=session.get('recent_searches', []))

@app.route('/waitlist/<int:train_id>', methods=['GET','POST'])
@login_required
def waitlist(train_id):
    db = get_db()
    train = db.execute('SELECT * FROM trains WHERE id=?', (train_id,)).fetchone()
    if not train:
        flash('Train not found.', 'error')
        return redirect(url_for('trains'))

    journey_date = request.args.get('date') or request.form.get('journey_date', '')
    if not journey_date:
        flash('Please choose a journey date before joining the waitlist.', 'warning')
        return redirect(url_for('trains'))

    if request.method == 'POST':
        existing = db.execute(
            'SELECT id FROM bookings WHERE user_id=? AND train_id=? AND journey_date=? AND status IN ("confirmed","waitlist")',
            (session['user_id'], train_id, journey_date)).fetchone()
        if existing:
            flash('You already have a confirmed booking or waitlist for this train.', 'error')
            return redirect(url_for('dashboard'))

        pnr = gen_pnr()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cur = db.execute(
            'INSERT INTO bookings (pnr,user_id,train_id,seats,journey_date,total_price,status,transaction_id,booked_at) '
            'VALUES (?,?,?,?,?,?,?,?,?)',
            (pnr, session['user_id'], train_id, 'WAITLIST', journey_date, 0.0, 'waitlist', None, now)
        )
        db.commit()
        wait_id = cur.lastrowid
        position = db.execute(
            'SELECT COUNT(*) AS pos FROM bookings WHERE train_id=? AND journey_date=? AND status="waitlist" AND id<=?'
            , (train_id, journey_date, wait_id)).fetchone()['pos']
        user = db.execute('SELECT * FROM users WHERE id=?', (session['user_id'],)).fetchone()
        try:
            send_waitlist_notification(user['email'], pnr, train['train_name'], journey_date)
        except Exception:
            pass
        flash(f'Added to waitlist at position {position}. We will confirm your seat automatically when one becomes available.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('waitlist.html', train=train, journey_date=journey_date, position=None, date=journey_date)

# ── Booking (seat selection) ──────────────────────────────────
@app.route('/booking/<int:train_id>', methods=['GET','POST'])
@login_required
def booking(train_id):
    db    = get_db()
    train = db.execute('SELECT * FROM trains WHERE id=?', (train_id,)).fetchone()
    if not train:
        flash('Train not found.', 'error')
        return redirect(url_for('trains'))
    journey_date = request.args.get('date') or request.form.get('journey_date', '')
    booked_raw   = db.execute(
        'SELECT seats FROM bookings WHERE train_id=? AND journey_date=? AND status="confirmed"',
        (train_id, journey_date)).fetchall()
    booked_seats = set()
    for r in booked_raw:
        for s in r['seats'].split(','):
            booked_seats.add(s.strip())

    seat_classes = [('Sleeper', 1.0), ('3AC', 1.4), ('2AC', 1.8), ('1AC', 2.5)]
    passengers = db.execute('SELECT * FROM passengers WHERE user_id=? ORDER BY created_at DESC',
                            (session['user_id'],)).fetchall()
    selected_class = request.form.get('seat_class', 'Sleeper') if request.method == 'POST' else 'Sleeper'

    if request.method == 'POST':
        selected = request.form.getlist('seats')
        seat_class = request.form.get('seat_class', 'Sleeper')
        passenger_id = request.form.get('passenger_id', '')
        passenger_name = request.form.get('passenger_name', '').strip()
        passenger_age = request.form.get('passenger_age', '')
        passenger_gender = request.form.get('passenger_gender', '')
        passenger_mobile = request.form.get('passenger_mobile', '').strip()

        if passenger_id and passenger_id != 'new':
            saved = db.execute('SELECT * FROM passengers WHERE id=? AND user_id=?',
                               (passenger_id, session['user_id'])).fetchone()
            if saved:
                passenger_name = saved['full_name']
                passenger_age = saved['age']
                passenger_gender = saved['gender']
                passenger_mobile = saved['mobile']

        if not selected:
            flash('Please select at least one seat.', 'error')
            return redirect(request.url)
        if not passenger_name:
            flash('Please enter passenger name.', 'error')
            return redirect(request.url)

        multiplier = dict(seat_classes).get(seat_class, 1.0)
        seat_price = round(train['price_per_seat'] * multiplier, 2)
        total_price = round(len(selected) * seat_price, 2)

        session['booking_draft'] = {
            'train_id': train_id,
            'journey_date': journey_date,
            'seats': selected,
            'seat_class': seat_class,
            'seat_price': seat_price,
            'total': total_price,
            'passenger_name': passenger_name,
            'passenger_age': passenger_age,
            'passenger_gender': passenger_gender,
            'passenger_mobile': passenger_mobile,
            'promo_code': '',
            'discount': 0.0,
            'points_redeemed': 0,
            'final_total': total_price
        }
        return redirect(url_for('payment'))

    return render_template('booking.html', train=train, journey_date=journey_date,
                           booked_seats=booked_seats, total_seats=train['total_seats'],
                           seat_classes=seat_classes, passengers=passengers,
                           selected_class=selected_class)

# ── Payment ────────────────────────────────────────────────────
@app.route('/payment', methods=['GET','POST'])
@login_required
def payment():
    draft = session.get('booking_draft')
    if not draft:
        return redirect(url_for('trains'))
    db    = get_db()
    train = db.execute('SELECT * FROM trains WHERE id=?', (draft['train_id'],)).fetchone()
    user  = db.execute('SELECT * FROM users WHERE id=?', (session['user_id'],)).fetchone()

    if request.method == 'POST':
        promo_code = request.form.get('promo_code','').strip().upper()
        discount_rate = PROMO_CODES.get(promo_code, 0.0)
        if promo_code and discount_rate == 0.0:
            flash('Promo code not recognized. Proceeding without discount.', 'warning')
            promo_code = ''

        original_total = draft['total']
        discount_amount = round(original_total * discount_rate, 2)
        subtotal = round(original_total - discount_amount, 2)

        requested_points = 0
        try:
            requested_points = int(request.form.get('use_points','0') or 0)
        except ValueError:
            requested_points = 0
        points_value = min(requested_points, user['points'], int(subtotal))
        final_total = round(subtotal - points_value, 2)

        draft['promo_code'] = promo_code
        draft['discount'] = discount_amount
        draft['points_redeemed'] = points_value
        draft['final_total'] = final_total
        session['booking_draft'] = draft

        result = process_payment(
            request.form.get('card_number',''),
            request.form.get('card_name',''),
            request.form.get('expiry',''),
            request.form.get('cvv',''),
            final_total
        )
        if result['success']:
            pnr       = gen_pnr()
            seats_str = ','.join(draft['seats'])
            now       = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            points_earned = int(final_total // 10)
            db.execute(
                'INSERT INTO bookings (pnr,user_id,train_id,seats,journey_date,total_price,seat_class,passenger_name,passenger_age,passenger_gender,passenger_mobile,status,transaction_id,booked_at) '
                'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)',
                (pnr, session['user_id'], draft['train_id'], seats_str,
                 draft['journey_date'], final_total, draft.get('seat_class','Sleeper'),
                 draft.get('passenger_name'), draft.get('passenger_age'),
                 draft.get('passenger_gender'), draft.get('passenger_mobile'),
                 'confirmed', result['transaction_id'], now))
            db.execute('UPDATE trains SET available_seats=available_seats-? WHERE id=?',
                       (len(draft['seats']), draft['train_id']))
            if points_value > 0 or points_earned > 0:
                db.execute('UPDATE users SET points=points-?+? WHERE id=?',
                           (points_value, points_earned, session['user_id']))
            db.commit()
            # Generate PDF
            booking = db.execute('SELECT * FROM bookings WHERE pnr=?', (pnr,)).fetchone()
            try:
                pdf_path = generate_ticket_pdf(booking, train, user)
                send_booking_confirmation(user['email'], pnr, pdf_path,
                                          train['train_name'], draft['journey_date'])
            except Exception:
                pass
            session.pop('booking_draft', None)
            session['last_pnr'] = pnr
            return redirect(url_for('success'))
        else:
            session['payment_error'] = result['message']
            return redirect(url_for('failed'))
    return render_template('payment.html', train=train, draft=draft, user=user)

# ── Success ────────────────────────────────────────────────────
@app.route('/success')
@login_required
def success():
    pnr = session.pop('last_pnr', None)
    if not pnr:
        return redirect(url_for('dashboard'))
    db      = get_db()
    booking = db.execute('SELECT * FROM bookings WHERE pnr=?', (pnr,)).fetchone()
    train   = db.execute('SELECT * FROM trains WHERE id=?', (booking['train_id'],)).fetchone()
    return render_template('success.html', booking=booking, train=train)

# ── Failed ─────────────────────────────────────────────────────
@app.route('/failed')
@login_required
def failed():
    error = session.pop('payment_error', 'Payment failed. Please try again.')
    return render_template('failed.html', error=error)

# ── Ticket view ────────────────────────────────────────────────
@app.route('/ticket/<pnr>')
@login_required
def ticket(pnr):
    db      = get_db()
    booking = db.execute('SELECT * FROM bookings WHERE pnr=?', (pnr,)).fetchone()
    if not booking or (booking['user_id'] != session['user_id'] and not session.get('is_admin')):
        flash('Ticket not found.', 'error')
        return redirect(url_for('dashboard'))
    train = db.execute('SELECT * FROM trains WHERE id=?', (booking['train_id'],)).fetchone()
    user  = db.execute('SELECT * FROM users WHERE id=?', (booking['user_id'],)).fetchone()
    return render_template('ticket.html', booking=booking, train=train, user=user)

# ── Download PDF ───────────────────────────────────────────────
@app.route('/download/<pnr>')
@login_required
def download(pnr):
    db      = get_db()
    booking = db.execute('SELECT * FROM bookings WHERE pnr=?', (pnr,)).fetchone()
    if not booking or (booking['user_id'] != session['user_id'] and not session.get('is_admin')):
        flash('Access denied.', 'error')
        return redirect(url_for('dashboard'))
    train = db.execute('SELECT * FROM trains WHERE id=?', (booking['train_id'],)).fetchone()
    user  = db.execute('SELECT * FROM users WHERE id=?', (booking['user_id'],)).fetchone()
    path  = generate_ticket_pdf(booking, train, user)
    return send_file(path, as_attachment=True, download_name=f'ticket_{pnr}.pdf')

# ── Cancel ─────────────────────────────────────────────────────
def auto_confirm_waitlist(train_id, journey_date):
    db = get_db()
    waitlist = db.execute(
        'SELECT * FROM bookings WHERE train_id=? AND journey_date=? AND status="waitlist" ORDER BY booked_at ASC LIMIT 1',
        (train_id, journey_date)).fetchone()
    if not waitlist:
        return None

    train = db.execute('SELECT * FROM trains WHERE id=?', (train_id,)).fetchone()
    if train['available_seats'] <= 0:
        return None

    txn_id = 'WTL' + str(int(time.time())) + str(random.randint(100, 999))
    db.execute('UPDATE bookings SET status=?, total_price=?, transaction_id=? WHERE id=?',
               ('confirmed', train['price_per_seat'], txn_id, waitlist['id']))
    db.execute('UPDATE trains SET available_seats=available_seats-1 WHERE id=?', (train_id,))
    db.commit()
    return waitlist

@app.route('/cancel/<pnr>', methods=['POST'])
@login_required
def cancel(pnr):
    db      = get_db()
    booking = db.execute('SELECT * FROM bookings WHERE pnr=? AND user_id=?',
                         (pnr, session['user_id'])).fetchone()
    if booking and booking['status'] == 'confirmed':
        count = len(booking['seats'].split(','))
        db.execute("UPDATE bookings SET status='cancelled' WHERE pnr=?", (pnr,))
        db.execute('UPDATE trains SET available_seats=available_seats+? WHERE id=?',
                   (count, booking['train_id']))
        db.commit()
        try:
            user = db.execute('SELECT * FROM users WHERE id=?', (session['user_id'],)).fetchone()
            send_cancellation_notification(user['email'], booking['pnr'],
                                           db.execute('SELECT train_name FROM trains WHERE id=?', (booking['train_id'],)).fetchone()['train_name'],
                                           booking['journey_date'])
        except Exception:
            pass

        waitlist_booking = auto_confirm_waitlist(booking['train_id'], booking['journey_date'])
        if waitlist_booking:
            wait_user = db.execute('SELECT * FROM users WHERE id=?', (waitlist_booking['user_id'],)).fetchone()
            wait_train = db.execute('SELECT * FROM trains WHERE id=?', (waitlist_booking['train_id'],)).fetchone()
            try:
                send_booking_confirmation(wait_user['email'], waitlist_booking['pnr'],
                                          generate_ticket_pdf(waitlist_booking, wait_train, wait_user),
                                          wait_train['train_name'], waitlist_booking['journey_date'])
            except Exception:
                pass
            flash(f'Booking {pnr} cancelled. A waitlist booking ({waitlist_booking["pnr"]}) has been confirmed.', 'success')
        else:
            flash(f'Booking {pnr} cancelled.', 'success')
    else:
        flash('Cannot cancel this booking.', 'error')
    return redirect(url_for('dashboard'))

# ════════════════════════════════════════════════════════════
#  ROUTES – ADMIN
# ════════════════════════════════════════════════════════════
@app.route('/admin')
@login_required
@admin_required
def admin():
    db = get_db()
    trains_list = db.execute('SELECT * FROM trains ORDER BY id DESC').fetchall()
    bookings    = db.execute(
        '''SELECT b.*,t.train_name,u.username FROM bookings b
           JOIN trains t ON b.train_id=t.id JOIN users u ON b.user_id=u.id
           ORDER BY b.booked_at DESC LIMIT 30''').fetchall()
    users       = db.execute('SELECT * FROM users ORDER BY id DESC').fetchall()
    popular_route = db.execute(
        '''SELECT t.from_station || ' → ' || t.to_station AS route, COUNT(*) AS count
           FROM bookings b JOIN trains t ON b.train_id=t.id
           WHERE b.status='confirmed'
           GROUP BY route ORDER BY count DESC LIMIT 1''').fetchone()
    popular_train = db.execute(
        '''SELECT t.train_name || ' #' || t.train_no AS train, COUNT(*) AS count
           FROM bookings b JOIN trains t ON b.train_id=t.id
           WHERE b.status='confirmed'
           GROUP BY t.id ORDER BY count DESC LIMIT 1''').fetchone()
    total_seats = db.execute('SELECT COALESCE(SUM(total_seats),0) FROM trains').fetchone()[0]
    occupied_seats = db.execute(
        'SELECT COALESCE(SUM(total_price / price_per_seat),0) FROM bookings b JOIN trains t ON b.train_id=t.id WHERE b.status="confirmed"').fetchone()[0]
    avg_occupancy = int((occupied_seats / total_seats * 100) if total_seats else 0)
    stats = {
        'trains':   db.execute('SELECT COUNT(*) FROM trains').fetchone()[0],
        'bookings': db.execute("SELECT COUNT(*) FROM bookings WHERE status='confirmed'").fetchone()[0],
        'users':    db.execute('SELECT COUNT(*) FROM users WHERE is_admin=0').fetchone()[0],
        'revenue':  db.execute("SELECT COALESCE(SUM(total_price),0) FROM bookings WHERE status='confirmed'").fetchone()[0],
        'waitlist': db.execute("SELECT COUNT(*) FROM bookings WHERE status='waitlist'").fetchone()[0],
        'popular_route': popular_route['route'] if popular_route else '—',
        'popular_train': popular_train['train'] if popular_train else '—',
        'average_occupancy': avg_occupancy,
    }
    return render_template('admin.html', trains=trains_list, bookings=bookings,
                           users=users, stats=stats)

@app.route('/admin/add_train', methods=['POST'])
@login_required
@admin_required
def add_train():
    db = get_db()
    total = int(request.form['total_seats'])
    img   = request.form.get('image','rajdhani.jpg')
    db.execute(
        'INSERT INTO trains (train_no,train_name,from_station,to_station,'
        'departure,arrival,total_seats,available_seats,price_per_seat,train_type,image)'
        ' VALUES (?,?,?,?,?,?,?,?,?,?,?)',
        (request.form['train_no'], request.form['train_name'],
         request.form['from_station'].upper(), request.form['to_station'].upper(),
         request.form['departure'], request.form['arrival'],
         total, total, float(request.form['price_per_seat']),
         request.form['train_type'], img))
    db.commit()
    flash('Train added.', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/delete_train/<int:tid>', methods=['POST'])
@login_required
@admin_required
def delete_train(tid):
    # FIX 2: Use a single db reference for both execute and commit
    db = get_db()
    db.execute('DELETE FROM trains WHERE id=?', (tid,))
    db.commit()
    flash('Train deleted.', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/delete_user/<int:uid>', methods=['POST'])
@login_required
@admin_required
def delete_user(uid):
    if uid == session['user_id']:
        flash('Cannot delete yourself.', 'error')
    else:
        db = get_db()
        db.execute('DELETE FROM users WHERE id=?', (uid,))
        db.commit()
        flash('User deleted.', 'success')
    return redirect(url_for('admin'))

@app.route('/admin/update_booking/<pnr>', methods=['POST'])
@login_required
@admin_required
def update_booking(pnr):
    action = request.form.get('action')
    db = get_db()
    booking = db.execute('SELECT * FROM bookings WHERE pnr=?', (pnr,)).fetchone()
    if not booking:
        flash('Booking not found.', 'error')
        return redirect(url_for('admin'))
    seat_count = len(booking['seats'].split(','))

    if action == 'cancel' and booking['status'] == 'confirmed':
        db.execute("UPDATE bookings SET status='cancelled' WHERE pnr=?", (pnr,))
        db.execute('UPDATE trains SET available_seats=available_seats+? WHERE id=?',
                   (seat_count, booking['train_id']))
        db.commit()
        flash(f'Booking {pnr} cancelled.', 'success')
    elif action == 'confirm' and booking['status'] == 'cancelled':
        train = db.execute('SELECT available_seats FROM trains WHERE id=?',
                           (booking['train_id'],)).fetchone()
        if train and train['available_seats'] >= seat_count:
            db.execute("UPDATE bookings SET status='confirmed' WHERE pnr=?", (pnr,))
            db.execute('UPDATE trains SET available_seats=available_seats-? WHERE id=?',
                       (seat_count, booking['train_id']))
            db.commit()
            flash(f'Booking {pnr} re-confirmed.', 'success')
        else:
            flash('Not enough available seats to confirm this booking.', 'error')
    else:
        flash('Invalid booking action.', 'error')
    return redirect(url_for('admin'))

# ════════════════════════════════════════════════════
#  LIVE TRAIN TRACKING
# ════════════════════════════════════════════════════════════

live_trains = {}

# FIX 3: initialize_live_trains uses a direct DB connection (not get_db)
# because it runs outside a request context
def initialize_live_trains():
    db = sqlite3.connect(Config.DATABASE)
    db.row_factory = sqlite3.Row
    trains = db.execute('SELECT * FROM trains').fetchall()
    db.close()

    for train in trains:
        source      = train['from_station']
        destination = train['to_station']

        if source in STATIONS and destination in STATIONS:
            start = STATIONS[source]
            end   = STATIONS[destination]

            live_trains[train['train_no']] = {
                'train_name':   train['train_name'],
                'lat':          start[0],
                'lng':          start[1],
                'dest_lat':     end[0],
                'dest_lng':     end[1],
                'speed':        random.randint(60, 140),
                'status':       'Running',
                'last_updated': datetime.now().strftime('%H:%M:%S'),
            }

# FIX 4: move_trains is now a proper module-level function (not nested),
# and is launched as a daemon thread after init
def move_trains():
    while True:
        for train_no, train in list(live_trains.items()):
            train['lat'] += (train['dest_lat'] - train['lat']) * 0.01
            train['lng'] += (train['dest_lng'] - train['lng']) * 0.01
            train['speed']        = random.randint(60, 140)
            train['last_updated'] = datetime.now().strftime('%H:%M:%S')

            socketio.emit('train_update', {
                'train_no':   train_no,
                'train_name': train['train_name'],
                'lat':        train['lat'],
                'lng':        train['lng'],
                'speed':      train['speed'],
                'status':     train['status'],
                'updated':    train['last_updated'],
            })

        time.sleep(3)

# FIX 5: /live_map route is at module level (not buried inside move_trains)
@app.route('/live_map')
@login_required
def live_map():
    return render_template('live_map.html')

# ════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════
if __name__ == '__main__':
    with app.app_context():
        init_db()

    # FIX 6: Initialize live trains and start background thread here,
    # after the DB is ready and outside any app/request context
    initialize_live_trains()
    t = threading.Thread(target=move_trains, daemon=True)
    t.start()

    socketio.run(app, host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)