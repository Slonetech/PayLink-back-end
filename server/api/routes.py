from api import  make_response,jsonify,User_Profile,User,UserBeneficiary,Beneficiary,Wallet,Transaction,WalletActivity,app,db,request
from api import  make_response,jsonify,Category,app,db,request
from api.serialization import api,ns,auth,Resource
from api.serialization import UserProfiles_Schema,UserProfile_Schema
from api.serialization import wallet,wallets_Schema,wallet_Schema,update_wallet
from api.serialization import transactions_Schema,create_transaction,wallet_activities_Schema,transactions
from api.serialization import post_user,user_model_input,User_Schema
from api.serialization import create_wallet
# from api.serialization import user_schema,ns,auth,Resource,user_model_input,login_input_model,vendor_model_update
# from api.serialization import vendor_model_input,post_user
import uuid
import string
import random 
from random import randint, choice as rc


import jwt


from flask_jwt_extended import JWTManager,jwt_required
from flask_jwt_extended import create_refresh_token,create_access_token, get_jwt_identity
# from flask_jwt_extended import get_jwt_claims

jwt = JWTManager(app)



@auth.route('/signup')
class Signup (Resource):

    @auth.expect(user_model_input)
    # @auth.marshal_with(post_user)
    def post(self):
      
        data =request.get_json()
        print(data)
    
        if data['user_name'] in [user.user_name for user in User.query.all()]:
            return make_response(jsonify({"message":"username already taken"}))
        
      
        new_user = User(
            user_name=data['user_name'],           
            password_hash = data['password'],
            public_id = str(uuid.uuid4()),
            is_admin=0

        )


        db.session.add(new_user)
        db.session.commit()


        
        '''------------populat user_profile table-------------------------'''

        code =['+254','+256','+252','+251']
        user_profile = User_Profile(            
        first_name=data['first_name'],
        last_name = data['last_name'],
        phone_number=str(rc(code)) +str(data['phone_number']),
        address=data['address'],
        Account = ''.join(random.choice(string.digits) for _ in range(14)),            
        profile_pictur='https://images.ctfassets.net/h6goo9gw1hh6/2sNZtFAWOdP1lmQ33VwRN3/24e953b920a9cd0ff2e1d587742a2472/1-intro-photo-final.jpg?w=1200&h=992&fl=progressive&q=70&fm=jpg',
        user_id = new_user.id,
        # email=data['first_name']+'@' + rc(['gmail','yahoo','outlook','iCloud Mail '])+'.com',
        )

        db.session.add(user_profile)
        db.session.commit()




        '''---------CREATE A WALLET FOR THE USER-----------------------------'''
        new_wallet = Wallet(
            balance=50000,
            user_prof_id=user_profile.id,
            type='Main',
            status = 'Active',
            Account =user_profile.Account
        )
       
    


        db.session.add(new_wallet)
        db.session.commit()
        # print('-----------------------------------------------')

        # print(new_user)

        # return new_user,200
        # return make_response(User_Schema.dump(user_profile),200)
        # return make_response(UserProfile_Schema.dump(user_profile),200)
        # return make_response(wallet_Schema.dump(new_wallet),200)
        return make_response(jsonify(
            {"message":"thank you for joining us"}
        ),200)


# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@auth.route('/login')
class Login(Resource):
    def post(self):
        print('---------------------------')
        print(request.get_json())
        username = request.get_json().get("username",None)
        password = request.get_json().get("password",None)


        if not username and not password:
            return jsonify({"msg": "Bad username or password"})
        
        user = User.query.filter_by(user_name=username).first()
        # print(user)
    
        print('----------------------------------------')    
        if not user:
            return jsonify({"message": "User not found"})
        if  not user.authenticate(password):
              return jsonify({"msg": "Bad username or password"})
               

        user_profile = User_Profile.query.filter_by(user_id=user.id).first()
        # print(user_profile)
        # user_claims= UserObject( user_id=user.id ,user_name=user.user_name,user_role=user.roles)
        # print(user_claims)
     
     
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return jsonify({
            "access_token": access_token,
            "refresh_token":refresh_token,
            "user_id":user_profile.id,
            "user_name":user_profile.first_name,
            "user_role":user.is_admin,
            "user_profile_pic":user_profile.profile_pictur,
            "account_number":user_profile.Account

            

        })


       #***************R E F R E S H_____-T O K E N 
