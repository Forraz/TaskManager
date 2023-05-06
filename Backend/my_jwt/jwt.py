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
        token = decode(token)
        header = str(eval(token.split(".")[0]))
        payload = eval(token.split(".")[1])
        exp = payload['exp']
        signature = token.split(".")[2]

        new_token = AccessToken()

        new_token.header = encode(header)
        new_token.payload = encode(str(payload))
        new_token.generate_signature()

    except Exception:
        raise False

    return exp > int(time.time()) and str(new_token.signature) == str(encode(signature))


class TokenMixin:
    typ = None
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

        return ".".join([self.header.decode(), self.payload.decode(), self.signature.decode()])


class AccessToken(TokenMixin):
    typ = 'access_token'


class RefreshToken(TokenMixin):
    typ = 'refresh_token'

    def generate_token(self, user) -> str:
        token = super().generate_token(user)
        if redis_cli.get(user.id):
            redis_cli.delete(user.id)

        redis_cli.set(user.id, token, ex=JWT['REFRESH_TOKEN_LIFETIME'])

        return token




