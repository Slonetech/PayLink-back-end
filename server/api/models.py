from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData,UniqueConstraint
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash,check_password_hash

import string, random
import uuid



metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)




class User(db.Model):
    __tablename__ ='users'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String)
    public_id = db.Column(db.String(50))
    password = db.Column(db.String)
    is_admin =  db.Column(db.Integer)
    # email = db.Column(db.String)
    joined = db.Column(db.DateTime, server_default=db.func.now())




  

    __table_args__ = (UniqueConstraint("public_id","user_name", name="User_unique_constraint"),)




    def __repr__(self):
        return f'(id: {self.id}, user_name: {self.user_name}, is_admin: {self.is_admin},  joined: {self.joined} )'






class User_Profile(db.Model):
    __tablename__ ='users_profile'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    address=db.Column(db.String)
    phone_number=db.Column(db.Integer)
    Account=db.Column(db.Integer)
    profile_pictur= db.Column(db.String)
    status = db.Column(db.String)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref='users_profile',uselist=False,single_parent=True)

    wallet = db.relationship('Wallet', backref='user_profile', lazy=True)

    transactions = db.relationship('Transaction', backref='user_profile', lazy=True)
    wallet_ctivities = db.relationship('WalletActivity', backref='user_profile', lazy=True)

    

    # beneficiary relationship
    user_beneficiary_association = db.relationship('UserBeneficiary', back_populates='user')
    beneficiaries = association_proxy('user_beneficiary_association','beneficiary')

    def full_name(self):
        full_name = self.first_name + ' ' + self.last_name
        return full_name
 

    def __repr__(self):
        return f'(id: {self.id}, first_name: {self.first_name},last_name: {self.last_name}, address: {self.address},  phone: {self.phone_number}, wallets={self.wallet},status: {self.status} )'





class UserBeneficiary(db.Model):
    __tablename__='user_beneficiaries'  
    
    
    id = db.Column(db.Integer, primary_key=True)    
    sender_id = db.Column('sender_id',db.Integer, db.ForeignKey("users_profile.id"))
    beneficiary_id = db.Column('beneficiary_id',db.Integer, db.ForeignKey("beneficiaries.id"))

    user = db.relationship('User_Profile', back_populates='user_beneficiary_association')
    beneficiary = db.relationship('Beneficiary', back_populates='user_beneficiary_association')

    def save(self):
        db.session.add(self)
        db.session.commit()

    # def __repr__(self):
    #     return f'(id: {self.id}, sender_id: {self.sender_id},beneficiary_id: {self.beneficiary_id} )'






class Beneficiary(db.Model):
    __tablename__ ='beneficiaries'
    pass

    id = db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String)
    Account=db.Column(db.String)




    # # beneficiary relationship
    user_beneficiary_association = db.relationship('UserBeneficiary', back_populates='beneficiary')
    users = association_proxy('user_beneficiary_association','user')

    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f'(id: {self.id}, name: {self.name}, Account: {self.Account}  )'





class Transaction(db.Model):
    __tablename__ ='transactions'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id =db.Column(db.String)
    sender_name =db.Column(db.String)
    receiver_name =db.Column(db.String)
    transaction_fee =  db.Column(db.Numeric(10,2))
    amount=db.Column(db.Integer)
    receiver_account=db.Column(db.Integer)
    created = db.Column(db.DateTime, server_default=db.func.now())
    sender_id = db.Column(db.Integer, db.ForeignKey('users_profile.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    #*******************relationships********************************
    wallet_ctivities = db.relationship('WalletActivity', backref='transaction', lazy=True)    
    category = db.relationship('Category', backref='transaction',uselist=False)

    #!-----------------------------------------------------------------------
    def save(self):
        db.session.add(self)
        db.session.commit()
    #!-----------------------------------------------------------------------
    
    @classmethod
    def transaction_fees(cls,amount):
        amount = int(amount)
        deductionA = 0.0017
        deductionB = 0.002
        deductionC = 0.0024
        deductionD = 0.0026
        deductionE = 0.0029
        deductionF = 0.003

        deduction = 0
        if 0 <= amount <= 5000:
            deduction = amount * deductionA
        elif 5001 <= amount <= 15000:
            deduction = amount * deductionB
        elif 15001 <= amount <= 30000:
            deduction = amount * deductionC
        elif 30001 <= amount <= 55000:
            deduction = amount * deductionD
        elif 55001 <= amount <= 100000:
            deduction = amount * deductionE
        else:
            deduction = amount * deductionF

        return deduction

    #!-----------------------------------------------------------------------
    
    @classmethod
    def generate_unique_id(cls):
        length = 14
        characters = string.ascii_uppercase + string.digits
        unique_id = ''.join(random.choice(characters) for _ in range(length))
        return unique_id
    
    def __repr__(self):
        return f'(id: {self.id}, transaction_id:{self.transaction_id} amount: {self.amount},sender_id: {self.sender_id} ,receiver_account: {self.receiver_account}, receiver_name: {self.receiver_name},sender_name: {self.sender_name}, category:{self.category.type} )'



class WalletActivity(db.Model):
    __tablename__ ='wallet_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_type = db.Column(db.String(50))  # E.g., 'sent', 'received', 'top-up'
    amount = db.Column(db.Float)
    description = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user_id = db.Column(db.Integer, db.ForeignKey('users_profile.id'), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)


class Category(db.Model):
    __tablename__ ='categories'

    id = db.Column(db.Integer, primary_key=True)
    type=db.Column(db.String)



class Wallet(db.Model):
    __tablename__ ='wallets'

    id = db.Column(db.Integer, primary_key=True)   
    balance =  db.Column(db.Numeric(10,2))
    type=db.Column(db.String)
    status=db.Column(db.String)
    Account=db.Column(db.String)
    

    joined = db.Column(db.DateTime, server_default=db.func.now())


    user_prof_id = db.Column(db.Integer, db.ForeignKey('users_profile.id'))
    # user_profile = db.relationship('User_Profile', back_populates='wallet', )

 



    def save(self):
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return f'(id: {self.id}, balance: {self.balance},user_id: {self.user_prof_id}, type: {self.type}  )'





