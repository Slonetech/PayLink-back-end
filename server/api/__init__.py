import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import request ,make_response,jsonify
from flask_cors import CORS
from flask_bcrypt import Bcrypt



from flask_marshmallow import Marshmallow
from flask import session
from flask_session import Session
from api.config import ApplicationConfig



# from flask_restx import Api, Resource, fields

# create both app and api instances
app = Flask(__name__)
CORS(app, supports_credentials=True)
bcrypt = Bcrypt(app)

sess = Session()
ma = Marshmallow(app)




app.config['SESSION_TYPE'] = 'redis'
app.config['SECRET_KEY'] = 'redsfsfsfsfis'

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///paylink.db"

from api.models import db,User,User_Profile,Wallet,Transaction,Beneficiary,Category,WalletActivity,UserBeneficiary


migrate = Migrate(app, db)
app.config.from_object(ApplicationConfig)
sess.init_app(app)

db.init_app(app)
# from  api import routes
# with app.app_context():
#   db.create_all()