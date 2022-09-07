from fastapi import FastAPI, HTTPException, Depends, Response, Request, Cookie
from starlette.responses import RedirectResponse
from sqlalchemy.exc import IntegrityError
from db import async_engine, async_session, Base, users_table, teams_table, User, Team
from .auth import Auth
from .schemas import SignUpDetails, LoginDetails, AuthedCookie


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


@app.post('/signup', status_code=201)
async def signup(request: SignUpDetails):
    async with async_session() as db:
        details = request.dict()
        user = User(**details)
        if await users_table.check_user(session=db, login=user.login):
            return 'Такой пользователь уже есть'
        elif await users_table.check_login(session=db, login=user.login):
            return 'Такой логин уже занят'
        try:
            #  Создание юзера в таблице
            await users_table.create(session=db, obj_model=user)
            # Страница для ответа
            content = ''
            response = Response(content=content)
            response.set_cookie(key='access_token', value=auth.encode_token(request.login))
            return response
        except IntegrityError:
            return 'Этот никнейм уже занят!'


@app.post('/login', status_code=200)
async def login(request: LoginDetails):
    async with async_session() as db:
        if await users_table.check_login_and_password(session=db, login=request.login, password=request.password):
            content = ''
            response = Response(status_code=200, content=content)
            response.set_cookie('access_token', value=auth.encode_token(request.login))
            return response
        return 'Неправильный логин или пароль.'


@app.get('/logout', status_code=201)
async def logout(request: Request):
    response = RedirectResponse(url='/')
    response.delete_cookie('access_token')
    return response


@app.get('/test', status_code=200)
async def test(request: Cookie = Depends(auth.cookie_wrapper)):
    pass


@app.get('/', status_code=200)
async def main():
    return 'Main page'
