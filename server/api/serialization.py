from flask_restx import fields, Model
from flask_marshmallow import Schema
from api.models import (
    User, User_Profile, Wallet, 
    Transaction, Beneficiary, 
    Category, WalletActivity
)

# Base configuration
api = Api(
    title='PayLink API',
    version='1.0',
    description='A digital wallet and payment system API',
    authorizations={
        'Bearer Auth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Type in the *Value* input box: Bearer {your JWT token}'
        }
    },
    security='Bearer Auth'
)

# Namespaces
ns = api.namespace('users', description='User operations')
auth = api.namespace('auth', description='Authentication operations')
wallet = api.namespace('wallet', description='Wallet operations')
transactions = api.namespace('transactions', description='Transaction operations')
beneficiaries = api.namespace('beneficiaries', description='Beneficiary operations')

# Schemas
class UserSchema(Schema):
    class Meta:
        model = User
        fields = ('id', 'user_name', 'public_id', 'is_admin', 'is_active', 'last_login')

class UserProfileSchema(Schema):
    class Meta:
        model = User_Profile
        fields = ('id', 'first_name', 'last_name', 'account_number', 
                 'phone_number', 'status', 'profile_picture', 'wallets')
    
    wallets = fields.Nested('WalletSchema', many=True)
    full_name = fields.String()

class WalletSchema(Schema):
    class Meta:
        model = Wallet
        fields = ('id', 'type', 'balance', 'account_number', 'status')

class TransactionSchema(Schema):
    class Meta:
        model = Transaction
        fields = ('id', 'transaction_id', 'amount', 'fee', 'status', 
                 'description', 'created_at', 'sender', 'receiver_account')
    
    sender = fields.Nested(UserProfileSchema, only=('id', 'full_name', 'account_number'))
    created_at = fields.DateTime(format='%Y-%m-%d %H:%M:%S')

class BeneficiarySchema(Schema):
    class Meta:
        model = Beneficiary
        fields = ('id', 'name', 'account_number', 'bank_code')

class CategorySchema(Schema):
    class Meta:
        model = Category
        fields = ('id', 'name', 'description')

class WalletActivitySchema(Schema):
    class Meta:
        model = WalletActivity
        fields = ('id', 'activity_type', 'amount', 'description', 
                 'created_at', 'wallet', 'transaction')
    
    wallet = fields.Nested(WalletSchema, only=('id', 'type', 'account_number'))
    transaction = fields.Nested(TransactionSchema, only=('id', 'transaction_id'))
    created_at = fields.DateTime(format='%Y-%m-%d %H:%M:%S')

# Instantiate schemas
User_Schema = UserSchema()
Users_Schema = UserSchema(many=True)
UserProfile_Schema = UserProfileSchema()
UserProfiles_Schema = UserProfileSchema(many=True)
wallet_Schema = WalletSchema()
wallets_Schema = WalletSchema(many=True)
transaction_Schema = TransactionSchema()
transactions_Schema = TransactionSchema(many=True)
Beneficiary_Schema = BeneficiarySchema()
Beneficiarys_Schema = BeneficiarySchema(many=True)
category_Schema = CategorySchema()
categories_Schema = CategorySchema(many=True)
wallet_activity_Schema = WalletActivitySchema()
wallet_activities_Schema = WalletActivitySchema(many=True)

# API Models for documentation
user_model_input = api.model('UserInput', {
    'user_name': fields.String(required=True),
    'password': fields.String(required=True),
    'confirm_password': fields.String(required=True),
    'first_name': fields.String(required=True),
    'last_name': fields.String(required=True),
    'phone_number': fields.String(required=True),
    'address': fields.String,
    'is_admin': fields.Boolean(default=False)
})

login_model = api.model('Login', {
    'user_name': fields.String(required=True),
    'password': fields.String(required=True)
})

create_wallet = api.model('CreateWallet', {
    'type': fields.String(required=True, enum=['Savings', 'Investment', 'Business']),
    'amount': fields.Float(required=True, min=0)
})

create_transaction = api.model('CreateTransaction', {
    'amount': fields.Float(required=True, min=0.01),
    'account_number': fields.String(required=True),
    'description': fields.String
})

beneficiary_model = api.model('Beneficiary', {
    'name': fields.String(required=True),
    'account_number': fields.String(required=True),
    'nickname': fields.String,
    'bank_code': fields.String
})