@auth.route('/refresh')
class Refresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        # print(request.get_json())
        identity = get_jwt_identity()
        print(identity)
        access = create_access_token(identity = identity)

    
        return jsonify({"access_token":access}),200




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
@wallet.route('/wallet')
class Wallets(Resource):
    def get(self):
        all_wallets = Wallet.query.all()

        if not all_wallets:
            return make_response(jsonify({"message":"no Wallets currently"}))
        
        return make_response(wallets_Schema.dump(all_wallets),200)
    


    '''---------------------------P O S T ------------W A L  L E T----------------'''
    @wallet.expect(create_wallet)
    def post(self):
        data = request.get_json()
        user_prof_id = data['user_prof_id']
        type = data['type']
        new_wallet = Wallet(
            balance=0,
            user_prof_id=user_prof_id,
            type =type,
            status = 'Active'

        )
        # new_wallet.save()
        return make_response(wallet_Schema.dump(new_wallet),200)

    
    
 
@wallet.route('/wallet/<int:id>')
class Wallets(Resource):
    @wallet.expect(update_wallet)
    def post(self,id):
        data = request.get_json()
     
        wallet = Wallet.query.filter_by(user_prof_id=id).first()
        if not wallet:
            return make_response(jsonify({"message":"wallet NOT found"}))
        wallet.balance +=data['amount']
        db.session.commit()
        print(wallet)
        
        # return make_response(wallets_Schema.dump(all_wallets),200)
        return make_response(wallet_Schema.dump(wallet),200)
    

   
 



'''_____________T R A N S A C T I O N S____________________________'''
@transactions.route('/transactions')
class Transactions(Resource):
    def get(self):
        all_transactions = Transaction.query.all()

        if not all_transactions:
            return make_response(jsonify({"message":"no beneficiaries found"}))
        
        return make_response(transactions_Schema.dump(all_transactions),200)
    
    #_______C R E A T E _____________-T R A N S A C T I O N S_________________
    @transactions.expect(create_transaction)
    def post(self):
        data = request.get_json()
        print(data)
        #-------------------------post the transaction
        transaction = Transaction(
            amount=data['amount'],
            receiver_account=data['account'],
            sender_id=data['sender_id'],
            category_id=Category.query.filter_by(type=data['category']).first().id,
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
        # print(sender.wallet.balance)
        # print('_________________________________________')
        # print(receiver.wallet.balance)


        sender_wallet_activity = WalletActivity(
            user_id =sender.id,
            transaction_type ='sent',
            amount=transaction.amount,
            description = f'sent money to {receiver.first_name}',
            transaction_id = transaction.id       
              )
        

        receiver_wallet_activity = WalletActivity(
            user_id =receiver.id,
            transaction_type ='received',
            amount=transaction.amount,
            description = f'received money from {sender.first_name}',
            transaction_id = transaction.id        )

        db.session.add_all([sender_wallet_activity,receiver_wallet_activity])
        db.session.commit()


        return make_response(jsonify({"message":f"money from wallet to {receiver.first_name}"}))
        


'''____________W A L L E T __________-A C T I V I T Y________________________'''

@wallet.route('/wallet-Activity')
class WalletsActivity(Resource):
    def get(self):
        wallet_activity = WalletActivity.query.all()

        if not wallet_activity:
            return make_response(jsonify({"message":"no beneficiaries found"}))
        
        return make_response(wallet_activities_Schema.dump(wallet_activity),200)
    


#cant see the wallet so i am writing this comment to push 