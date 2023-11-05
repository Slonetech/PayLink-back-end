from api import  make_response,jsonify,User,app,ma,User_Profile,Category,Beneficiary
from api import  Wallet,Transaction,WalletActivity

from flask_restx import Api,Resource,Namespace,fields

api = Api()
api.init_app(app)


ns=Namespace('/')
api.add_namespace(ns)


auth=Namespace('auth')
api.add_namespace(auth)

transactions=Namespace('transaction')
api.add_namespace(transactions)

wallet=Namespace('wallet')
api.add_namespace(wallet)

beneficiaries=Namespace('beneficiaries')
api.add_namespace(beneficiaries)




class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        ordered = True

    # beneficiaries = ma.List(ma.Nested("BeneficiarySchema"))
    # wallet = ma.Nested("WalletSchema")

User_Schema = UserSchema()
Users_Schema = UserSchema(many=True)




class UserProfileSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User_Profile
        ordered = True

    beneficiaries = ma.List(ma.Nested("BeneficiarySchema"))
    wallet = ma.List(ma.Nested("WalletSchema"))
    transactions =  ma.List(ma.Nested("TreansactionSchema"))
    wallet_ctivities=ma.List(ma.Nested("WalletActivitySchema"))

UserProfile_Schema = UserProfileSchema()
UserProfiles_Schema = UserProfileSchema(many=True)


'''------------B E N E F I C I A R I E S      S C H E M A---------'''

class BeneficiarySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Beneficiary
        ordered = True

Beneficiary_Schema = BeneficiarySchema()
Beneficiarys_Schema = BeneficiarySchema(many=True)

'''__________________________W A L L E T____________________________________________'''

class WalletSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Wallet
        ordered = True
    balance = fields.Float()
    user_prof_id=ma.auto_field()
    
wallet_Schema = WalletSchema()
wallets_Schema = WalletSchema(many=True)



class TreansactionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Transaction
        ordered = True
    sender_id=ma.auto_field()
    # category=ma.auto_field()
    category = ma.Nested("CategorySchema")


 
transaction_Schema = TreansactionSchema()
transactions_Schema = TreansactionSchema(many=True)



class CategorySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Category
        ordered = True
 
category_Schema = CategorySchema()
categories_Schema = CategorySchema(many=True)

class WalletActivitySchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = WalletActivity
        ordered = True

    user_id=ma.auto_field()
    
wallet_activity_Schema = WalletActivitySchema()
wallet_activities_Schema = WalletActivitySchema(many=True)


class TreansactionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Transaction
        ordered = True
    sender_id=ma.auto_field()
    # category=ma.auto_field()
    category = ma.Nested("CategorySchema")


 
transaction_Schema = TreansactionSchema()
transactions_Schema = TreansactionSchema(many=True)



'''_________A P I _________M O D E L S___________________'''

                #*********WALLET API.MODEL*************************************
update_wallet =api.model('update_wallet',{

    'id':fields.Integer,
  


})
create_wallet =api.model('create_wallet',{
# i will  set the amoun to 0 since the is a new wallt the user created and status to Active
    'user_prof_id':fields.Integer,
    'type':fields.String,
  


})
move_money =api.model('move_money',{
# i will  set the amoun to 0 since the is a new wallt the user created and status to Active
    'amount':fields.Integer,
    'from_wallet':fields.String,
    'to_wallet':fields.String,
    'user_id':fields.String,
  


})
create_transaction =api.model('create_transaction',{
    
    'amount':fields.Integer,
    'receiver_account':fields.String,
    'sender_id':fields.String,
    'category':fields.String,

 
  

})

'''__________S I G N U P ____________'''

user_model_input =api.model('signup',{
    
    'amout':fields.String,
    'type':fields.String,
    'user_id':fields.String,
    # 'roles':fields.String change--- this when handlind the posting
    # 'public_id':fields.String,-- and this one aswell
  

})
post_user =api.model('signup_post',{


    'first_name':fields.String,
    'last_name':fields.String,
    'user_name':fields.String,
    'email':fields.String,
    'password':fields.String,
    'address':fields.String,
    'phone':fields.String
  

})



login_model =api.model('login',{
    
    'user_name':fields.String,
    # 'profile_picture':fields.String,
    'password':fields.String,
    # 'roles':fields.String change--- this when handlind the posting
    # 'public_id':fields.String,-- and this one aswell
  

})






