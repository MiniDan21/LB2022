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
    first_name: str = Field(..., min_length=1, regex=r'[А-Яа-я ]{1,}')
    last_name: str = Field(..., min_length=1, regex=r'[А-Яа-я ]{1,}')
    vk_ref: str = Field(..., regex=r'[A-Za-z0-9]+')
    group: str = Field(..., regex=r'[А-Яа-я]+[0-9]{1,2}[А-Яа-я]?-1[0-9]?[Б]?')


class NameOfTeam(BaseModel):
    name: str = Field(..., min_length=1, max_length=21)


class InvitationCode(BaseModel):
    code: str = Field(..., regex=r'22[A-Za-z]{4}LB')
