from app import app
from models import db, User, Employee, Disbursement, SalaryPeriod, SalarySlip
db.init_app(app)

with app.app_context():
    db.drop_all()
    db.create_all()
    db.session.commit()

with app.app_context():
 	user = User('admin','password')
 	emp1 = Employee('NSS1', 'Emp1', 'Male', 'Professor', 'CSE', 'AICTE',  'SBT', 
 		'4651621652651', '75165616', '1234567989', '1@example.com', 24152.26)
 	emp2 = Employee('NSS2','Emp2', 'Female', 'Professor', 'CE', 'UGC',  'SBI', 
 		'52030156301', '1653065',  '1234565589', '2@example.com',79456.00)
 	emp3 = Employee('NSS3',' Emp3', 'Male', 'Clerk', 'Office', 'State',  'SBT', 
 		'47777899', '645665616',  '9876543210', '3@example.com', 12345.97)
 	db.session.add(emp1)
 	db.session.add(emp2)
 	db.session.add(emp3)
 	db.session.add(user)
 	db.session.commit()
