import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask import request ,make_response,jsonify
from flask_cors import CORS


from flask_marshmallow import Marshmallow




# from flask_restx import Api, Resource, fields

# create both app and api instances
app = Flask(__name__)
CORS(app)


ma = Marshmallow(app)




secret_key = app.config['SECRET_KEY'] = 'a16e4b678a12af3ac6df0b0d9b40db31'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///paylink.db"

from api.models import db,User,User_Profile,Wallet,Transaction,Beneficiary,Category,WalletActivity,UserBeneficiary


migrate = Migrate(app, db)
db.init_app(app)
# from  api import routes
