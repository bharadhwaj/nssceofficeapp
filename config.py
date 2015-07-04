import os
basedir = os.path.abspath(os.path.dirname(__file__))

DATABASE = 'office.db'

DEBUG = True
SECRET_KEY = "this is some kind of secret"
DATABASE_PATH = os.path.join(basedir, DATABASE)
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DATABASE_PATH

BANK_TYPES = {'SBT': 'State Bank of Travancore',
			  'SBI': 'State Bank of India',
			  'PNB': 'Punjab National Bank',
			  'UBI': 'Union Bank of India'}