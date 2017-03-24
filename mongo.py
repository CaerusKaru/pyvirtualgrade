'''
mongo.py -- interface for instance of MongoDB
Created by: Adam Plumer
Date created: Feb 24, 2017
'''


import pymongo

client = pymongo.MongoClient("mongodb://tester:vgrade-test@vm-virtualgrade:27017/test")

db = client.test
test1 = db.test1.find_one({})
print(test1)

