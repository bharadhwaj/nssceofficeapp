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

DISB_TYPES = {'premiums_cut': 'Premiums Cut',
			   'telephone':'Telephone',
			   'tenancy_rent':'Tenancy Rent',
			   'cs_loan':'CS Loan',
			   'cs_chitty':'CS Chitty',
			   'stamp':'Stamp',
			   'send_off':'Send Off',
			   'welfare_fund':'Welfare Fund',
			   'dte_jp':'DTE JP',
			   'jn':'JN',
			   'indian_bank':'Indian Bank',
			   'pdc_bank':'PDC Bank',
			   'ksfe':'KSFE',
			   'ksc_bank':'KSC Bank',
			   'other1':'Other 1',
			   'other2':'Other 2',
			   'other3':'Other 3'}