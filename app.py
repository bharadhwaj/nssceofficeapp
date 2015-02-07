from flask import Flask, request, render_template, url_for, redirect, flash, session, g, send_file, abort
from flask.ext.login import LoginManager
from flask.ext.login import login_user , logout_user , current_user , login_required
from werkzeug import generate_password_hash, check_password_hash
from flask.ext.seasurf import SeaSurf #for csrf protection
from flask_mail import Mail, Message
from flask import copy_current_request_context #for async mail
from threading import Thread
import os
import pytz

from models import Employee
from models import db

app = Flask(__name__)
app.config.from_object('config')


db.init_app(app)
csrf = SeaSurf(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.route('/')
def index():
    employees = Employee.query.all()
    return render_template('employees.html', employees = employees)

@app.route('/employee/<empid>',methods=['GET','POST'])
def editemp(empid):
    if request.method == 'GET':
        employee = Employee.query.filter_by(empid=empid).first()
        if employee:
            return render_template('editemp.html', emp = employee, str=str)

    elif request.method == 'POST':
        app.logger.info(repr(request.form))
        empid = request.form['empid']
        name = request.form['name']
        gender = request.form['gender']
        designation = request.form['designation']
        department = request.form['department']
        emptype = request.form['emp-type']
        accno = request.form['accno']
        bprs = request.form['bp-rs']
        bpps = request.form['bp-ps']
        bank = request.form['bank']
        pan = request.form['pan']
        email = request.form['email']
        mobilenumber = request.form['mobilenumber']
        bp = int(bprs)+(int(bpps)/100.0)
        user = Employee.query.filter_by(empid = empid).first()

        user.empid = empid
        user.name = name
        user.gender = gender
        user.designation = designation
        user.department = department
        user.emptype = emptype
        user.accno = accno
        user.basic_pay = bp
        user.bank_name = bank
        user.pan_no = pan
        user.mobilenumber = mobilenumber
        user.email = email
        user.mobilenumber = mobilenumber

        db.session.commit()

        return render_template('editemp.html', emp = user, str=str)

@app.route('/register',methods=['GET','POST'])
def register():
 
    if request.method == 'GET':
        return render_template('userdetails.html',page="register")

    elif request.method == 'POST':
        app.logger.info(repr(request.form))
        empid = request.form['empid']
        name = request.form['name']
        gender = request.form['gender']
        designation = request.form['designation']
        department = request.form['department']
        emptype = request.form['emp-type']
        accno = request.form['accno']
        bprs = request.form['bp-rs']
        bpps = request.form['bp-ps']
        bank = request.form['bank']
        pan = request.form['pan']
        email = request.form['email']
        mobilenumber = request.form['mobilenumber']
        bp = int(bprs)+(int(bpps)/100.0)
        user = Employee.query.filter_by(empid = empid).first()

        error = False

        if user:
            error = True
            flash('Employee ID already registered','warning')

        if len(mobilenumber) != 10 or not mobilenumber.isdigit():
            error = True
            flash("Mobile number is invalid",'warning')

        #app.logger.info("Error = ", str(error))
        if error:
            return render_template('userdetails.html',page="register",retry=True, oldform = request.form)
        else:
    	    newuser = Employee(empid,name,gender,designation,department, emptype,bank,accno,pan,mobilenumber,email,bp)
    	    newuser.authenticated = True
    	    db.session.add(newuser)
    	    db.session.commit()
	    return redirect(url_for('index'))

@app.route('/leaves/<empid>',methods=['GET','POST'])
def leaves():
	def editemp(empid):
    if request.method == 'GET':
        employee = Employee.query.filter_by(empid=empid).first()
        if employee:
            return render_template('leaves.html', emp = employee, str=str)



@app.route('/test/<template>')
def test(template):
    return render_template(template+'.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8080)
