import time
from base64 import b64encode, b64decode
from config import settings
from hashlib import sha256
import hmac
from .redis_db import redis_refresh_tokens, redis_access_tokens


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

    token = redis_refresh_tokens.get(user_id)

    if token:
        return token.decode() == token

    return False


def check_access_token(token):
    try:
        user_id = eval(decode(token).split(".")[1])['user_id']

    except Exception as e:
        return False

    db_token = redis_access_tokens.get(user_id)

    if token:
        return db_token.decode() == token

    return False


def delete_tokens(request):
    user_id = request.user.id
    redis_refresh_tokens.delete(user_id)
    redis_access_tokens.delete(user_id)


class TokenMixin:
    typ = None
    db = None
    alg = 'sha256'

    def __init__(self):
        self.header = None
        self.payload = None
        self.signature = None

    @staticmethod
    def get_exp():
        return int(time.time()) + JWT['ACCESS_TOKEN_LIFETIME']

    def generate_header(self) -> None:
        self.header = encode(str({'alg': self.alg, 'typ': self.typ}))

    def generate_payload(self, user) -> None:
        exp = self.get_exp()
        user_id = user.id

        self.payload = encode(str({'user_id': user_id, 'exp': exp}))

    def generate_signature(self) -> None:
        self.signature = encode(str(hmac.new(SECRET_KEY.encode(), self.header + b"." + self.payload, sha256).digest().
                                    hex()))

    def generate_token(self, user) -> str:
        self.generate_header()
        self.generate_payload(user)
        self.generate_signature()

        token = ".".join([self.header.decode(), self.payload.decode(), self.signature.decode()])

        if self.db.get(user.id):
            self.db.delete(user.id)

        self.db.set(user.id, token, ex=JWT[f'{self.typ.upper()}_LIFETIME'])

        return token


class AccessToken(TokenMixin):
    typ = 'access_token'
    db = redis_access_tokens


class RefreshToken(TokenMixin):
    typ = 'refresh_token'
    db = redis_refresh_tokens





