from datetime import datetime, timedelta
from fastapi import HTTPException, Security, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, APIKeyCookie
import jwt
from db import async_session, users_table
from config import settings


class Auth:
    api_key_cookie = APIKeyCookie(name='access_token', auto_error=False)
    secret = settings.FastApi_secret

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
        res = self.decode_token(auth)
        async with async_session() as db:
            user = await users_table.check_user_by_token(session=db, token=auth)
        if not user:
            raise HTTPException(status_code=401, detail='Авторизируйтесь заново!')
        return res
