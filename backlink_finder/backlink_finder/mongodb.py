import pymongo
from bson.objectid import ObjectId

class MongoDB:

    def __init__(self, host, port, database, collection):
        self.client = pymongo.MongoClient(host, port)
        self.db = self.client[database]
        self.collection = self.db[collection]

    def field_exists(self, field):
        return self.collection.find({field: {'$ne': None}})
    
    def find_value_of_field(self, field, value):
        return self.collection.find({field: value})
    
    def field_has_value(self, field, value):
        return self.collection.find({field: {'$eq': value}})
    
    def find_object_by_id(self, id):
        return self.collection.find_one({'_id': ObjectId(id)})
