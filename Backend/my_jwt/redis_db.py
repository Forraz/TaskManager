import redis
from config.settings import REDIS

redis_cli = redis.Redis(**REDIS)
