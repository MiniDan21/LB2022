from fastapi import Request, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from db import async_session, users_table
from server.auth import Auth


auth = Auth()


class LoginDetails(BaseModel):
    login: str = Field(..., min_length=5, max_length=21, regex=r'[A-Za-z][A-Za-z0-9]+\S+')
    password: str = Field(..., min_length=5, max_length=15, regex=r'[A-Za-z0-9]{5,15}')


class SignUpDetails(LoginDetails):
    name: str = Field(..., min_length=1, regex=r'[А-Яа-я]{1,}')
    surname: str = Field(..., min_length=1, regex=r'[А-Яа-я]{1,}')
    link: str = Field(..., regex=r'[A-Za-z0-9]+')
    group: str = Field(..., regex=r'[А-Яа-я]+[0-9]{1,2}[А-Яа-я]?-1[0-9]?[Б]?')


class AuthedCookie(Request):
    pass
#     async def check_cookie(self, auth: HTTPAuthorizationCredentials = Security(security)):
#         try:
#             temp_login = auth.decode_token(self.cookies['access_token'])
#             async with async_session() as db:
#                 if await users_table.check_user(session=db, login=temp_login):
#                     return '<Страница>, доступная вам'
#         except KeyError:
#             pass
#         return HTTPException(status_code=401, detail='Вы не авторизировались')
