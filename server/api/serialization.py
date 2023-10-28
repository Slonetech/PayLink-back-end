from api import  make_response,jsonify,User,app,ma,User_Profile,UserBeneficiary,Beneficiary,Wallet,Transaction

from flask_restx import Api,Resource,Namespace,fields

api = Api()
api.init_app(app)
ns=Namespace('/')
auth=Namespace('auth')
api.add_namespace(auth)
api.add_namespace(ns)



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



class WalletSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Wallet
        ordered = True

 
wallet_Schema = WalletSchema()
wallets_Schema = WalletSchema(many=True)


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