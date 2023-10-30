from api import app,db,User,User_Profile,Wallet,Transaction,Beneficiary,UserBeneficiary,Category,WalletActivity
from faker import Faker
import random 
from random import randint, choice as rc
import uuid
import random
import string
# print(''.join(random.choice(string.digits) for _ in range(14)))


fake = Faker()

with app.app_context():
    User.query.delete()

    user_list = []
    for user in range(50):      

        
        user_name = fake.unique.user_name()
        company = fake.company()

        user = User(
            user_name=user_name,
            password_hash = str(random.randint(2,54324423)),
            public_id = str(uuid.uuid4()),
            is_admin=rc([0,1])

         
        )
        user_list.append(user)
    db.session.add_all(user_list)
    db.session.commit()


            # email=user_name.split(' ')[0]+"@"+company[:5]+".com",


    '''-------------- USER Profile TABLE-----------------------'''
    User_Profile.query.delete()

    users_profile_list = []
    users =[user.id for user in user_list if user.is_admin ==0]
    i=0
    for user in user_list:      

        if user.is_admin==0:
        
      
          
    #
            user = User_Profile(
                first_name = fake.unique.first_name(),
                last_name = fake.unique.last_name(),
                address = fake.address(),
                phone_number=random.randint(1111111111,9999999999),
                Account = ''.join(random.choice(string.digits) for _ in range(14)),            
                profile_pictur='https://images.pexels.com/photos/733872/pexels-photo-733872.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500',
                user_id = [user.id for user in user_list][i]
                
            )
            i+=1
   
            users_profile_list.append(user)
    db.session.add_all(users_profile_list)
    db.session.commit()



    Wallet.query.delete()

    wallet_list = []
    for user in users_profile_list:
        wallet = Wallet(
                    balance=random.randint(1000, 50000),
                    user_prof_id= user.id
                    
                )
        wallet_list.append(wallet)

    db.session.add_all(wallet_list)
    db.session.commit()


    '''C A T E G O R I E S_________T A B L E         S E E D I N G _______________'''
    Category.query.delete()
    category_list=[]
    categories = ["Food", "Rent", "Fees", "Investment", "Entertainment", "Transportation", "Utilities", "Healthcare", "Education", "Travel"]
    i=0
    for i in range(8):
         category = Category(
              type=categories[i]
         )
         i+=1
         category_list.append(category)    
    db.session.add_all(category_list)
    db.session.commit()
        



    '''Transactions table        S E E D I N G _______________'''

    Transaction.query.delete()
    category_id = [cat.id for cat in category_list]
    transaction1 = Transaction(
        sender_id=[user.id for user in users_profile_list][0],
        amount= random.randint(111111,999999),
        receiver_account=[user.Account for user in users_profile_list][1],
        category_id =rc(category_id)
        
  )
    transaction2 = Transaction(
        sender_id=[user.id for user in users_profile_list][1],
        amount= random.randint(111111,999999),
        receiver_account=[user.Account for user in users_profile_list][2],
        category_id =rc(category_id)
        
  )
    transaction3 = Transaction(
        sender_id=[user.id for user in users_profile_list][2],
        amount= random.randint(111111,999999),
        receiver_account=[user.Account for user in users_profile_list][3],
        category_id =rc(category_id)
        
  )
    transaction4 = Transaction(
        sender_id=[user.id for user in users_profile_list][3],
        amount= random.randint(111111,999999),
        receiver_account=[user.Account for user in users_profile_list][4],
        category_id =rc(category_id)
        
  )
    transaction5 = Transaction(
        sender_id=[user.id for user in users_profile_list][0],
        amount= random.randint(111111,999999),
        receiver_account=[user.Account for user in users_profile_list][3],
        category_id =rc(category_id)
        
  )
    transaction6 = Transaction(
        sender_id=[user.id for user in users_profile_list][0],
        amount= random.randint(111111,999999),
        receiver_account=[user.Account for user in users_profile_list][2],
        category_id =rc(category_id)
        
  )
    transaction7 = Transaction(
        sender_id=[user.id for user in users_profile_list][0],
        amount= random.randint(111111,999999),
        receiver_account=[user.Account for user in users_profile_list][3],
        category_id =rc(category_id)
        
  )
    transaction8 = Transaction(
        sender_id=[user.id for user in users_profile_list][0],
        amount= random.randint(111111,9999999),
        receiver_account=[user.Account for user in users_profile_list][3],
        category_id =rc(category_id)
        
  )

    # db.session.add_all(wallet_list)
    transaction_list = [transaction1,transaction2,transaction3,transaction4,transaction5,transaction6,transaction7,transaction8]
    db.session.add_all(transaction_list)
    db.session.commit()



    '''____________W A L L E T__________A C T I V I T Y ___________________'''


    '''loop thru the transactoions and for each transaction record creat two walletActivity records
    one for the sender and one for the receiver'''
    
    WalletActivity.query.delete()
    wallet_activity_list=[]
    for transaction in transaction_list:
        sender = User_Profile.query.filter_by(id = transaction.sender_id).first()
        receiver = User_Profile.query.filter_by(Account = transaction.receiver_account).first()
        sender_wallet_activity = WalletActivity(
            user_id =sender.id,
            transaction_type ='sent',
            amount=transaction.amount,
            description = f'sent money to {receiver.first_name}',
            transaction_id = transaction.id        )
        
        wallet_activity_list.append(sender_wallet_activity)

        receiver_wallet_activity = WalletActivity(
            user_id =receiver.id,
            transaction_type ='received',
            amount=transaction.amount,
            description = f'received money from {sender.first_name}',
            transaction_id = transaction.id        )
        wallet_activity_list.append(receiver_wallet_activity)
        
    db.session.add_all(wallet_activity_list)
    db.session.flush()
        




    '''user beneficiary  table        S E E D I N G _______________'''
    Beneficiary.query.delete()

    # transaction_list =Transaction.query.all()
    # beneficiary_list =[]
    # for_user_benef =[]
    # for transaction in  transaction_list:
    #     user = User_Profile.query.filter_by(Account = transaction.receiver_account).first()
    #     senders = User_Profile.query.filter_by(id = transaction.sender_id).first()
    #     for_user_benef.append(senders)
        
    #     beneficiary = Beneficiary(
    #          user_profile_id=user.id
    #     )
    #     beneficiary_list.append(beneficiary)
    # db.session.add_all(beneficiary_list)
    db.session.commit()
        
    # print(for_user_benef)

    

       

    '''U S E R ________________B E N F I C I A R Y _________S E E D I N G'''
    UserBeneficiary.query.delete()


    beneficiaries = Beneficiary.query.all()

    # Define your criteria to match user profiles and beneficiaries, and create relationships
    # For example, let's assume you want to associate beneficiaries with user profiles with the same first name.
    # i=0
    # for beneficiary in beneficiaries:
     
    #         # Create a relationship between the user profile and the beneficiary
    #     id = [sender.id for sender in for_user_benef][i]
    #     # print(id)
    #     user_beneficiary = UserBeneficiary(sender_id=id, beneficiary_id=beneficiary.id)
    #     i+=1
    #     db.session.add(user_beneficiary)

    db.session.commit()
    
    

