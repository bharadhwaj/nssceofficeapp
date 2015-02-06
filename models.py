from werkzeug import generate_password_hash
import datetime

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Employee(db.Model):
	__tablename__ = "employee"
	id = db.Column(db.Integer, primary_key=True)
	empid = db.Column(db.Integer, unique=True)
	name = db.Column(db.String)
	mobilenumber = db.Column(db.Integer)
	email = db.Column(db.String, unique = True)
	gender = db.Column(db.String)
	designation = db.Column(db.String)
	department = db.Column(db.String)
	scheme = db.Column(db.String)
	bank_name = db.Column(db.String)
	accno = db.Column(db.String, unique =True)	
	pan_no = db.Column(db.String, unique = True)	
	basic_pay = db.Column(db.Float)
	

	def __init__(self,empid, name, gender, designation, department, scheme, bank_name, accno, pan_no, mobilenumber, email, basic_pay):
		self.empid = empid
		self.name = name
		self.gender = gender
		self.mobilenumber = mobilenumber
		self.email = email
		self.designation = designation
		self.department = department
		self.scheme = scheme
		self.bank_name = bank_name
		self.accno = accno
		self.pan_no = pan_no
		self.basic_pay = basic_pay
