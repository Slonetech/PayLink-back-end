from datetime import datetime
from api import db
from sqlalchemy import MetaData, UniqueConstraint, CheckConstraint
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import validates
from werkzeug.security import generate_password_hash, check_password_hash
import string
import random
import uuid

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
})

class BaseModel(db.Model):
    """Base model with common columns and methods"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def save(self):
        db.session.add(self)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def delete(self):
        db.session.delete(self)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

class User(BaseModel):
    __tablename__ = 'users'
    
    user_name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    public_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    profile = db.relationship('User_Profile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    
    __table_args__ = (
        UniqueConstraint('public_id', 'user_name', name='user_unique_constraint'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.public_id = str(uuid.uuid4())
        if 'password' in kwargs:
            self.set_password(kwargs['password'])

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.user_name}>'

class User_Profile(BaseModel):
    __tablename__ = 'users_profile'
    
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(200))
    phone_number = db.Column(db.String(20), nullable=False, index=True)
    account_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    profile_picture = db.Column(db.String(255), default='default_profile.jpg')
    status = db.Column(db.String(20), default='Active', nullable=False)
    gender = db.Column(db.String(10))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    
    user = db.relationship('User', back_populates='profile')
    wallets = db.relationship('Wallet', back_populates='user_profile', cascade='all, delete-orphan')
    transactions = db.relationship('Transaction', back_populates='user_profile', foreign_keys='Transaction.sender_id')
    wallet_activities = db.relationship('WalletActivity', back_populates='user_profile')
    
    # Beneficiary relationships
    beneficiaries_association = db.relationship('UserBeneficiary', back_populates='user', cascade='all, delete-orphan')
    beneficiaries = association_proxy('beneficiaries_association', 'beneficiary')

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __repr__(self):
        return f'<UserProfile {self.full_name}>'

class Wallet(BaseModel):
    __tablename__ = 'wallets'
    
    balance = db.Column(db.Numeric(10, 2), default=0.00, nullable=False)
    type = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='Active', nullable=False)
    account_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    user_prof_id = db.Column(db.Integer, db.ForeignKey('users_profile.id', ondelete='CASCADE'), nullable=False)
    
    user_profile = db.relationship('User_Profile', back_populates='wallets')
    activities = db.relationship('WalletActivity', back_populates='wallet')
    
    __table_args__ = (
        CheckConstraint('balance >= 0', name='non_negative_balance'),
    )

    def __repr__(self):
        return f'<Wallet {self.type} - {self.account_number}>'

class Transaction(BaseModel):
    __tablename__ = 'transactions'
    
    transaction_id = db.Column(db.String(20), unique=True, nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    fee = db.Column(db.Numeric(10, 2), default=0.00)
    status = db.Column(db.String(20), default='Pending', nullable=False)
    description = db.Column(db.String(255))
    sender_id = db.Column(db.Integer, db.ForeignKey('users_profile.id', ondelete='CASCADE'), nullable=False)
    receiver_account = db.Column(db.String(20), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'))
    
    user_profile = db.relationship('User_Profile', back_populates='transactions', foreign_keys=[sender_id])
    category = db.relationship('Category', back_populates='transactions')
    activities = db.relationship('WalletActivity', back_populates='transaction')
    
    __table_args__ = (
        CheckConstraint('amount > 0', name='positive_amount'),
    )

    @classmethod
    def calculate_fee(cls, amount):
        amount = float(amount)
        tiers = [
            (0, 5000, 0.0017),
            (5001, 15000, 0.002),
            (15001, 30000, 0.0024),
            (30001, 55000, 0.0026),
            (55001, 100000, 0.0029),
            (100001, None, 0.003)
        ]
        for min_amt, max_amt, rate in tiers:
            if max_amt is None and amount >= min_amt:
                return amount * rate
            elif min_amt <= amount <= max_amt:
                return amount * rate
        return 0

    @classmethod
    def generate_transaction_id(cls):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=14))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        if not self.fee and 'amount' in kwargs:
            self.fee = self.calculate_fee(kwargs['amount'])

    def __repr__(self):
        return f'<Transaction {self.transaction_id}>'

class WalletActivity(BaseModel):
    __tablename__ = 'wallet_activities'
    
    activity_type = db.Column(db.String(20), nullable=False)  # 'debit', 'credit', 'transfer', etc.
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    description = db.Column(db.String(255))
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users_profile.id', ondelete='CASCADE'), nullable=False)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id', ondelete='SET NULL'))
    
    wallet = db.relationship('Wallet', back_populates='activities')
    user_profile = db.relationship('User_Profile', back_populates='wallet_activities')
    transaction = db.relationship('Transaction', back_populates='activities')
    
    __table_args__ = (
        CheckConstraint('amount > 0', name='positive_activity_amount'),
    )

    def __repr__(self):
        return f'<WalletActivity {self.activity_type} - {self.amount}>'

class Category(BaseModel):
    __tablename__ = 'categories'
    
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    
    transactions = db.relationship('Transaction', back_populates='category')

    def __repr__(self):
        return f'<Category {self.name}>'

class Beneficiary(BaseModel):
    __tablename__ = 'beneficiaries'
    
    name = db.Column(db.String(100), nullable=False)
    account_number = db.Column(db.String(20), nullable=False, index=True)
    bank_code = db.Column(db.String(10))
    
    users_association = db.relationship('UserBeneficiary', back_populates='beneficiary', cascade='all, delete-orphan')
    users = association_proxy('users_association', 'user')

    def __repr__(self):
        return f'<Beneficiary {self.name} - {self.account_number}>'

class UserBeneficiary(BaseModel):
    __tablename__ = 'user_beneficiaries'
    
    sender_id = db.Column(db.Integer, db.ForeignKey('users_profile.id', ondelete='CASCADE'), primary_key=True)
    beneficiary_id = db.Column(db.Integer, db.ForeignKey('beneficiaries.id', ondelete='CASCADE'), primary_key=True)
    nickname = db.Column(db.String(50))
    
    user = db.relationship('User_Profile', back_populates='beneficiaries_association')
    beneficiary = db.relationship('Beneficiary', back_populates='users_association')

    def __repr__(self):
        return f'<UserBeneficiary {self.sender_id} -> {self.beneficiary_id}>'