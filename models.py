from werkzeug import generate_password_hash
import datetime

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
	"""This is the database model for User Information """
	__tablename__ = "user"
   	id = db.Column(db.Integer, primary_key=True)
    	name = db.Column(db.String, nullable=False)
    	gender = db.Column(db.String, nullable=False)
    	designation = db.Column(db.String, nullable=False)
    	Type = db.Colum(db.String, nullable=False)
     	bank_name = db.Column(db.String, nullable=False)
     	accno = db.Column(db.String,nullable=False, unique =True)  	
    	PAN = db.Column(db.String, nullable=False)  	
    	mobilenumber = db.Column(db.Integer, nullable=False)
     	email = db.Column(db.String, nullable=False, unique = True)
     	basic_pay = db.Column(db.Integer, nulable=False)
     	month = db.Column(db.String, nullable=False, primary_key=True)
     	year = db.Column(db.Integer,nullable=False, primary_key=False)
     	
     	toget = db.relationship('credit', backref='user', lazy='dynamic')
     	leaves_taken = db.relationship('leave', backref='user', lazy='dynamic')
     	cut = db.relationship('debit', backref='user', lazy='dynamic')
     	disperse = db.relationship('dispersement', backref='user', lazy='dynamic')
     	
      def __init__(self, id, name, gender, designation, Type, bank_name, accno, PAN, mobilenumber, email, basic_pay, month, year):
      	self.id = id
        self.name = name
        self.gender = gender
        self.designation = designation
        self.Type = Type
        self.bank_name = bank_name
        self.accno = accno
        self.PAN = PAN
        self.mobilenumber = mobilenumber
        self.email = email
        self.basic_pay = basic_pay
        self.month = month
        self.year = year

 class Credit(db.Model):
	"""This is the database model for Credit Information """
	__tablename__ = "credit" 
	id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
	bpay = db.Column(db.Integer, nullable = False)
	agp = db.Column(db.Integer, nullable = False)
	da = db.Column(db.Integer, nullable = False)
	hra = db.Column(db.Integer, nullable = False)
	other1 = db.Column(db.Integer, nullable = False)
	other2 = db.Column(db.Integer, nullable = False)
	other3 = db.Column(db.Integer, nullable = False)
	gross_sal = db.Column(db.integer, nullable =False)
	month = db.Column(db.String, nullable=False, db.ForeignKey('user.id'), primary_key=True)
     	year = db.Column(db.Integer, nullable=False, db.ForeignKey('user.id'), primary_key=False)
	
	def __init__(self, id, bpay, agp, da, hra, other1, other2, other3, gross_sal, month, year)
	    self.id = id
	    self.bpay = bpay
	    self.agp = agp
	    self.da = da
	    self.hra = hra
	    self.other1 = other1
	    self.other2 = other2
	    self.other3 = other3
	    self.gross_sal = gross_sal
	    self.month = month
	    self.year = year
	    
class Debit(db.Model):
	"""This is the database model for Debit Information """
	__tablename__ = "debit"
	id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
	pf = db.Column(db.Integer, nullable = False)
	pf_loan = db.Column(db.Integer, nullable = False)
	SLI = db.Column(db.Integer, nullable = False)
	FBS = db.Column(db.Integer, nullable = False)
	IT =  db.Column(db.Integer, nullable = False)
	GPIS = db.Column(db.Integer, nullable = False)
	other1 = db.Column(db.Integer, nullable = False)
	other2 = db.Column(db.Integer, nullable = False)
	tot_deduct = db.Column(db.Integer, nullable = False)
	month = db.Column(db.String, nullable=False, db.ForeignKey('user.id'), primary_key=True)
     	year = db.Column(db.Integer, nullable=False, db.ForeignKey('user.id'), primary_key=False)
     	
	def __init__(self, id, bpay, agp, da, hra, other1, other2, other3, gross_sal, month, year)
	    self.id = id
	    self.pf = pf
	    self.pf_loan = pf_loan
	    self.SLI = SLI
	    self.FBS = FBS
	    self.IT = IT
	    self.GPIS =GPIS
	    self.other1 = other1
	    self.other2 = other2
	    self.tot_deduct = tot_deduct
	    self.month = month
	    self.year = year
	    	 
 class Dispersement(db.Model):
	"""This is the database model for Dispersement Information """
	__tablename__ = "dispersement" 
	id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
	LIC =  db.Column(db.Integer, nullable = False)	 
	PLIS =  db.Column(db.Integer, nullable = False)  
	other1 = db.Column(db.Integer, nullable = False)
	other2 = db.Column(db.Integer, nullable = False)
	other3 = db.Column(db.Integer, nullable = False)
	month = db.Column(db.String, nullable=False, db.ForeignKey('user.id'), primary_key=True)
     	year = db.Column(db.Integer, nullable=False, db.ForeignKey('user.id'), primary_key=True)
	
	def __init__(self ,id , LIC, PLIS, other1, other2, other3, month, year)
	    self.id = id
	    self.SLI = SLI
	    self.FBS = FBS
	    self.IT = IT
	    self.GPIS =GPIS
	    self.other1 = other1
	    self.other2 = other2
	    self.tot_deduct = tot_deduct
	    self.month = month
	    self.year = year
	    
class Leaves(db.Model):
	"""This is the database model is for the Leave related data"""
	__tablename__ = "leave"	
	id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
     	basic_pay = db.Column(db.Integer, db.ForeignKey('user.id'), nulable=False)
     	HP_leave = db.Column(db.Integer, nullable=False)
     	LWA_leave = db.Column(db.Integer, nullabele=True)
 	month = db.Column(db.String, nullable=False, db.ForeignKey('user.id'), primary_key=True)
     	year = db.Column(db.Integer, nullable=False, db.ForeignKey('user.id'), primary_key=True)
	
	def __init__(self ,id , basic_pay, final_bp, HP_leave, LWA_leavemonth, year)
	    self.id = id
	    self.SLI = SLI
	    self.FBS = FBS
	    self.IT = IT
	    self.GPIS =GPIS
	    self.other1 = other1
	    self.other2 = other2
	    self.tot_deduct = tot_deduct
	    self.month = month
	    self.year = yea	
