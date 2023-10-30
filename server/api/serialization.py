from api import  make_response,jsonify,User,app,ma,User_Profile,UserBeneficiary,Beneficiary,Wallet,Transaction

from flask_restx import Api,Resource,Namespace,fields

api = Api()
api.init_app(app)


ns=Namespace('/')
api.add_namespace(ns)


auth=Namespace('auth')
api.add_namespace(auth)

wallet=Namespace('wallet')
api.add_namespace(wallet)



class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        ordered = True

    beneficiaries = ma.List(ma.Nested("BeneficiarySchema"))
    wallet = ma.Nested("WalletSchema")

User_Schema = UserSchema()
Users_Schema = UserSchema(many=True)




class UserProfileSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User_Profile
        ordered = True

    beneficiaries = ma.List(ma.Nested("BeneficiarySchema"))
    wallet = ma.Nested("WalletSchema")



UserProfile_Schema = UserProfileSchema()
UserProfiles_Schema = UserProfileSchema(many=True)



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

    user_prof_id=ma.auto_field()
    
wallet_Schema = WalletSchema()
wallets_Schema = WalletSchema(many=True)

                #*********WALLET API.MODEL
update_wallet =api.model('update_wallet',{

    'amount':fields.Integer,
  


})




class TreansactionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Transaction
        ordered = True
    sender_id=ma.auto_field()
 
transaction_Schema = TreansactionSchema()
transactions_Schema = TreansactionSchema(many=True)



'''_________A P I _________M O D E L S___________________'''

create_transaction =api.model('create_transaction',{
    
    'amount':fields.Integer,
    'receiver_account':fields.String,
    'sender_id':fields.String,
    'category':fields.String,

 
  

})
'''__________S I G N U P ____________'''

user_model_input =api.model('signup',{
    
    'user_name':fields.String,
    # 'profile_picture':fields.String,
    'password':fields.String,
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