from flask import Flask, request, render_template, url_for, redirect, flash, session, g, send_file, abort
from flask.ext.login import LoginManager
from flask.ext.login import login_user , logout_user , current_user , login_required
from werkzeug import generate_password_hash, check_password_hash
from flask.ext.seasurf import SeaSurf #for csrf protection
from flask_mail import Mail, Message
from flask import copy_current_request_context #for async mail
from flask import jsonify
from threading import Thread
from flask_weasyprint import HTML, render_pdf
from flask.ext.mandrill import Mandrill
from xhtml2pdf import pisa
from StringIO import StringIO
import os
import pytz
import json
import datetime
import pdfkit


from models import Employee, User, SalaryPeriod, SalarySlip, Disbursement, Premium
from models import db

app = Flask(__name__)
app.config.from_object('config')


db.init_app(app)
csrf = SeaSurf(app)
mail = Mail(app)

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
		name = request.form['name']
		if name == 'edit_employee':
			empid = request.form['empid']
			return redirect(url_for('editemp',empid=empid))
		if name == 'view_report':
			year = request.form['year']
			month = request.form['month']

			return redirect(url_for('generate',year=year, month=month))

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
        employee = Employee.query.filter_by(empid = empid).first()
        app.logger.info(employee)
        if request.form['formtype'] == "editemp":
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
            if not bpps:
                    bpps = str(00)
            bank = request.form['bank']
            pan = request.form['pan']
            email = request.form['email']
            mobilenumber = request.form['mobilenumber']
            bp = int(bprs)+(int(bpps)/100.0)
            

            employee.empid = empid
            employee.name = name
            employee.gender = gender
            employee.designation = designation
            employee.department = department
            employee.emptype = emptype
            employee.accno = accno
            employee.basic_pay = bp
            employee.bank_name = bank
            employee.pan_no = pan
            employee.mobilenumber = mobilenumber
            employee.email = email
            employee.mobilenumber = mobilenumber

            db.session.commit()
        elif request.form['formtype'] == 'addpremium':
            premium_name = request.form['name']
            premium_number = request.form['number']
            premium_total_amount = request.form['total']
            premium_monthly_amount = request.form['monthly']
            premium_upto_month = request.form['upto_month']
            premium_upto_year = request.form['upto_year']

            new_premium = Premium(employee.id, premium_name, premium_number,
                premium_total_amount, premium_monthly_amount, premium_upto_month, premium_upto_year)
            db.session.add(new_premium)
            db.session.commit()
        elif request.form['formtype'] == 'delpremium':
            premium_id = request.form['pid']
            premium = Premium.query.get(int(premium_id))
            db.session.delete(premium)
            db.session.commit()

        return render_template('editemp.html', emp = employee, str=str)

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
    	    newuser = Employee(empid,name,gender,designation,department, emptype,bank,accno,pan,email,mobilenumber,bp)
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
        elif SalaryPeriod.query.filter_by(disburse_completed = False).first():
            return redirect(url_for('disbursementinput'))
        else:
            return render_template('newperiod.html')

    if request.method == 'POST':
        app.logger.info(repr(request.form))
        year = int(request.form['year'])
        month = int(request.form['month'])

        prev = SalaryPeriod.query.filter_by(year = int(year), month=int(month)).first()
        if prev:
            flash('Report already generated for that month','warning')
            return render_template('newperiod.html')

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
    if request.method == 'GET':
        return render_template('verifyentries.html',slips = slips, period=period)
    
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
            period.spark_completed = True;
            db.session.add(period)
            db.session.commit()
            return redirect(url_for('disbursementinput'))


