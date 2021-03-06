import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = 'change-it-not-to-be-guessed'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')  # local db
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    REDIS_URL = 'redis://'  # local server
    # Flask-Mail SMTP server settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    SERVER_NAME = '127.0.0.1:5000'

    INSTANCE_DIR = '/home/michal/PycharmProjects/Pointer/instance'
    MAX_MEMORY_MB = 5000  # sample

    ALLOWED_DOMAINS = ['mail.com', 'gmail.com']

    # POINTER EMAIL SENDER
    MAIL_USERNAME = 'mail@mail.com'
    MAIL_PASSWORD = 'password'

    TOKEN_EXPIRES_IN = 600  # seconds

    GROUP_ID = 1
    SPLITWISE_BEARER = 'bearer'

