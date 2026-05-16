import os

class Config:
    SECRET_KEY          = os.environ.get('SECRET_KEY', 'railbook_super_secret_2024')
    DATABASE            = os.environ.get('DATABASE', 'database.db')
    # Email (Gmail SMTP)
    SMTP_EMAIL          = os.environ.get('SMTP_EMAIL', 'your_email@gmail.com')
    SMTP_PASSWORD       = os.environ.get('SMTP_PASSWORD', 'your_app_password')
    # Payment gateway (simulated)
    PAYMENT_GATEWAY_KEY = os.environ.get('PAYMENT_GATEWAY_KEY', 'test_key_123')
    # App
    HOST                = '0.0.0.0'
    PORT                = 5000
    DEBUG               = True