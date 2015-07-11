from app import app
from models import db, User, Employee, Premium
db.init_app(app)

with app.app_context():
    db.drop_all()
    db.create_all()
    db.session.commit()

with app.app_context():
 	user = User('admin','password')
 	emp1 = Employee('NSS1', 'Emp1', 'Male', 'Professor', 'CSE', 'AICTE',  'SBT', 
 		'4651621652651', '75165616', 'bharadhwaj10@gmail.com', '1234567989', 24152)
 	emp2 = Employee('NSS2','Emp2', 'Female', 'Professor', 'CE', 'UGC',  'SBI', 
 		'52030156301', '1653065', 'shafeeq94@gmail.com', '1234565589', 79456)
 	emp3 = Employee('NSS3',' Emp3', 'Male', 'Clerk', 'Office', 'State',  'SBT', 
 		'47777899', '645665616', '3@example.com', '9876543210', 12345)
 	db.session.add(emp1)
 	db.session.add(emp2)
 	db.session.add(emp3)
 	db.session.add(user)

 	premium1 = Premium(1, 'LIC', '12354LIC', 250000, 1000, 5,2025)
 	db.session.add(premium1)
 	
 	db.session.commit()
