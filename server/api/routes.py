from api import  make_response,jsonify,User_Profile,User,Wallet,Transaction,WalletActivity,app,db,request
from api import  Beneficiary,UserBeneficiary,Category,app,db,request,bcrypt,session
from api.serialization import api,ns,auth,Resource
from api.serialization import UserProfiles_Schema,UserProfile_Schema
from api.serialization import wallet,wallets_Schema,wallet_Schema,update_wallet
from api.serialization import transactions_Schema,create_transaction,wallet_activities_Schema,transactions
from api.serialization import post_user,user_model_input,User_Schema,login_model
from api.serialization import create_wallet,move_money
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
        # print(data)
    
        user_exists = User.query.filter_by(user_name=data['user_name']).first() is not None

        if user_exists:
            return make_response({"error": "User already exists"}, 409)
        
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
        # status= rc(['Active', 'Inactive'])
        status= 'Active'
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
       

        return             make_response({"msg":"thank you for joining us",
             "id":new_user.id,
             "user_name":new_user.user_name
             }        ,200
   )


# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@auth.route('/login')
class Login(Resource):
    @auth.expect(login_model)   
    def post(self):
        # print('---------------------------')
        # print(request.get_json())
        username = request.get_json().get("username",None)
        password = request.get_json().get("password",None)


        if not username and not password:
            return make_response( {"msg": "Bad username or password"},401)
        


        user = User.query.filter_by(user_name=username).first()
    
    
        # print('--------------__--__--__--__---------')    
        if user is None:
            return make_response( {"error": "Unauthorized"},401)
        
        #checking if the password is the same as hashed password
        if not bcrypt.check_password_hash(user.password, password):
            return make_response({"error": "Unauthorized"},401)
  
        print('N000000000000000000000')

      
        user_profile = User_Profile.query.filter_by(user_id=user.id).first()
     
        # print(user_profile)
        
        if user_profile.status =='Inactive':
            return make_response({"error": "your Account is deactivated"},401)
        # print('N000000000000000000000')

     
     
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        return  make_response({
            'access_token':access_token,
            'refresh_token':refresh_token,
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

    
        return make_response({"access_token":access},200)









@ns.route('/users')
class UserProfiles(Resource):
    def get(self):
        all_users = User_Profile.query.all()

        if not all_users:
            return make_response({"msg":"no Users found"})
             
        return make_response(UserProfiles_Schema.dump(all_users),200)

 

@ns.route('/user')
class SingleUserProfile(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()

        # print('---------------------------: ',current_user)
        user = User_Profile.query.filter_by(user_id=current_user).first()
        # print(user)

      
             
        return make_response(UserProfile_Schema.dump(user),200)


@ns.route('/user/<int:id>')
class SingleUserProfile(Resource):
    @jwt_required()
    def put(self,id):
        current_user = get_jwt_identity()
        print('---------------------------: ',id)
        user = User_Profile.query.filter_by(id=id).first()

        # print(user)
        # user.status = 'Active'

        if user.status == 'Active':
            user.status  ='Inactive'
        elif  user.status == 'Inactive':
            user.status  ='Active'

        db.session.commit()
      
             
        return make_response(UserProfile_Schema.dump(user),200)

 
 

 

'''_____________W   A   L  L  E  T ____________________________'''
@wallet.route('/wallet')
class Wallets(Resource):
    def get(self):
        all_wallets = Wallet.query.all()

        if not all_wallets:
            return make_response({"msg":"no Wallets currently"})
        
        return make_response(wallets_Schema.dump(all_wallets),200)
    


    '''---------------------------P O S T ------------W A L  L E T----------------'''
    @wallet.expect(create_wallet)
    def post(self):
        data = request.get_json()
        print(data)
        amount = Decimal(data['amount'])
        user_id=data['user_id']
        type = data['type']

        # query all wallet types the user has
        wallet_types = [wallet.type for wallet in Wallet.query.filter_by(user_prof_id = user_id).all()]
        #check if the chosen type already exisits or if the use hser it already
        if type  in wallet_types:
            return make_response({"msg":f"you already have a {type} wallet"},409)
        # deduct the amount the user wants to move from main wallet
        #query the main wallet 
        main_wallet =  Wallet.query.filter_by(user_prof_id = user_id , type ='Main').first()
        #check if the money the user wants to move is lesser than the balance in Main wallet
        if amount > main_wallet.balance:
            needed_balance = amount - main_wallet.balance     
            return make_response({"msg":f"you dont have {amount} take a loan of {needed_balance}?" },409)
        #-----deduction
        main_wallet.balance -=amount

        db.session.commit()
       

        '''--------fin d the wallet that is attached'''
    
        new_wallet = Wallet(
            balance= amount,
            user_prof_id=user_id,
            type = type,
            status = 'Active'

        )
        new_wallet.save()
        print(new_wallet)
        return make_response(wallet_Schema.dump(new_wallet),200)






'''_____________M O V E      M O N E Y  ____________________________'''

@wallet.route('/move-movey')
class Wallets(Resource):
    @wallet.expect(move_money)
    def post(self):
        data = request.get_json()
        print(data)
        amount = Decimal(data['amount'])
        user_id=data['user_id']
        to_wallet = data['to_wallet']
        from_wallet = data['from_wallet']

        #

        # query both the source and target to manipulate them 
        source = Wallet.query.filter_by(type = from_wallet , user_prof_id= user_id).first()
        target = Wallet.query.filter_by(type = to_wallet , user_prof_id= user_id).first()


        if source.type == target.type:
            return make_response({"msg":"we cant move money from and to the same wallet"},409)
        # ------------------------make the transefer
        if source.status =='Inactive':
            return make_response( {"msg":f"{source.type} is Inactive, activate it first" },404)
        #-----check if source has the money
        if amount > source.balance:
            needed_balance = amount - source.balance   
            return make_response({"msg":f"you dont have {amount} in your {source.type} take a loan of {needed_balance}?" },409)
        print(        source.balance)
        print(        target.balance)
        # #deduct form source ---------------------
        source.balance -=amount

        # add to target --------------------
        target.balance +=amount
        source.save()
        target.save()
        db.session.commit()
        print(        source.balance)
        print(        target.balance)
      
        wallets = Wallet.query.filter_by(user_prof_id=data['user_id']).all()

        print(wallets)

        return jsonify(wallets_Schema.dump(wallets))
    




        
 
@wallet.route('/wallet/<int:id>')
class Wallets(Resource):
    @wallet.expect(update_wallet)
    def put(self,id):
        data = request.get_json()
        # print(id)
     
        wallet = Wallet.query.filter_by(id=id).first()
        if not wallet:
            return make_response({"msg":"wallet NOT found"})
        
        
        if wallet.type == 'Main':
              return make_response({"msg":"cannot deactivate Main wallet"})

        if wallet.status == 'Active':
            wallet.status  ='Inactive'
        elif  wallet.status == 'Inactive':
            wallet.status  ='Active'

        db.session.commit()
        # print(wallet)
        
        # # return make_response(wallets_Schema.dump(all_wallets),200)
        return make_response(wallet_Schema.dump(wallet),200)
    

   
 



'''_____________A L L          T R A N S A C T I O N S____________________________'''
@transactions.route('/transactions')
class Transactions(Resource):
    def get(self):
        all_transactions = Transaction.query.all()

        if not all_transactions:
            return make_response({"msg":"no beneficiaries found"})
        
        return make_response(transactions_Schema.dump(all_transactions),200)
    
    '''_______C R E A T E _____________-T R A N S A C T I O N S_________________'''
    @transactions.expect(create_transaction)
    def post(self):
        data = request.get_json()
        print(data)


        '''----------check if-----Beneficary/Receiver-------exists------in the database-------------------'''
        receiver = User_Profile.query.filter_by(Account = data['account']).first()
        if not receiver:
            return make_response(
            {"msg":f"Account does not exist "},404
            )
        # print(ceiv)
        receiver_main_wallet = [ wallet  for wallet in Wallet.query.filter_by(user_prof_id = receiver.id).all() if wallet.type=='Main'][0]
        print(receiver_main_wallet)

        '''-----------U P D A T E ------------------------W A L L E T --------------B A L A N C E'''

        #---- we check if the receiver is a beneficiary of the sender
        #---------check if th erciver id is in 
        #--------------move the money 
        sender = User_Profile.query.filter_by(id = data['sender_id']).first()
        print(sender)
        # -----user has many wallets, so we get the Main wallet
        sender_main_wallet = [ wallet  for wallet in Wallet.query.filter_by(user_prof_id = sender.id).all() if wallet.type=='Main'][0]
        print(sender_main_wallet)
        # print(sender_main_wallet.balance)
        ''' ---------check if amount is greater than what is in their wallet-----------------'''
        if int(data['amount']) > sender_main_wallet.balance:
            remainder =  int(data['amount']) - sender_main_wallet.balance            
            return make_response({"msg":f"you dont have {int(data['amount'])} take a loan of {remainder}?" })

    
        '''---------if else, proceed with the payment ------------------'''
        sender_main_wallet.balance -= int(data['amount'])
        receiver_main_wallet.balance += int(data['amount'])
        '''--------Charge the sender the transaction feees and deduct form the balance------------------'''
        deduction_amount = Transaction.transaction_fees(data['amount'])
        sender_main_wallet.balance -= Decimal(deduction_amount)
        print(deduction_amount)
        print(sender_main_wallet.balance)

        '''----------check if the RECEIVER is a beneficiary of the sender-------------------'''
        is_beneficiary = Beneficiary.query.filter_by(Account = receiver.Account).first()
        if receiver.first_name not in [ben.name for ben in  sender.beneficiaries]:
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
        # print(sender_main_wallet.balance)
        # print('_________________________________________')
        # print(receiver_main_wallet.balance)



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
        # let's return the sender wallet to update the UI
        sender_wallet = User_Profile.query.filter_by(id=sender.id).first().wallet
        return           make_response(wallets_Schema.dump(sender_wallet))
 

'''-----------P E R S O N A L I Z E     T R A N S A C T I O N S---------------'''

@transactions.route('/user_transactions')
class UserTransactions(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        # print('----------------------------',current_user)
        all_transactions = Transaction.query.filter_by(sender_id = current_user).all()
        # print('----------------------',all_transactions)
  

        return make_response(transactions_Schema.dump(all_transactions),200)

       
        

'''____________W A L L E T __________-A C T I V I T Y________________________'''

@wallet.route('/wallet-Activity')
class WalletsActivity(Resource):
    def get(self):
        wallet_activity = WalletActivity.query.all()

        if not wallet_activity:
            return make_response({"message":"no beneficiaries found"})
        
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


# @beneficiaries.route('/user_beneficiaries')
# class UserBeneficiaries(Resource):
#     # @wallet.expect(update_wallet)
#     @jwt_required()
#     def get(self):
#         current_user = get_jwt_identity()
#         print('----------------------------',current_user)
#         beneficiaries = Beneficiary.query.all()
#         # we choose a user till we fix the login and signup
#         user = User_Profile.query.filter_by(id=7).first()
#         benef = user.beneficiaries
#         # if not beneficiaries or not benef:
#         #     return make_response({"msg":"not beneficiaries found in the db"})
#         return make_response(Beneficiarys_Schema.dump(benef))