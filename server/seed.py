from api import app,db,User,Category
from faker import Faker
import random 
from random import randint, choice as rc
import uuid


fake = Faker()

with app.app_context():
    '''-------------- USER AUTHENTICATION TABLE-----------------------'''
    User.query.delete()

    # user_list = []
    # for user in range(50):      

        
    #     user_name = fake.unique.user_name()
    #     company = fake.company()

    #     user = User(
    #         user_name=user_name,
    #         # email=user_name.split(' ')[0]+"@"+company[:5]+".com",
    #         profile_picture='https://images.pexels.com/photos/733872/pexels-photo-733872.jpeg?auto=compress&cs=tinysrgb&dpr=1&w=500',
    #         password_hash = str(random.randint(2,54324423)),
    #         public_id = str(uuid.uuid4()),
    #         roles=rc(['Admin','Vendor','Customer'])

         
    #     )
    #     user_list.append(user)
    # db.session.add_all(user_list)
    db.session.commit()


