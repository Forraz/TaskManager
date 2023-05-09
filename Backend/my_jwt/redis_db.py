import redis
from config.settings import REDIS

redis_refresh_tokens = redis.Redis(host=REDIS['host'], port=REDIS['port'], db=REDIS['refresh_tokens_db'])
redis_access_tokens = redis.Redis(host=REDIS['host'], port=REDIS['port'], db=REDIS['access_tokens_db'])
