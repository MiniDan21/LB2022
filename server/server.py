from fastapi import FastAPI, HTTPException, Depends, Response, Request
from sqlalchemy.exc import IntegrityError
from db import async_engine, async_session, Base, users_table, teams_table, User, Team
from server.auth import Auth
from server.schemas import SignUpDetails, LoginDetails


async def create_tables(drop: bool = False):
    async with async_engine.begin() as conn:
        if drop:
            await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI()
auth = Auth()


@app.on_event('startup')
async def startup():
    await create_tables(drop=True)
    await create_tables()


@app.on_event('shutdown')
async def shutdown():
    await create_tables(drop=True)


@app.post('/user/sign_up', status_code=201)
async def signup(request: SignUpDetails):
    async with async_session() as db:
        details = request.dict()
        user = User(**details)
        if await users_table.check_login(session=db, login=user.login):
            return 'Такой логин уже занят!'
        await users_table.create(session=db, obj_model=user)
        return 'success'


@app.post('/user/sign_in', status_code=200)
async def login(request: LoginDetails):
    async with async_session() as db:
        user = await users_table.check_login_and_password(session=db, login=request.login, password=request.password)
    if not user:
        return 'Неправильный логин или пароль!'
    return 'success'


@app.get('/user/info', status_code=200)
async def user_info(request: Request):
    async with async_session() as db:
        user = await users_table.check_login(session=db, login=request.cookies.get('login', 'never will happen'))
    if user:
        return user
    return 'unsuccess'


# @app.post('/user/my_team', status_code=200)
# async def post_team(request: Cookie = Depends(auth.cookie_wrapper)):
#     async with async_session() as db:
#         user = users_table.check_user_by_token(session=db, token=request['access_token'])
#         if user.captain:
#             return 'Страница для капитана команды'
#         elif user.team_name:
#             return 'Страница для участника команды'
#     return 'Присоединитесь к команде или создайте ее'
#
#
# @app.get('/user/my_team', status_code=200)
# async def get_team(request: Cookie = Depends(auth.cookie_wrapper)):
#     async with async_session() as db:
#         user = users_table.check_user_by_token(session=db, token=request['access_token'])
#         if user.captain:
#             return 'Страница для капитана команды'
#         elif user.team_name:
#             return 'Страница для участника команды'
#     return 'Присоединитесь к команде или создайте ее'
#
#
# @app.get('/user/my_team/create')
# async def get_create_team(request: Cookie = Depends(auth.cookie_wrapper)):
#     return 'Страница для создании команды'
#
#
# @app.post('/user/my_team/create')
# async def post_create_team(request: NameOfTeam, cookie: Cookie = Depends(auth.cookie_wrapper)):
#     async with async_session() as db:
#         code = settings.invitation_code
#         while await teams_table.check_by_code(session=db, code=code):
#             code = settings.invitation_code
#         if await teams_table.check_name(session=db, name=request.name):
#             return 'Это название команды уже занято'
#         team = Team(**request.dict())
#         team.invitation_code = code
#         await teams_table.create(session=db, obj_model=team)
#         await users_table.make_captain(session=db, token=auth.decode_token(cookie['access_token']))
#     return team.invitation_code
#
#
# @app.get('/user/my_team/join')
# async def join_team(cookie: Cookie = Depends(auth.cookie_wrapper)):
#     async with async_session() as db:
#         user = users_table.check_user_by_token(session=db, token=cookie['access_token'])
#         if user.team_name:
#             return 'У вас уже есть команда!'
#         teams = await teams_table.get_all(session=db)
#     return [{'name': team.name, 'code': team.invitation_code} for team in teams]
#
#
# @app.post('/user/my_team/join')
# async def join_concrete_team(code: InvitationCode, cookie: Cookie = Depends(auth.cookie_wrapper)):
#     async with async_session() as db:
#         user = users_table.check_user_by_token(session=db, token=cookie['access_token'])
#         if user.team_name:
#             return 'У вас уже есть команда!'
#         team_name = await teams_table.check_by_code(session=db, code=code)
#         if not team_name:
#             return 'Неверный код приглашения'
#         users_table.set_team_by_token(session=db, token=cookie['access_token'], team_name=team_name)
#     return RedirectResponse(url='/user/main')


# @app.get('/', status_code=200)
# async def main(request: Request):
#     url = '/user/sign_in'
#     delete_cookie = False
#     token = request.cookies.get('access_token', None)
#     if token:
#         async with async_session() as db:
#             if await users_table.check_user_by_token(session=db, token=token):
#                 url = '/user/main'
#             else:
#                 delete_cookie = True
#     response = RedirectResponse(url=url)
#     if delete_cookie:
#         response.delete_cookie('access_token')
#     return response
