import os
basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE = 'office.db'

DEBUG = True
SECRET_KEY = "this is some kind of secret"
DATABASE_PATH = os.path.join(basedir, DATABASE)
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH

MAIL_SERVER='smtp.gmail.com'
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USERNAME = 'timnotifications@gmail.com'
MAIL_PASSWORD = 'tim is not moodle'	

BANK_TYPES = {'SBT': 'State Bank of Travancore',
			  'SBI': 'State Bank of India',
			  'PNB': 'Punjab National Bank',
			  'UBI': 'Union Bank of India'}