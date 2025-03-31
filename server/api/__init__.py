import os
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_marshmallow import Marshmallow
from flask_session import Session
from werkzeug.exceptions import HTTPException
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create app instance
app = Flask(__name__)

# Configuration
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'mysecret'),
    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URI', 'sqlite:///paylink.db'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SESSION_TYPE='sqlalchemy',
    SESSION_SQLALCHEMY=db,
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY', 'super-secret'),
)

# Initialize extensions
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
ma = Marshmallow(app)
sess = Session(app)
CORS(app, resources={
    r"/*": {
        "origins": os.getenv('ALLOWED_ORIGINS', 'http://localhost:5173').split(','),
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Error handling
@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({
        "error": e.name,
        "message": e.description,
    }), e.code

# Import models and routes after app creation to avoid circular imports
from api.models import User, User_Profile, Wallet, Transaction, Beneficiary, Category, WalletActivity, UserBeneficiary
from api import routes
from api.serialization import api

# Initialize API
api.init_app(app)

if __name__ == '__main__':
    app.run(debug=os.getenv('FLASK_DEBUG', 'true').lower() == 'true', port=5555)