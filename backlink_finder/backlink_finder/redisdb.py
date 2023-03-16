import redis

class RedisDB:

    def __init__(self, host, port, db):
        self.host = host
        self.port = port
        self.db = db
        self.r = redis.StrictRedis(host=self.host, port=self.port, db=self.db)
    
    def get(self, key):
        return self.r.get(key)

    def set(self, key, value):
        self.r.set(key, value)

    def delete(self, key):
        self.r.delete(key)

    def exists(self, key):
        return self.r.exists(key)

    def get_all(self):
        return self.r.keys()
    
    def set_to_hash(self, key, field, value):
        try:
            self.r.hset(key, field, value)
        except Exception as e:
            print(e)
    
    def exists_in_hash(self, hash_name, field):
        return self.r.hexists(hash_name, field)
    
    def get_from_hash(self, hash_name, field):
        return self.r.hget(hash_name, field)
    
    def get_all_from_hash(self, hash_name):
        return self.r.hgetall(hash_name)
    
    def get_keys_from_hash(self, hash_name):
        return self.r.hkeys(hash_name)