from werkzeug import generate_password_hash
import datetime

from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    pwdhash = db.Column(db.String, nullable=False)
    registered_on = db.Column(db.DateTime)
    authenticated = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default = False)

    def __init__(self, username, password):
        self.username = username
        self.pwdhash = generate_password_hash(password)
        self.registered_on = datetime.datetime.utcnow()



    def is_active(self):
        return True

    def get_id(self):
        return self.id

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False

    def __repr__(self):
        return '<id: %r - email: %r>' %(self.id, self.email)

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
    basic_pay = db.Column(db.Integer)
    salaryslips = db.relationship('SalarySlip', backref='employee', lazy='dynamic')
    disbursements = db.relationship('Disbursement', backref='employee', lazy='dynamic')
    premiums = db.relationship('Premium', backref='employee', lazy='dynamic')


    def __init__(self,empid, name, gender, designation, department, scheme, bank_name, accno, pan_no, email, mobilenumber, basic_pay):
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

    def __repr__(self):
        return '<EMP id: %r - email: %r>' %(self.id, self.email)


class SalaryPeriod(db.Model):
    __tablename__ = "period"
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    spark_completed = db.Column(db.Boolean, default = False)
    disburse_completed = db.Column(db.Boolean, default = False)
    da_qip = db.Column(db.Float)
    da_state = db.Column(db.Float)
    da_ugc = db.Column(db.Float)
    da_aicte = db.Column(db.Float)
    hra = db.Column(db.Float)
    started_on = db.Column(db.DateTime)
    started_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    salaryslips = db.relationship('SalarySlip', backref='period', lazy='dynamic')
    disbursements = db.relationship('Disbursement', backref='period', lazy='dynamic')
    disbursement_others = db.Column(db.String)


    def __repr__(self):
        return '<Period year: %r - month: %r>' %(self.year, self.month)

    def __init__(self, year, month, hra, da_qip, da_state, da_ugc, da_aicte, userid):
        self.year = year
        self.month = month
        self.hra = hra
        self.da_qip = da_qip
        self.da_state = da_state
        self.da_ugc = da_ugc
        self.da_aicte = da_aicte
        self.started_by = userid
        self.started_on = datetime.datetime.utcnow()



class SalarySlip(db.Model):
    __tablename__ = "salaryslip"
    id  = db.Column(db.Integer, primary_key=True)
    period_id = db.Column(db.Integer, db.ForeignKey('period.id'))
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))

    basic_pay = db.Column(db.Float, default = 0)
    lwa = db.Column(db.Integer, default = 0)
    halfpay = db.Column(db.Integer, default = 0)
    agp = db.Column(db.Float, default = 0)
    da = db.Column(db.Float, default = 0)
    hra = db.Column(db.Float, default = 0)
    other = db.Column(db.Float, default = 0)
    gross = db.Column(db.Float, default = 0)

    #cuttings:

    pf = db.Column(db.Float, default = 0)
    pf_loan = db.Column(db.Float, default = 0)
    sli = db.Column(db.Float, default = 0)
    fbs = db.Column(db.Float, default = 0)
    gis = db.Column(db.Float, default = 0)
    income_tax = db.Column(db.Float, default = 0)
    gpis = db.Column(db.Float, default = 0)
    other2 = db.Column(db.Float, default = 0)
    total_deductions = db.Column(db.Float, default = 0)

    net_salary = db.Column(db.Float, default = 0)

    def __init__(self, period, emp, basic_pay, agp, da, hra, other,lwa, halfpay, pf, pf_loan, sli, fbs,
        gis, income_tax, gpis, other2):
        self.period_id = period
        self.employee_id = emp
        self.basic_pay = basic_pay
        self.agp = agp
        self.da = da
        self.hra = hra
        self.other = other
        self.lwa = lwa
        self.halfpay = halfpay

        #self.gross = self.basic_pay + self.agp + self.da + self.hra + self.other

        self.pf = pf
        self.pf_loan = pf_loan
        self.sli = sli
        self.fbs = fbs
        self.gis = gis
        self.income_tax = income_tax
        self.gpis = gpis
        self.other2 = other2

        # self.total_deductions = self.pf + self.pf_loan + self.sli + self.fbs + self.gis + self.income_tax + self.gpis + self.other2

        # self.net_salary = self.gross - self.total_deductions

    def __repr__(self):
        return 'Salaryslip:<emp-%d period-%d(%d/%d)>'%(self.employee_id, self.period_id, self.period.month, self.period.year)


class Disbursement(db.Model):
    __tablename__ = "disbursement"
    id  = db.Column(db.Integer, primary_key=True)
    period_id = db.Column(db.Integer, db.ForeignKey('period.id'))
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))

    premiums_cut = db.Column(db.Float, default = 0)
    telephone = db.Column(db.Float, default = 0)
    tenancy_rent = db.Column(db.Float, default = 0)
    cs_loan = db.Column(db.Float, default = 0)
    cs_chitty = db.Column(db.Float, default = 0)
    stamp = db.Column(db.Float, default = 0)
    send_off = db.Column(db.Float, default = 0)
    welfare_fund = db.Column(db.Float, default = 0)
    dte_jp = db.Column(db.Float, default = 0)
    jn = db.Column(db.Float, default = 0)
    indian_bank = db.Column(db.Float, default = 0)
    pdc_bank = db.Column(db.Float, default = 0)
    ksfe = db.Column(db.Float, default = 0)
    ksc_bank = db.Column(db.Float, default = 0)

    other1 = db.Column(db.Float, default = 0)
    other2 = db.Column(db.Float, default = 0)
    other3 = db.Column(db.Float, default = 0)

    net_salary = db.Column(db.Float)

    gross_salary = db.Column(db.Float) #net-payable in tables

    def __init__(self, period, empid, premiums_cut,
                 telephone, tenancy_rent, cs_chitty, cs_loan,
                 stamp, send_off, welfare_fund, dte_jp, jn, indian_bank,
                 pdc_bank, ksfe, ksc_bank, other3, other2, other1, net_salary):
        self.period_id = period
        self.employee_id = empid
        self.premiums_cut = premiums_cut
        
        self.telephone = telephone
        self.tenancy_rent = tenancy_rent
        self.cs_loan = cs_loan
        self.cs_chitty = cs_chitty
        self.stamp = stamp
        self.send_off = send_off
        self.welfare_fund = welfare_fund
        self.dte_jp = dte_jp
        self.jn = jn
        self.indian_bank = indian_bank
        self.pdc_bank = pdc_bank
        self.ksfe = ksfe
        self.ksc_bank = ksc_bank

        self.other1 = other1
        self.other2 = other2
        self.other3 = other3


        self.net_salary = net_salary

    def __repr__(self):
        return 'Disb:<emp-%d period-%d(%d/%d)>'%(self.employee_id, self.period_id, self.period.month, self.period.year)


class Premium(db.Model):
    __tablename__ = "premium"
    id = db.Column(db.Integer, primary_key = True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    name = db.Column(db.String, nullable=False)
    number = db.Column(db.String, nullable = False)
    monthly_amount = db.Column(db.Float)
    total_premium = db.Column(db.Float)
    date_updated = db.Column(db.DateTime)
    upto_month = db.Column(db.Integer)
    upto_year = db.Column(db.Integer)


    def __init__(self,employee_id, name, number, total_premium, monthly_amount, upto_month, upto_year):
        self.employee_id = employee_id
        self.name = name
        self.number = number
        self.total_premium = total_premium
        self.monthly_amount = monthly_amount
        self.upto_year = upto_year
        self.upto_month = upto_month
        self.date_updated = datetime.datetime.utcnow()

   