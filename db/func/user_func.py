from .base_func import *


class UsersTable(BaseFunc):
    async def check_user(self, session: AsyncSession, login: str = None):
        res = await session.execute(
            select(self.model).where(self.model.login == login)
        )
        return True if res.scalar() else False

    async def check_login(self, session: AsyncSession, login: str):
        res = await session.execute(
            select(self.model).where(self.model.login == login)
        )
        res = res.scalar()
        return res if res else False

    async def check_login_and_password(self, session: AsyncSession, login: str, password: str):
        temp_row = await session.execute(
            select(self.model).where(self.model.password == password and self.model.login == login)
        )
        temp_row = temp_row.scalar()
        if temp_row:
            if temp_row.login == login and temp_row.password == password:
                return True
        return False