@app.route('/disbursementinput', methods=['GET','POST'])
@login_required
def disbursementinput():
    period = SalaryPeriod.query.filter_by(disburse_completed=False).first()
    if request.method == 'POST':
        app.logger.info(sorted(request.form))
        empid = request.form['empid']
        employee = Employee.query.get(int(empid))


        premiums_cut = request.form['premiums_cut']
        telephone = request.form['telephone']
        tenancy_rent = request.form['tenancy_rent']
        cs_loan = request.form['cs_loan']
        cs_chitty = request.form['cs_chitty']
        stamp = request.form['stamp']
        send_off = request.form['send_off']
        welfare_fund = request.form['welfare_fund']
        dte_jp = request.form['dte_jp']
        jn = request.form['jn']
        indian_bank = request.form['indian_bank']
        pdc_bank = request.form['pdc_bank']
        ksfe = request.form['ksfe']
        ksc_bank = request.form['ksc_bank']

        other1 = request.form['other1']
        other2 = request.form['other2']
        other3 = request.form['other3']
       
        app.logger.info('All fields okay')

        if request.form['hasslip'] == 'True':
            slip = Disbursement.query.filter_by(employee_id = int(empid), period_id = period.id).first()
            app.logger.info('Found existing slip: %r'%slip)
            slip.premiums_cut = premiums_cut


            slip.telephone = telephone
            slip.tenancy_rent = tenancy_rent
            slip.cs_loan = cs_loan
            slip.cs_chitty = cs_chitty
            slip.stamp = stamp
            slip.send_off = send_off
            slip.welfare_fund = welfare_fund
            slip.dte_jp = dte_jp
            slip.jn = jn
            slip.indian_bank = indian_bank
            slip.pdc_bank = pdc_bank
            slip.ksfe = ksfe
            slip.ksc_bank = ksc_bank

            slip.other1 = other1
            slip.other2 = other2
            slip.other3 = other3
           

            db.session.add(slip)
            db.session.commit()

        else:
            sparkslip = SalarySlip.query.filter_by(period_id=period.id, employee_id=employee.id).first()
            empslip = Disbursement(period.id, employee.id, premiums_cut,
                                     telephone, tenancy_rent, cs_chitty, cs_loan,
                                     stamp, send_off, welfare_fund, dte_jp, jn, indian_bank,
                                     pdc_bank, ksfe, ksc_bank, other3, other2, other1, sparkslip.net_salary)
            
            empslip.premiums_cut = 0
            premiums = employee.premiums.filter(Premium.upto_year >= period.year).all()
            for premium in premiums:
                if premium.upto_year == period.year:
                    if premium.upto_month >= period.month:
                        empslip.premiums_cut += premium.monthly_amount
                else:
                        empslip.premiums_cut += premium.monthly_amount
            db.session.add(empslip)
            db.session.commit()

    employees = Employee.query.all()
    updatedemps = [slip.employee.id for slip in Disbursement.query.filter_by(period_id = period.id).all()]
    progress = (float(len(updatedemps)) / len(employees) )* 100

    app.logger.info('period %r, updatedemps %r' %(period, updatedemps))
    return render_template('disbursementinput.html', employees = employees, updatedemps=updatedemps, progress=progress)

   

@app.route('/disbursementform/<empid>', methods=['GET','POST'])
@login_required
def disbursementform(empid):
    if request.method == 'GET':   
        employee = Employee.query.get(int(empid))
        if employee:
            hasslip = False
            period = SalaryPeriod.query.filter_by(disburse_completed=False).first()
            slip = Disbursement.query.filter_by(period_id = period.id, employee_id = employee.id).first()
            if slip:
                hasslip = True
                app.logger.info('gotslip %r', slip.id)
    
            return render_template('disbursementform.html', employee = employee, slip=slip, hasslip= hasslip)
        else:
            return 'No such employee'

