from api import  make_response,jsonify,User_Profile,User,Wallet,Transaction,WalletActivity,app,db,request
from api import  Beneficiary,UserBeneficiary,Category,app,db,request,bcrypt,session
from api.serialization import api,ns,auth,Resource
from api.serialization import UserProfiles_Schema,UserProfile_Schema
from api.serialization import wallet,wallets_Schema,wallet_Schema,update_wallet
from api.serialization import transactions_Schema,create_transaction,wallet_activities_Schema,transactions
from api.serialization import post_user,user_model_input,User_Schema,login_model
from api.serialization import create_wallet
from api.serialization import beneficiaries,Beneficiarys_Schema




# from api.serialization import user_schema,ns,auth,Resource,user_model_input,login_input_model,vendor_model_update
# from api.serialization import vendor_model_input,post_user
import uuid
import string
import random 
from random import randint, choice as rc
from decimal import Decimal


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
    
        user_exists = User.query.filter_by(user_name=data['user_name']).first() is not None

        if user_exists:
            print(session["user_id"]) #= new_user.id
            print('-------------------------------------')
            return make_response(jsonify({"error": "User already exists"}), 409)
        
        '''--------------create a user opject-----------'''
        hashed_password = bcrypt.generate_password_hash(data['password'])
        new_user = User(
            user_name=data['user_name'],           
            password = hashed_password,
            public_id = str(uuid.uuid4()),
            is_admin=0

        )
        db.session.add(new_user)
        db.session.commit()
       



        
        # '''------------populat user_profile table-------------------------'''

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
       

        return make_response(jsonify(
            {"message":"thank you for joining us",
             "id":new_user.id,
             "user_name":new_user.user_name
             }
        ),200)
   


# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@auth.route('/login')
@auth.expect(login_model)
class Login(Resource):
    def post(self):
        print('---------------------------')
        print(request.get_json())
        username = request.get_json().get("user_name",None)
        password = request.get_json().get("password",None)


        if not username and not password:
            return make_response( jsonify({"msg": "Bad username or password"}))
        


        user = User.query.filter_by(user_name=username).first()
        # session["user_id"] = user.id  
        print(session.get('user_id')) 
        # print(user)
    
        print('----------------------------------------')    
        if user is None:
            return make_response( jsonify({"error": "Unauthorized"}), 401)
        
        #checking if the password is the same as hashed password
        if not bcrypt.check_password_hash(user.password, password):
            return jsonify({"error": "Unauthorized"}), 401
    
        # if  not user.authenticate(password):
        #       return jsonify({"msg": "Bad username or password"})


        # session["user_id"] = user.id  
        # print(session['user_id'])             
        return jsonify({
            "id": user.id,
            "user_name": user.user_name
        })
        # user_profile = User_Profile.query.filter_by(user_id=user.id).first()
        # print(user_profile)
        # user_claims= UserObject( user_id=user.id ,user_name=user.user_name,user_role=user.roles)
        # print(user_claims)
     
     
        # access_token = create_access_token(identity=user.id)
        # refresh_token = create_refresh_token(identity=user.id)

        # session["user_id"] = user.id
        # return jsonify({
           
        #     "user_id":user_profile.id,
        #     "user_name":user_profile.first_name,
        #     "user_role":user.is_admin,
        #     "user_profile_pic":user_profile.profile_pictur,
        #     "account_number":user_profile.Account

            

        # })


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


@app.route("/logout", methods=["POST"])
def logout_user():
    session.pop("user_id")
    return "200"

@app.route("/@me")
def get_current_user():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401
    
    user = User.query.filter_by(id=user_id).first()
    return jsonify({
        "id": user.id,
        "user_name": user.user_name
    }) 






@ns.route('/users')
class UserProfiles(Resource):
    def get(self):
        all_users = User_Profile.query.all()

        if not all_users:
            return make_response(jsonify({"message":"no Users found"}))   
             
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
    
    '''_______C R E A T E _____________-T R A N S A C T I O N S_________________'''
    @transactions.expect(create_transaction)
    def post(self):
        data = request.get_json()
        # print(data)


        '''----------check if-----Beneficary/Receiver-------exists------in the database-------------------'''
        receiver = User_Profile.query.filter_by(Account = data['account']).first()
        if not receiver:
                return make_response(jsonify(
            {"message":f"Account does not exist "},
            ))
        '''-----------U P D A T E ------------------------W A L L E T --------------B A L A N C E'''

        #---- we check if the receiver is a beneficiary of the sender
        #---------check if th erciver id is in 
        #--------------move the money 
        sender = User_Profile.query.filter_by(id = data['sender_id']).first()
        ''' ---------check if amount is greater than what is in their wallet-----------------'''
        if int(data['amount']) > sender.wallet.balance:
            remainder =  int(data['amount']) - sender.wallet.balance            
            return make_response({"message":f"you dont have {int(data['amount'])} take a loan of {remainder}?" })

    
        '''---------if else, proceed with the payment ------------------'''
        sender.wallet.balance -= int(data['amount'])
        receiver.wallet.balance += int(data['amount'])
        '''--------Charge the sender the transaction feees and deduct form the balance------------------'''
        print(sender.wallet.balance)
        deduction_amount = Transaction.transaction_fees(data['amount'])
        sender.wallet.balance -= Decimal(deduction_amount)
        print(deduction_amount)
        print(sender.wallet.balance)
        '''----------check if the RECEIVER is a beneficiary of the sender-------------------'''

        is_beneficiary = Beneficiary.query.filter_by(Account = receiver.Account).first()
        if not is_beneficiary:
            beneficiary = Beneficiary(
            name=receiver.first_name,
            Account = receiver.Account
         )
            beneficiary.save()
            # sender.beneficiaries.append(beneficiary)
            user_beneficiary = UserBeneficiary(
             sender_id=sender.id,
             beneficiary_id = beneficiary.id
         )
            user_beneficiary.save()
        # print(sender.wallet.balance)
        # print('_________________________________________')
        # print(receiver.wallet.balance)



        ''' #-------------------------P O S T     T R A N S A C T I O N'''
        transaction = Transaction(
            amount=data['amount'],
            receiver_account=data['account'],
            sender_id=data['sender_id'],
            sender_name=sender.full_name(),
            receiver_name=receiver.full_name(),
            transaction_fee = deduction_amount,         
            category_id=Category.query.filter_by(type=data['category']).first().id,
            transaction_id = Transaction.generate_unique_id()

        )
        transaction.save()


        '''------P O P U L A T E --------W A L L E T-------------A C T I V I T Y       TABLE'''
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


        return make_response(jsonify(
            {"message":f"money from wallet to {receiver.first_name}"},
            ))
        


'''____________W A L L E T __________-A C T I V I T Y________________________'''

@wallet.route('/wallet-Activity')
class WalletsActivity(Resource):
    def get(self):
        wallet_activity = WalletActivity.query.all()

        if not wallet_activity:
            return make_response(jsonify({"message":"no beneficiaries found"}))
        
        return make_response(wallet_activities_Schema.dump(wallet_activity),200)
    


'''------------B E N E F I C I A R I E S      M O D E L--------'''
 
@beneficiaries.route('/beneficiaries')
class Beneficiaries(Resource):
    # @wallet.expect(update_wallet)
    def get(self):
        beneficiaries = Beneficiary.query.all()
        # we choose a user till we fix the login and signup
        user = User_Profile.query.filter_by(id=7).first()
        benef = user.beneficiaries
        if not beneficiaries or not benef:
            return make_response({"msg":"not beneficiaries found in the db"})
        return make_response(Beneficiarys_Schema.dump(benef))