#     '''____USER_PROFILE ___USER______RELATIONSHIP        T E S T I N G _______________'''
    # tesing the one-to-one rlshp between User and User_Profile
    # user1 = User_Profile.query.all()[0]
    # print(user1.user)

    '''____USER_PROFILE ___TRANSACTIONS______RELATIONSHIP        T E S T I N G _______________'''
    user_profile1 = User_Profile.query.all()[4]
    transaction= Transaction.query.all()[4]
    # print(len(transaction.sender_id))
    print(transaction.sender_id)
    # print(user_profile1.transactions)


#----------------beneficiary and user_profile relationship test----------------
    # benef1 = Beneficiary.query.all()[0]
    # user_profile1 = User_Profile.query.all()[0]
    # print(benef1.user_profile)
    # print(user_profile1.beneficiaries)

#--------------wallet and user profile relationship test
    # wallet = Wallet.query.all()[0]
    # user_profile1 = User_Profile.query.all()[0]

    # print(wallet.user_profile)#--  first_name is osmith
    # print(user_profile1.wallet)#-- balance of 41010

# (id: 1, first_name: osmith,last_name: qhurst, address: 1000 Samantha Loaf New Jodi, AL 63102,  phone: 8577326204 )
# (id: 1, balance: 41010,user_id: 1  )