@app.route('/verifydisbursals', methods=['GET', 'POST'])
def verifydisbursals():
    period = SalaryPeriod.query.filter_by(disburse_completed=False).first()
    slips = Disbursement.query.filter_by(period_id = period.id).order_by(Disbursement.employee_id).all()
    if request.method == 'GET':
        return render_template('verifydisbursals.html',slips = slips, period=period)
    
    if request.method == 'POST':
        verified = request.form['verified']
        if verified:
            for slip in slips:
                slip.gross_salary = slip.net_salary - (slip.premiums_cut \
                                                    + slip.telephone \
                                                    + slip.tenancy_rent \
                                                    + slip.cs_loan \
                                                    + slip.cs_chitty \
                                                    + slip.stamp \
                                                    + slip.send_off \
                                                    + slip.welfare_fund \
                                                    + slip.dte_jp \
                                                    + slip.jn \
                                                    + slip.indian_bank \
                                                    + slip.pdc_bank \
                                                    + slip.ksfe \
                                                    + slip.ksc_bank \
                                                    + slip.other1
                                                    + slip.other2 \
                                                    + slip.other3)

                db.session.add(slip)

            period.disburse_completed = True;
            db.session.add(period)
            db.session.commit()
            return redirect(url_for('generate', year = period.year, month = period.month))


@app.route('/generate/<year>/<month>',methods=['GET','POST'])
@login_required
def generate(year,month):
    if request.method == 'GET':
        period = SalaryPeriod.query.filter_by(year = year, month=month).first()
        if period:
            app.logger.info('Got period')
            sortby = request.args.get('sortby')
            app.logger.info(repr(request.args.get))
            if not sortby:
                slips = SalarySlip.query.filter_by(period_id=period.id).order_by(SalarySlip.employee_id)
                disbs = Disbursement.query.filter_by(period_id=period.id).order_by(Disbursement.employee_id)
                data = zip(slips,disbs)
                return render_template('viewall.html', data=data, period=period, banks = app.config['BANK_TYPES'])

            else:
                app.logger.info('Sorting by: '+sortby)

                if sortby == 'bank': 
                    bank = request.args.get('bank')
                    app.logger.info(repr(request.args.get))
                    if bank:
                        app.logger.info('Got bank')
                        app.logger.info('Sorting by bank: ' + bank)
                        employees = Employee.query.filter_by(bank_name = str(bank)).all()
                        slips  = []
                        disbs  = []
                        for e in employees:
                            slips.append(e.salaryslips.filter_by(period_id = period.id).first())
                            disbs.append(e.disbursements.filter_by(period_id = period.id).first())
                        app.logger.info(slips)
                        app.logger.info(disbs)
                        data = zip(slips,disbs)

                        bank_name = bank
                        bank_total = sum([d.gross_salary for d in disbs])
                        return render_template('viewall-bank.html',data=data, 
                            period=period, banks = app.config['BANK_TYPES'],
                            bank_name = bank_name, bank_total = bank_total)
                elif sortby == 'scheme':
                    scheme = request.args.get('scheme' )
                    app.logger.info('Sorting by scheme: ' + scheme)
                    if scheme:
                        app.logger.info('Sorting by scheme: ' + scheme)
                        employees = Employee.query.filter_by(scheme = scheme).all()
                        slips  = []
                        disbs  = []
                        for e in employees:
                            slips.append(e.salaryslips.filter_by(period_id = period.id).first())
                            disbs.append(e.disbursements.filter_by(period_id = period.id).first())
                        app.logger.info(slips)
                        app.logger.info(disbs)
                        data = zip(slips,disbs)
                        
                        return render_template('viewall.html',data=data, period=period, banks = app.config['BANK_TYPES'])

            #return 'ok'
        else:
            flash('Report not generated for this month','warning')
            return render_template('index.html')

    elif request.method == 'POST':
        name = request.form['name']
        if name == 'personal':
            period = SalaryPeriod.query.filter_by(year = year, month=month).first()
            slips = SalarySlip.query.filter_by(period_id=period.id).order_by(SalarySlip.employee_id)
            employees = [] # since we cannot access slip.employee in thread2 due to db session issues
            for s in slips:
                employees.append(s.employee)
            disbs = Disbursement.query.filter_by(period_id=period.id).order_by(Disbursement.employee_id)
            data = zip(slips, disbs, employees)
            generate_salary_slips(data, period)
        else:
            period = SalaryPeriod.query.filter_by(year = year, month=month).first()
            employees = Employee.query.filter_by(bank_name = name).all()
            disbs = Disbursement.query.filter_by(period_id=period.id).order_by(Disbursement.employee_id)
            
            data = zip(disbs, employees)
            app.logger.info(employees)
            app.logger.info(disbs)
            bank_total = sum([d.gross_salary for d in disbs])
            generate_bank_slips(data, period, name, bank_total)

            # employee = Employee.query.all()
            # app.logger.info('Queried all employees')
            # for emp in employee:
            #     send_email("Pay Slip",
            #         'TIM',
            #         [emp.email],
            #         'Check in attachments',
            #         render_template('employeereport.html',employee = emp, data = dataglobal)
            #         )
            #     app.logger.info('Mail sent')

        return redirect(url_for('index'))


