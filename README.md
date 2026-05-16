# Railway Reservation System

Simple Flask-based demo application for searching trains, booking tickets, and generating PDFs.

Getting started (local):

```bash
git clone https://github.com/siva116k-sudo/siva.git
cd siva
python -m venv venv
./venv/Scripts/Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
python app.py
```

Deployment notes:
- The app reads `HOST` and `PORT` from the environment (falls back to `0.0.0.0:5000`).
- A simple `Procfile` is included (`web: python app.py`) for platforms like Heroku or Render.
- For Socket.IO support in production, consider using `eventlet` or `gevent` workers with `gunicorn`.

Want me to add CI, a license, or deploy it to Render/Heroku? Reply with which service you prefer.
