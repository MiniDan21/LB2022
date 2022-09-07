from datetime import datetime, timedelta
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, APIKeyCookie
import jwt
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
            raise HTTPException(status_code=401, detail='Token expired')
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail='Invalid token')

    def cookie_wrapper(self, auth: HTTPAuthorizationCredentials = Security(api_key_cookie)):
        return self.decode_token(auth)
