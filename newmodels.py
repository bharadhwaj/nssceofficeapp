from werkzeug import generate_password_hash
import datetime

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Employee(db.Model):
	__tablename__ = "employee"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String)
	gender = db.Column(db.String)
	designation = db.Column(db.String)
	scheme = db.Colum(db.String)
	bank_name = db.Column(db.String)
	accno = db.Column(db.Strin, unique =True)	
	pan_no = db.Column(db.String)	
	mobilenumber = db.Column(db.Integer)
	email = db.Column(db.String, unique = True)
	basic_pay = db.Column(db.Integer)
	

	def __init__(self, name, gender, designation, scheme, bank_name, accno, pan_no, mobilenumber, email, basic_pay):
		self.name = name
		self.gender = gender
		self.mobilenumber = mobilenumber
		self.email = email
		self.designation = designation
		self.scheme = scheme
		self.bank_name = bank_name
		self.accno = accno
		self.pan_no = pan_no
		self.basic_pay = basic_pay
		
	leaves = db.relationship('leaves', backref='employee', lazy='dynamic')
	
class Leaves(db.Model):
	__tablename__ = "leaves"
	id = db.Column(db.Integer, primary_key = True)
	empid = db.Column(db.Integer, db.ForeignKey('employee.id'))
	month = db.Column(db.String, nullable = False)
	year = db.Column(db.Integer, nullable = False)
	hpa = db.Column(db.Integer, nullable = False)
	lwa = db.Column(db.Integer, nullable = False)
	
	def __init__(self, empid, month, year, hpa, lwa):
		self.empid = empid
		self.month = month
		self.year = year
		self.hpa = hpa
		self.lwa = lwa

class User(db.model):
	__tablename__ = "user"
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String)
	pwd_hash = db.Column(db.String)
