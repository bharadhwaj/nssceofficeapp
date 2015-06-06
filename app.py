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


@app.route('/',methods=['GET','POST'])
@login_required
def index():
	if request.method == 'POST':
		empid = request.form['empid']
		return redirect(url_for('editemp',empid=empid))
	return render_template('index.html')
    
@app.route('/employees')
@login_required
def employees():    
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
        else:
        	flash('Employee ID is invalid' , 'warning')
        	return redirect(url_for('index'))

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
        if SalaryPeriod.query.filter_by(spark_completed=False).first():
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
    period = SalaryPeriod.query.filter_by(spark_completed=False).first()
    if request.method == 'POST':
        empid = request.form['empid']
        employee = Employee.query.get(int(empid))
        basic_pay = float(request.form['basic_pay'])
        agp = float(request.form['agp'])
        da = float(request.form['da'])
        hra = float(request.form['hra'])
        other = float(request.form['other'])
        lwa = int(request.form['lwa'])
        halfpay = int(request.form['halfpay'])
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
            app.logger.info('Found existing slip: %r'%slip)
            slip.basic_pay = basic_pay
            slip.agp = agp
            slip.da = da
            slip.hra = hra
            slip.other = other
            slip.lwa = lwa
            slip.halfpay = halfpay
            slip.pf = pf
            slip.pfloan = pfloan
            slip.sli = sli
            slip.fbs = fbs
            slip.gis = gis
            slip.gpis = gpis
            slip.other2 = other2

            db.session.add(slip)
            db.session.commit()

        else:
            empslip = SalarySlip(period.id, employee.id, basic_pay, agp, da, hra, other, lwa, halfpay, 
            pf, pfloan, sli, fbs, gis, it, gpis, other2)

            db.session.add(empslip)
            db.session.commit()

    employees = Employee.query.all()
    updatedemps = [slip.employee.id for slip in SalarySlip.query.filter_by(period_id = period.id).all()]
    progress = (float(len(updatedemps)) / len(employees) )* 100

    app.logger.info('period %r, updatedemps %r' %(period, updatedemps))
    return render_template('reportentry.html', employees = employees, updatedemps=updatedemps, progress=progress)

@app.route('/reportform/<empid>', methods=['GET','POST'])
@login_required
def reportform(empid):
    if request.method == 'GET':   
        employee = Employee.query.get(int(empid))
        if employee:
            hasslip = False
            period = SalaryPeriod.query.filter_by(spark_completed=False).first()
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


@app.route('/verifyentries', methods=['GET', 'POST'])
def verifyentries():
    daysinmonth = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    period = SalaryPeriod.query.filter_by(spark_completed=False).first()
    slips = SalarySlip.query.filter_by(period_id = period.id).order_by(SalarySlip.employee_id).all()
    if request.method == 'POST':
        verified = request.form['verified']
        if verified:
            for slip in slips:
                original_basic_pay = slip.basic_pay
                app.logger.info(daysinmonth[period.month - 1])
                basicperday = float(slip.basic_pay) / daysinmonth[period.month - 1]
                daperday = float(slip.da) / daysinmonth[period.month - 1]
                agpperday = float(slip.agp) / daysinmonth[period.month - 1]
                hraperday = float(slip.hra) / daysinmonth[period.month - 1]
              
                slip.basic_pay -= slip.lwa * basicperday
                slip.agp -= slip.lwa * agpperday
                slip.da -= slip.lwa * daperday
                slip.hra -= slip.lwa * hraperday

                #Halfpay

                slip.basic_pay -= slip.halfpay * basicperday / 2
                if original_basic_pay > 18739:
                    slip.agp -= slip.halfpay * agpperday / 2
                    slip.da -= slip.halfpay * daperday / 2
                    slip.hra -= slip.halfpay * hraperday / 2

                slip.gross = slip.basic_pay + slip.agp + slip.da + slip.hra + slip.other
                slip.total_deductions = slip.pf + slip.pf_loan + slip.sli + slip.fbs + slip.gis + slip.income_tax + slip.gpis + slip.other2
                slip.net_salary = slip.gross - slip.total_deductions

                db.session.add(slip)
            db.session.commit()


    return render_template('verifyentries.html', slips = slips, period=period)



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
