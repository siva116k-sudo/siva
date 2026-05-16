import smtplib, os
from email.mime.multipart import MIMEMultipart
from email.mime.text      import MIMEText
from email.mime.base      import MIMEBase
from email                import encoders
from config               import Config

def send_booking_confirmation(to_email, pnr, pdf_path, train_name, journey_date):
    try:
        msg            = MIMEMultipart()
        msg['From']    = Config.SMTP_EMAIL
        msg['To']      = to_email
        msg['Subject'] = f'Booking Confirmed – PNR {pnr}'
        body = f"""
Dear Passenger,

Your railway ticket has been confirmed!

  PNR         : {pnr}
  Train       : {train_name}
  Journey Date: {journey_date}

Please find your PDF ticket attached.

Thank you for choosing RailBook.
        """
        msg.attach(MIMEText(body, 'plain'))
        with open(pdf_path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename=ticket_{pnr}.pdf')
        msg.attach(part)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(Config.SMTP_EMAIL, Config.SMTP_PASSWORD)
            s.sendmail(Config.SMTP_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f'[EMAIL ERROR] {e}')
        return False


def send_cancellation_notification(to_email, pnr, train_name, journey_date):
    try:
        msg            = MIMEMultipart()
        msg['From']    = Config.SMTP_EMAIL
        msg['To']      = to_email
        msg['Subject'] = f'Booking Cancelled – PNR {pnr}'
        body = f"""
Dear Passenger,

Your RailBook booking has been cancelled.

  PNR         : {pnr}
  Train       : {train_name}
  Journey Date: {journey_date}

If you would like to book another train, please visit RailBook again.

Thank you,
RailBook Team
        """
        msg.attach(MIMEText(body, 'plain'))
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(Config.SMTP_EMAIL, Config.SMTP_PASSWORD)
            s.sendmail(Config.SMTP_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f'[EMAIL ERROR] {e}')
        return False


def send_waitlist_notification(to_email, pnr, train_name, journey_date):
    try:
        msg            = MIMEMultipart()
        msg['From']    = Config.SMTP_EMAIL
        msg['To']      = to_email
        msg['Subject'] = f'Waitlist Joined – PNR {pnr}'
        body = f"""
Dear Passenger,

You have been added to the waitlist for your selected train.

  PNR         : {pnr}
  Train       : {train_name}
  Journey Date: {journey_date}

We will notify you if a seat becomes available.

Thank you,
RailBook Team
        """
        msg.attach(MIMEText(body, 'plain'))
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(Config.SMTP_EMAIL, Config.SMTP_PASSWORD)
            s.sendmail(Config.SMTP_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f'[EMAIL ERROR] {e}')
        return False


def send_password_reset(to_email, token):
    try:
        msg            = MIMEMultipart()
        msg['From']    = Config.SMTP_EMAIL
        msg['To']      = to_email
        msg['Subject'] = 'RailBook – Password Reset Request'
        reset_link = f'http://localhost:5000/reset_password/{token}'
        body = f"""
Dear User,

A password reset was requested for your RailBook account.

Click the link below to reset your password (valid for 1 hour):
{reset_link}

If you did not request this, please ignore this email.

– RailBook Team
        """
        msg.attach(MIMEText(body, 'plain'))
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as s:
            s.login(Config.SMTP_EMAIL, Config.SMTP_PASSWORD)
            s.sendmail(Config.SMTP_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f'[EMAIL ERROR] {e}')
        return False