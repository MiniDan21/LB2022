import logging
from datetime import datetime, timedelta
from functools import wraps
from fastapi import HTTPException, Security, Request
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, APIKeyCookie, APIKeyHeader
import jwt
from db import async_session, users_table
from config import settings


def token_required(f):
    @wraps(f)
    def _verify(request: Request, *args, **kwargs):
        auth_headers = request.headers.get('Authorization', '').split()
        invalid_msg = {
            'message': 'Invalid token. Registration and / or authentication required',
            'authenticated': False
        }
        expired_msg = {
            'message': 'Expired token. Reauthentication required.',
            'authenticated': False
        }
        if auth_headers[0] != 'Bearer':
            raise HTTPException(status_code=401, detail=invalid_msg)
        if len(auth_headers) != 2:
            raise HTTPException(status_code=401, detail=invalid_msg)
        try:
            token = auth_headers[1]
            data = jwt.decode(token, settings.FastApi_secret, 'HS256')
            return f(request, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail=expired_msg)  # 401 is Unauthorized HTTP status code
        except (jwt.InvalidTokenError, Exception) as e:
            raise HTTPException(status_code=401, detail=invalid_msg)
    return _verify


class Auth:
    api_key_cookie = APIKeyCookie(name='access_token', auto_error=False)
    secret = settings.FastApi_secret
    api_key_header = APIKeyHeader(name='Authorization')

    def encode_token(self, login):
        payload = {
            'exp': datetime.utcnow() + timedelta(days=365),
            'iat': datetime.utcnow(),
            'scope': 'access_token',
            'sub': login
        }

        return jwt.encode(
            payload,
            self.secret,
            algorithm='HS256'
        )

    def decode_token(self, token):
        try:
            payload = jwt.decode(token, self.secret, algorithms=['HS256'])
            if payload['scope'] == 'access_token':
                return payload['sub']
            raise HTTPException(status_code=401, detail='Scope for the token is invalid')
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail='Войдите в аккаунт снова.')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Вы не авторизировались!')

    async def cookie_wrapper(self, auth: HTTPAuthorizationCredentials = Security(api_key_cookie)):
        login = self.decode_token(auth)
        async with async_session() as db:
            user = await users_table.check_login(session=db, login=login)
        if not user:
            raise HTTPException(status_code=401, detail='Авторизируйтесь!')
        return login
