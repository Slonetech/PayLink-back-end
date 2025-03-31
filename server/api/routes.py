from flask import request, make_response
from flask_jwt_extended import (
    jwt_required, 
    create_access_token, 
    create_refresh_token, 
    get_jwt_identity,
    current_user
)
from werkzeug.exceptions import BadRequest, NotFound, Unauthorized, Conflict
from decimal import Decimal
import random
import string
from datetime import timedelta

from api import app, db, bcrypt
from api.models import (
    User, User_Profile, Wallet, Transaction, 
    Beneficiary, Category, WalletActivity, UserBeneficiary
)
from api.serialization import (
    UserProfile_Schema, UserProfile_Schema,
    wallet_Schema, wallets_Schema,
    transaction_Schema, transactions_Schema,
    Beneficiary_Schema, Beneficiarys_Schema,
    api, ns, auth, wallet, transactions, beneficiaries
)

# Helper functions
def generate_account_number():
    return ''.join(random.choices(string.digits, k=14))

def validate_phone_number(phone):
    # Add proper phone number validation
    return phone

# Auth Routes
@auth.route('/signup')
class Signup(Resource):
    @auth.expect(user_model_input)
    def post(self):
        data = request.get_json()
        
        # Validate input
        if not all(k in data for k in ['user_name', 'password', 'confirm_password', 
                                      'first_name', 'last_name', 'phone_number']):
            raise BadRequest('Missing required fields')
        
        if data['password'] != data['confirm_password']:
            raise BadRequest('Passwords do not match')
        
        if User.query.filter_by(user_name=data['user_name']).first():
            raise Conflict('Username already exists')
        
        # Create user
        user = User(
            user_name=data['user_name'],
            password=data['password'],
            is_admin=data.get('is_admin', False)
        )
        
        # Create profile
        profile = User_Profile(
            first_name=data['first_name'],
            last_name=data['last_name'],
            phone_number=validate_phone_number(data['phone_number']),
            address=data.get('address', ''),
            account_number=generate_account_number(),
            user=user
        )
        
        # Create main wallet
        wallet = Wallet(
            balance=Decimal('50000.00'),  # Starting balance
            type='Main',
            account_number=profile.account_number,
            user_profile=profile
        )
        
        db.session.add_all([user, profile, wallet])
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise BadRequest('Failed to create account')
        
        return {
            'message': 'Account created successfully',
            'user_id': user.id,
            'account_number': profile.account_number
        }, 201

@auth.route('/login')
class Login(Resource):
    @auth.expect(login_model)
    def post(self):
        data = request.get_json()
        user_name = data.get('user_name')
        password = data.get('password')
        
        if not user_name or not password:
            raise BadRequest('Username and password are required')
        
        user = User.query.filter_by(user_name=user_name).first()
        if not user or not user.check_password(password):
            raise Unauthorized('Invalid credentials')
        
        if not user.is_active:
            raise Unauthorized('Account is deactivated')
        
        # Create tokens
        access_token = create_access_token(
            identity=user.profile.id,
            expires_delta=timedelta(minutes=30)
        )
        refresh_token = create_refresh_token(
            identity=user.profile.id,
            expires_delta=timedelta(days=7)
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user_id': user.profile.id,
            'user_name': user.user_name,
            'is_admin': user.is_admin,
            'account_number': user.profile.account_number
        }, 200

@auth.route('/refresh')
class Refresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        identity = get_jwt_identity()
        new_token = create_access_token(identity=identity)
        return {'access_token': new_token}, 200

# User Routes
@ns.route('/user')
class UserProfile(Resource):
    @jwt_required()
    def get(self):
        return UserProfile_Schema.dump(current_user), 200

# Wallet Routes
@wallet.route('/wallets')
class UserWallets(Resource):
    @jwt_required()
    def get(self):
        wallets = current_user.wallets
        return wallets_Schema.dump(wallets), 200

    @jwt_required()
    @wallet.expect(create_wallet)
    def post(self):
        data = request.get_json()
        wallet_type = data.get('type')
        amount = Decimal(data.get('amount', 0))
        
        if not wallet_type:
            raise BadRequest('Wallet type is required')
        
        # Check if wallet type already exists
        if any(w.type == wallet_type for w in current_user.wallets):
            raise Conflict(f'You already have a {wallet_type} wallet')
        
        # Get main wallet
        main_wallet = next((w for w in current_user.wallets if w.type == 'Main'), None)
        if not main_wallet:
            raise NotFound('Main wallet not found')
        
        # Check balance
        if amount > main_wallet.balance:
            raise BadRequest('Insufficient funds in main wallet')
        
        # Deduct from main wallet
        main_wallet.balance -= amount
        
        # Create new wallet
        new_wallet = Wallet(
            type=wallet_type,
            balance=amount,
            account_number=generate_account_number(),
            user_profile=current_user
        )
        
        db.session.add(new_wallet)
        db.session.commit()
        
        return wallet_Schema.dump(new_wallet), 201

