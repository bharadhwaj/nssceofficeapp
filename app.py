from flask import Flask, request, render_template, url_for, redirect, flash, session, g, send_file, abort
from flask.ext.login import LoginManager
from flask.ext.login import login_user , logout_user , current_user , login_required
from werkzeug import generate_password_hash, check_password_hash
from flask.ext.seasurf import SeaSurf #for csrf protection
from flask_mail import Mail, Message
from flask import copy_current_request_context #for async mail
from flask import jsonify
from threading import Thread
import os
import pytz
import json

from models import Employee, User, SalaryPeriod, SalarySlip
from models import db

app = Flask(__name__)
app.config.from_object('config')


db.init_app(app)
csrf = SeaSurf(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.before_request
def before_request():
    g.user = current_user


@app.route('/')
@login_required
def index():
    employees = Employee.query.all()
    return render_template('employees.html', employees = employees)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if g.user is not None and g.user.is_authenticated():
            return redirect(url_for('index'))
        return render_template('login.html',page="login")

    elif request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.pwdhash, password):
                user.authenticated = True
                db.session.commit()
                login_user(user)
                return redirect(url_for('index'))

        flash('Username or Password is invalid' , 'warning')
        return render_template("login.html",page="login")


@app.route('/logout')
@login_required
def logout():
    g.user.authenticated = False
    db.session.commit()
    logout_user()
    return redirect(url_for('index'))


@app.route('/employee/<empid>',methods=['GET','POST'])
@login_required
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
@login_required
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

@app.route('/newreport', methods=['GET','POST'])
@login_required
def newreport():
    if request.method == 'GET':
        if SalaryPeriod.query.filter_by(completed=False).first():
            return redirect(url_for('reportentry'))
        else:
            return render_template('newperiod.html')

    if request.method == 'POST':
        app.logger.info(repr(request.form))
        year = int(request.form['year'])
        month = int(request.form['month'])

        hra = float(request.form['hra'])

        da_qip = float(request.form['qip'])
        da_state = float(request.form['state'])
        da_ugc = float(request.form['ugc'])
        da_aicte = float(request.form['aicte'])

        newperiod = SalaryPeriod(year, month, hra, da_qip, da_state, da_ugc, da_aicte, g.user.id)
        db.session.add(newperiod)
        db.session.commit()

        return redirect(url_for('reportentry'))

@app.route('/reportentry', methods=['GET','POST'])
@login_required
def reportentry():
    employees = Employee.query.all()
    period = SalaryPeriod.query.filter_by(completed=False).first()
    updatedemps = [emp.id for emp in SalarySlip.query.filter_by(period_id = period.id).all()]
    app.logger.info('period %r, updatedemps %r' %(period, updatedemps))
    progress = (float(len(updatedemps)) / len(employees) )* 100

    if request.method == 'POST':
        empid = request.form['empid']
        employee = Employee.query.get(int(empid))
        basic_pay = float(request.form['basic_pay'])
        agp = float(request.form['agp'])
        da = float(request.form['da'])
        hra = float(request.form['hra'])
        other = float(request.form['other'])
        pf = float(request.form['pf'])
        pfloan = float(request.form['pfloan'])
        sli = float(request.form['sli'])
        fbs = float(request.form['fbs'])
        gis = float(request.form['gis'])
        it = float(request.form['it'])
        gpis = float(request.form['gpis'])
        other2 = float(request.form['other2'])

        if request.form['hasslip'] == 'True':
            slip = SalarySlip.query.filter_by(employee_id = int(empid), period_id = period.id).first()
            db.session.delete(slip)
            db.session.commit()

        empslip = SalarySlip(period.id, employee.id, basic_pay, agp, da, hra, other, 
            pf, pfloan, sli, fbs, gis, it, gpis, other2)

        db.session.add(empslip)
        db.session.commit()

    return render_template('reportentry.html', employees = employees, updatedemps=updatedemps, progress=progress)

@app.route('/reportform/<empid>', methods=['GET','POST'])
@login_required
def reportform(empid):
    if request.method == 'GET':   
        employee = Employee.query.get(int(empid))
        if employee:
            hasslip = False
            period = SalaryPeriod.query.filter_by(completed=False).first()
            slip = SalarySlip.query.filter_by(period_id = period.id, employee_id = employee.id).first()
            if slip:
                hasslip = True
                app.logger.info('gotslip %r', slip.id)
            hraval = period.hra
            if employee.scheme == 'State':
                daval = employee.basic_pay *period.da_state / 100.
            elif  employee.scheme == 'AICTE':
                daval = employee.basic_pay *period.da_aicte / 100.
            elif employee.scheme == 'QIP':
                daval = employee.basic_pay *period.da_qip / 100.
            elif employee.scheme == 'UGC':
                daval = employee.basic_pay *period.da_ugc / 100.


            return render_template('reportform.html', employee = employee, hraval=hraval, daval=daval, slip=slip, hasslip= hasslip)
        else:
            return 'No such employee'


@app.route('/monthreport')
def monthreport():
    period = SalaryPeriod.query.filter_by(completed=False).first()
    slips = SalarySlip.query.filter_by(period_id = period.id).all()
    return render_template('monthreport.html', slips = slips, period=period)



@app.route('/generate',methods=['GET','POST'])
@login_required
def generate():
    employees = Employee.query.all()
    empjson = []
    for i in employees:
        app.logger.info(i.__dict__)
        d = dict(i.__dict__)
        d.pop('_sa_instance_state')
        empjson.append(d)
        
    empjson = json.dumps(empjson)

    app.logger.info(empjson)   
    return render_template('generate.html', empjson=empjson)


@app.route('/test/<template>')
def test(template):
    return render_template(template+'.html')


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)
