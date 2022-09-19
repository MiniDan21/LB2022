import logging
from fastapi import FastAPI, HTTPException, Depends, Response, Cookie, Header, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from db import async_engine, async_session, Base, users_table, teams_table, User, Team
from server.auth import Auth, token_required
from server.schemas import SignUpDetails, LoginDetails, NameOfTeam, InvitationCode, UserId
from config import settings


async def create_tables(drop: bool = False):
    async with async_engine.begin() as conn:
        if drop:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI()
auth = Auth()

origins = [
    'https://localhost',
    'https://localhost:8080',
    'https://local.legends.batalichev.pro:8080',
    'https://bauman2022.netlify.app'
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)


def return_login(header: Header):
    return auth.decode_token(header.get('Authorization', '').split()[1])


@app.on_event('startup')
async def startup():
#    await create_tables(drop=True)
    await create_tables()


@app.on_event('shutdown')
async def shutdown():
    pass
#    await create_tables(drop=True)


@app.post('/api/user/sign_up', status_code=201)
async def sign_up(request: SignUpDetails):
    async with async_session() as db:
        details = request.dict()
        token = auth.encode_token(request.login)
        user = User(**details)
        if await users_table.check_login(session=db, login=user.login):
            raise HTTPException(status_code=400, detail='Такой логин уже занят!')
        await users_table.create(session=db, obj_model=user)
    return {'access_token': token}


@app.post('/api/user/sign_in', status_code=200)
async def sign_in(request: LoginDetails):
    async with async_session() as db:
        user = await users_table.check_login_and_password(session=db, login=request.login, password=request.password)
    if not user:
        raise HTTPException(status_code=400, detail='Неправильный логин или пароль!')
    return {'access_token': auth.encode_token(login=request.login)}


@token_required
@app.get('/api/user/info', status_code=200)
async def user_info(request: Request):
    async with async_session() as db:
        user = await users_table.check_login(session=db, login=return_login(request.headers))
    if user:
        return user
    raise HTTPException(status_code=400, detail='Пользователь не найден!')


@token_required
@app.get('/api/user/all', status_code=200)
async def user_all(request: Request):
    async with async_session() as db:
        users = await users_table.get_all(session=db)
    if users:
        return [user for user in users]
    raise HTTPException(status_code=400, detail='Пользователи не найдены!')


@token_required
@app.get('/api/team/info')
async def team_info(request: Request):
    async with async_session() as db:
        user = await users_table.check_login(session=db, login=return_login(request.headers))
        team = await teams_table.check_team_id(session=db, team_id=user.team_id)
    if team:
        return team
    raise HTTPException(status_code=400, detail='У вас нет команды!')


@token_required
@app.get('/api/team/all')
async def team_all(request: Request):
    async with async_session() as db:
        teams = teams_table.get_all(session=db)
    if teams:
        return [team for team in teams]
    raise HTTPException(status_code=400, detail='Команды не найдены!')


@token_required
@app.get('/api/team/members')
async def team_members(request: Request):
    async with async_session() as db:
        user = await users_table.check_login(session=db, login=return_login(request.headers))
        if user:
            team_id = user.team_id
        else:
            raise HTTPException(status_code=400, detail='Пользователь не найден!')
        members = await users_table.get_all_members(session=db, team_id=team_id)
    if members:
        return [member for member in members]
    raise HTTPException(status_code=400, detail='Участники команды не найдены!')


@token_required
@app.post('/api/team/join')
async def team_join(body: InvitationCode, request: Request):
    async with async_session() as db:
        team = await teams_table.check_by_code(session=db, code=body.code)
        if team:
            if team.amount_of_members >= 8:
                raise HTTPException(status_code=400, detail='Команда переполнена!')
            team_id = team
        else:
            raise HTTPException(status_code=400, detail='Команда не найдена!')
        await users_table.set_team_by_login(session=db, login=return_login(request.headers), team_id=team_id)
        await teams_table.add_member(session=db, team_id=team_id)
        # team - объект до увелечения количества участников на 1, т.е. до 8, поэтому их пока 7
        if team.amount_of_members == 7:
            return 'full'
        return 'success'


@token_required
@app.post('/api/team/create')
async def team_create(body: NameOfTeam, request: Request):
    async with async_session() as db:
        code = settings.invitation_code
        while await teams_table.check_by_code(session=db, code=code):
            code = settings.invitation_code
        if await teams_table.check_name(session=db, name=body.name):
            raise HTTPException(status_code=400, detail='Это название команды уже занято!')
        team = Team(**body.dict())
        team.invitation_code = code
        await teams_table.create(session=db, obj_model=team)
        await users_table.make_captain(session=db, login=return_login(request.headers))
        team = await teams_table.check_name(session=db, name=team.name)
        await teams_table.add_member(session=db, team_id=team.user_id)
        await users_table.set_team_by_login(session=db, login=return_login(request.headers), team_id=team.team_id)
    return team.invitation_code


@token_required
@app.get('/api/team/change')
async def team_change(body: UserId, request: Request):
    async with async_session() as db:
        captain = await users_table.check_id(session=db, id=body.user_id)
        new_captain = await users_table.check_login(session=db, login=return_login(request.headers))
        if not (captain and new_captain):
            raise HTTPException(status_code=400, detail='Пользователи не найдены!')
        await users_table.make_captain(session=db, login=captain.login, demotion=True)
        await users_table.make_captain(session=db, login=new_captain.login, demotion=False)
    return new_captain + ' новый капитан!'


@token_required
@app.delete('/api/team/kick')
async def team_kick(body: UserId, request: Request):
    async with async_session() as db:
        user = await users_table.check_id(session=db, id=body.user_id)
        await users_table.delete_user_from_team(session=db, login=user.login)
    return 'success'


@token_required
@app.delete('/api/team/leave')
async def team_leave(request: Request):
    async with async_session() as db:
        await users_table.delete_user_from_team(session=db, login=return_login(request.headers))

    return 'success'
