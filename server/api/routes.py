from api import  make_response,jsonify,User_Profile,User,UserBeneficiary,Beneficiary,Wallet,Transaction,app,db,request
from api import  make_response,jsonify,Category,app,db,request
from api.serialization import api,ns,auth,Resource
from api.serialization import UserProfiles_Schema,UserProfile_Schema
from api.serialization import wallets_Schema
from api.serialization import transactions_Schema,create_transaction
# from api.serialization import user_schema,ns,auth,Resource,user_model_input,login_input_model,vendor_model_update
# from api.serialization import vendor_model_input,post_user
import uuid

from faker import Faker
import random 
from random import randint, choice as rc
fake = Faker()

import jwt
from functools import wraps

from flask_jwt_extended import JWTManager,jwt_required
from flask_jwt_extended import create_refresh_token,create_access_token, get_jwt_identity
# from flask_jwt_extended import get_jwt_claims

jwt = JWTManager(app)






@ns.route('/users')
class UserProfiles(Resource):
    def get(self):
        all_users = User_Profile.query.all()

        if not all_users:
            return make_response(jsonify({"message":"no Users found"}))
        
        # get each user's beneficiaries or the receivers
        beneficiaries_list=[user.beneficiaries for user in all_users  if len(user.beneficiaries) > 0]
        receiver_list =[]
        # loop thru the nested list
        for benef in beneficiaries_list:
            # loop thru the tupple (id: 6, user_profile_id: 3 )
            for b in benef:
                receiver_list.append(b.user_profile_id)

        # loop thru the list of beneficiary id's and get their user information
        receiver_object_list =[]
        for receiver_id in receiver_list:
            receiver=User_Profile.query.filter_by(id = receiver_id).first()
            receiver_object_list.append(receiver)
        print(receiver_object_list)
                
        
        return make_response(UserProfiles_Schema.dump(all_users),200)



'''_____________W   A   L  L  E  T ____________________________'''
@ns.route('/wallet')
class Wallets(Resource):
    def get(self):
        all_wallets = Wallet.query.all()

        if not all_wallets:
            return make_response(jsonify({"message":"no beneficiaries found"}))
        
        return make_response(wallets_Schema.dump(all_wallets),200)
    
 


'''_____________T R A N S A C T I O N S____________________________'''
@ns.route('/transactions')
class Transactions(Resource):
    def get(self):
        all_transactions = Transaction.query.all()

        if not all_transactions:
            return make_response(jsonify({"message":"no beneficiaries found"}))
        
        return make_response(transactions_Schema.dump(all_transactions),200)
    
    #_______C R E A T E _____________-T R A N S A C T I O N S_________________
    @ns.expect(create_transaction)
    def post(self):
        data = request.get_json()
        print(data)
        #-------------------------post the transaction
        transaction = Transaction(
            amount=data['amount'],
            receiver_account=data['receiver_account'],
            sender_id=data['sender_id'],
            category_id=Category.query.filter_by(type=data['category']).first().id,
            status='Sent'
        )
        #---- we check if the receiver is a beneficiary of the sender
        #---------check if th erciver id is in 
        #--------------move the money 
        sender = User_Profile.query.filter_by(id = data['sender_id']).first()
        sender.wallet.balance -= data['amount']
        receiver = User_Profile.query.filter_by(Account = data['receiver_account']).first()
        receiver.wallet.balance += data['amount']

        db.session.add(transaction)
        db.session.commit()
        print(sender.wallet.balance)
        print('_________________________________________')
        print(receiver.wallet.balance)



     





        return make_response(jsonify({"message":f"money from wallet to {receiver.first_name}"}))
        

