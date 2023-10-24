from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData,UniqueConstraint
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash,check_password_hash




metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)




class User(db.Model):
    __tablename__ ='users'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String)
    public_id = db.Column(db.String(50))
    _password = db.Column(db.String)
    roles =  db.Column(db.String)
    profile_picture = db.Column(db.String)
    joined = db.Column(db.DateTime, server_default=db.func.now())




  

    __table_args__ = (UniqueConstraint("public_id","user_name", name="User_unique_constraint"),)

    @hybrid_property
    def password_hash(self):
        return self._password
    
    @password_hash.setter
    def password_hash(self, password):
        self._password = generate_password_hash(password,method='pbkdf2:sha256')

    def authenticate(self,password):
        return True if check_password_hash(self._password, password) else False



    def __repr__(self):
        return f'(id: {self.id}, user_name: {self.user_name}, roles: {self.roles},  joined: {self.joined} )'


# Wallet Account (linked to Wallet model)
# Profile Details (linked to UserProfile model)
# Beneficiaries (many-to-many relationship with User for contacts)
# Transactions (one-to-many relationship with Transaction for user's transactions)


# Wallet:
# Fields:
# Wallet ID (auto-generated)
# User (foreign key to User)
# Balance


# UserProfile:
# Fields:
# Profile ID (auto-generated)
# User (foreign key to User)
# Full Name
# Address
# Phone Number
# Profile Picture (image upload)


# Beneficiary:
# Fields:
# Beneficiary ID (auto-generated)
# User (foreign key to User)
# Beneficiary User (foreign key to User for the contact)



# Transaction:
# Fields:
# Transaction ID (auto-generated)
# Sender (foreign key to User)
# Receiver (foreign key to User)
# Amount
# Date and Time
# Status (e.g., completed, pending)


# Admin:
# Fields:
# Admin ID (auto-generated)
# Username
# Password (hashed and salted)




# TransactionLog (for Admin):
# Fields:
# Log ID (auto-generated)
# Admin (foreign key to Admin)
# User (foreign key to User, nullable)
# Transaction (foreign key to Transaction)
# Action (e.g., create, read, update, delete)
# Date and Time



# AnalyticsData:
# Fields:
# Analytics ID (auto-generated)
# User (foreign key to User, nullable)
# Transaction (foreign key to Transaction, nullable)
# Profit (if applicable)
# Date and Time