def async(f):
    def wrapper(*args, **kwargs):
        thr = Thread(target = f, args = args, kwargs = kwargs)
        thr.start()
    return wrapper


@async
def send_async_email(subject,sender,recipients,text_body,attachment,filename):
    with app.app_context():
        subject = subject
        msg = Message(subject, sender = sender, recipients = recipients)
        msg.body = text_body
        msg.attach(filename, "application/pdf", open(attachment,'rb').read())
        mail.send(msg)
    app.logger.info('Sent email')

def send_email(subject, sender, recipients, text_body, attachments):
    send_async_email(subject,sender,recipients,text_body, attachments)


@async
def generate_salary_slips(data, period):
    with app.app_context():        
        dirpath = 'slips/%d/%d/' %(period.year,period.month)
        if not os.path.isdir(dirpath):
            try:
                os.makedirs(dirpath)
            except:
                app.logger.info("Couldn't create directory")
                return "Couldn't create directory"

        app.logger.info('Making dir successful')
        css = ['static/css/bootstrap.css']
        for slip,disb,employee in data:
            slip_html = render_template('employeereport.html', slip=slip, disb =disb, employee=employee, year=period.year, month = period.month, int=int)
            pdfkit.from_string(slip_html, dirpath+str(employee.empid)+'.pdf', css = css)
            app.logger.info('Made pdf for employee %r' %employee.empid)
            subject = "Pay Slip for "+str(period.month)+'/' + str(period.year)
            filename = employee.name + ' - '+str(period.month)+'/'+ str(period.year)+'.pdf'
            body = 'Hi '+employee.name+', \n We have attached your salary slip of '+ ' - '+str(period.month)+'/'+ str(period.year)+'\n Please find it in attachments. \n Thank you.'
            send_async_email(subject, 'TIM', [employee.email], body, dirpath+str(employee.empid)+'.pdf',filename)
                    
@async
def generate_bank_slips(data, period, bank_name, bank_total):
    with app.app_context():        
        dirpath = 'slips/%d/%s/' %(period.year,bank_name)
        if not os.path.isdir(dirpath):
            try:
                os.makedirs(dirpath)
            except:
                app.logger.info("Couldn't create directory")
                return "Couldn't create directory"
        admin = ['bharadhwaj10@gmail.com','shafeeq94@gmail.com']
        app.logger.info('Making dir successful')
        css = ['static/css/bootstrap.css','static/css/reports.css','static/css/bootswatch.css','static/css/styles.css']
        bank_slip_html = render_template('bankreport.html',data=data, period=period, bank_name = bank_name, bank_total = bank_total)
        pdfkit.from_string(bank_slip_html, dirpath+bank_name+'-'+str(period.month)+'-'+str(period.year)+ '.pdf', css = css)
        app.logger.info('Made pdf for Bank %r' %bank_name)
        subject = bank_name + " Bank Slip for "+str(period.month)+'/'+str(period.year)
        filename = bank_name + ' - '+str(period.month)+'/'+str(period.year)+'.pdf'
        body = 'Hi, \n We have attached the '+ bank_name +'\'s bank slip of '+ ' - '+str(period.month)+'/'+ str(period.year)+'\n Please find it in attachments. \n Thank you.'
        send_async_email(subject, 'TIM', admin, body, dirpath+bank_name+'.pdf',filename)


@app.route('/test/<template>')
def test(template):
    return render_template(template+'.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000)