# Transaction Routes
@transactions.route('/transactions')
class Transactions(Resource):
    @jwt_required()
    def get(self):
        transactions = current_user.transactions
        return transactions_Schema.dump(transactions), 200

    @jwt_required()
    @transactions.expect(create_transaction)
    def post(self):
        data = request.get_json()
        amount = Decimal(data.get('amount', 0))
        account_number = data.get('account_number')
        description = data.get('description', '')
        
        if not all([amount, account_number]):
            raise BadRequest('Amount and account number are required')
        
        if amount <= 0:
            raise BadRequest('Amount must be positive')
        
        # Get sender's main wallet
        sender_wallet = next((w for w in current_user.wallets if w.type == 'Main'), None)
        if not sender_wallet:
            raise NotFound('Main wallet not found')
        
        # Check if sending to self
        if account_number == sender_wallet.account_number:
            raise BadRequest('Cannot send to yourself')
        
        # Check balance
        if amount > sender_wallet.balance:
            raise BadRequest('Insufficient funds')
        
        # Find receiver
        receiver_profile = User_Profile.query.filter_by(account_number=account_number).first()
        if not receiver_profile:
            raise NotFound('Receiver account not found')
        
        receiver_wallet = next((w for w in receiver_profile.wallets if w.type == 'Main'), None)
        if not receiver_wallet:
            raise NotFound('Receiver main wallet not found')
        
        # Calculate fee
        fee = Transaction.calculate_fee(amount)
        total_debit = amount + fee
        
        # Check balance again with fee
        if total_debit > sender_wallet.balance:
            raise BadRequest(f'Insufficient funds including fee. Total required: {total_debit}')
        
        # Create transaction
        transaction = Transaction(
            amount=amount,
            fee=fee,
            sender_id=current_user.id,
            receiver_account=account_number,
            description=description
        )
        
        # Update balances
        sender_wallet.balance -= total_debit
        receiver_wallet.balance += amount
        
        # Create wallet activities
        sender_activity = WalletActivity(
            activity_type='debit',
            amount=total_debit,
            description=f'Transfer to {receiver_profile.full_name}',
            wallet=sender_wallet,
            user_profile=current_user,
            transaction=transaction
        )
        
        receiver_activity = WalletActivity(
            activity_type='credit',
            amount=amount,
            description=f'Transfer from {current_user.full_name}',
            wallet=receiver_wallet,
            user_profile=receiver_profile,
            transaction=transaction
        )
        
        db.session.add_all([transaction, sender_activity, receiver_activity])
        db.session.commit()
        
        return transaction_Schema.dump(transaction), 201

# Beneficiary Routes
@beneficiaries.route('/beneficiaries')
class Beneficiaries(Resource):
    @jwt_required()
    def get(self):
        return Beneficiarys_Schema.dump(current_user.beneficiaries), 200

    @jwt_required()
    @beneficiaries.expect(Beneficiary_Schema)
    def post(self):
        data = request.get_json()
        account_number = data.get('account_number')
        name = data.get('name')
        
        if not all([account_number, name]):
            raise BadRequest('Account number and name are required')
        
        # Check if already a beneficiary
        if any(b.account_number == account_number for b in current_user.beneficiaries):
            raise Conflict('This account is already in your beneficiaries')
        
        # Find or create beneficiary
        beneficiary = Beneficiary.query.filter_by(account_number=account_number).first()
        if not beneficiary:
            beneficiary = Beneficiary(
                name=name,
                account_number=account_number
            )
        
        # Create association
        user_beneficiary = UserBeneficiary(
            user=current_user,
            beneficiary=beneficiary,
            nickname=data.get('nickname')
        )
        
        db.session.add(user_beneficiary)
        db.session.commit()
        
        return Beneficiary_Schema.dump(beneficiary), 201