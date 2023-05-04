from django.contrib.auth.middleware import get_user
from django.contrib.auth import authenticate
from my_jwt.jwt import check_access_token
from graphql.error import GraphQLError
from my_jwt.jwt import decode
from django.contrib.auth.models import User


class TokenAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = get_user(request)

        if not user.is_authenticated and 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            token = auth_header.split()[1]

            if not check_access_token(token):
                raise GraphQLError('Invalid access_token')

            user_id = eval(decode(token.split(".")[1]))['user_id']

            user = User.objects.get(id=user_id)

            if user is not None:
                request.user = user

        response = self.get_response(request)

        return response
