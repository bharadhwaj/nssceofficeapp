from app import app
from models import db, User
db.init_app(app)

with app.app_context():
    db.drop_all()
    db.create_all()
    db.session.commit()

with app.app_context():
 	user = User('admin','password')
 	db.session.add(user)
 	db.session.commit()
