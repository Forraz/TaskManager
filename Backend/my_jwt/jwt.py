import time
from base64 import b64encode, b64decode
from config import settings
from hashlib import sha256
import hmac
from .redis_db import redis_cli


SECRET_KEY = settings.SECRET_KEY
JWT = settings.JWT


def encode(obj: str) -> bytes:

    return b64encode(obj.encode())


def decode(code: str) -> str:
    lst = code.split(".")

    result = []

    for i in lst:
        i = b64decode(i.encode()).decode()
        result.append(i)

    return ".".join(result)


def check_refresh_token(token):
    try:
        user_id = eval(decode(token).split(".")[1])['user_id']

    except Exception:
        return False

    return redis_cli.get(user_id).decode() == token


def check_access_token(token):
    try:
        exp = eval(decode(token).split(".")[1])['exp']

    except Exception:
        return False

    return exp > int(time.time())


class TokenMixin:
    typ = None
    alg = 'sha256'

    @staticmethod
    def get_exp():
        return int(time.time()) + JWT['ACCESS_TOKEN_LIFETIME']

    @classmethod
    def generate_header(cls) -> None:
        cls.header = encode(str({'alg': cls.alg, 'typ': cls.typ}))

    @classmethod
    def generate_payload(cls, user) -> None:
        exp = cls.get_exp()
        user_id = user.id

        cls.payload = encode(str({'user_id': user_id, 'exp': exp}))

    @classmethod
    def generate_signature(cls, user) -> None:
        cls.generate_header()
        cls.generate_payload(user)

        cls.signature = encode(str(hmac.new(SECRET_KEY.encode(), cls.header + b"." + cls.payload, sha256).digest().hex()))

    @classmethod
    def generate_token(cls, user) -> str:
        cls.generate_signature(user)

        return ".".join([cls.header.decode(), cls.payload.decode(), cls.signature.decode()])


class AccessToken(TokenMixin):
    typ = 'access_token'


class RefreshToken(TokenMixin):
    typ = 'refresh_token'

    @classmethod
    def generate_token(cls, user) -> str:
        token = super().generate_token(user)
        if redis_cli.get(user.id):
            redis_cli.delete(user.id)

        redis_cli.set(user.id, token, ex=JWT['REFRESH_TOKEN_LIFETIME'])

        return token




