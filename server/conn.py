import pymongo
import redis

class Conn():
    def __init__(self):
        self._mongo_list = []
        self._redis_list = []
        self._redis_pool = None

    def gen_mongo(self, host, port):
        conn = pymongo.MongoClient(host=host, port=port)
        self._mongo_list.append(conn)
        return conn

    def enable_redis_pool(self,host,port):
        self._redis_pool = redis.ConnectionPool(host=host, port=port)

    def gen_redis(self,host=None,port=None,db=None):
        conn = None
        if self._redis_pool:
            conn = redis.Redis(connection_pool=self._redis_pool)
        elif host and port and db:
            conn = redis.Redis(host=host, port=port,db=db)
        if conn:
            self._redis_list.append(conn)
        return conn
