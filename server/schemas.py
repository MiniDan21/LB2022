from re import match
from fastapi import Request, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.exceptions import ValidationError
from pydantic import BaseModel, Field, validator
from db import async_session, users_table
from server.auth import Auth


auth = Auth()


class LoginDetails(BaseModel):
    login: str = Field(..., min_length=5, max_length=21, regex=r'^[A-Za-z0-9]+$')
    password: str = Field(..., min_length=5, max_length=21, regex=r'^[A-Za-z0-9]+$')

    # class Config:
    #     validate_assignment = True
    #     error_msg_templates = {
    #         'value_error.any_str.max_length': 'max_length: 21',
    #         'value_error.any_str.min_length': 'max_length: 5',
    #         'value_error.str.regex': 'msg: Пароль или логин должны состоять из латиницы(a-z) или цифр(0-9)'
    #     }


class SignUpDetails(LoginDetails):
    first_name: str = Field(..., min_length=1, max_length=20, regex=r'^[А-Яа-я ]{1,30}$')
    last_name: str = Field(..., min_length=1, max_length=20, regex=r'^[А-Яа-я ]{1,30}$')
    group_number: str = Field(..., regex=r"^([А-Яа-я]+)\d{0,2}([ЦцИи])?-(1[1-9])(Б|б|БВ|бв|Бв|бВ)?\s*$")
    vk_ref: str = Field(..., min_length=1, max_length=40, regex=r'^(https://vk.com/)?[A-Za-z0-9_.]+$')


class NameOfTeam(BaseModel):
    name: str = Field(..., min_length=1, max_length=21)


class InvitationCode(BaseModel):
    code: str = Field(..., regex=r'22[A-Za-z]{4}LB')


class UserId(BaseModel):
    user_id: int = Field(...)
