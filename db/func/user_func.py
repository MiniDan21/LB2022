from .base_func import *


class UsersTable(BaseFunc):
    async def check_id(self, session: AsyncSession, id: int):
        res = await session.execute(
            select(self.model).where(self.model.id == id)
        )
        res = res.scalar()
        return res

    async def check_login(self, session: AsyncSession, login: str):
        res = await session.execute(
            select(self.model).where(self.model.login == login)
        )
        res = res.scalar()
        return res

    async def check_login_and_password(self, session: AsyncSession, login: str, password: str):
        temp_row = await session.execute(
            select(self.model).where(self.model.password == password and self.model.login == login)
        )
        temp_row = temp_row.scalar()
        if temp_row:
            if temp_row.login == login and temp_row.password == password:
                return temp_row
        return False

    async def update_cookie(self, session: AsyncSession, updating_column: Dict, login: str):
        await session.execute(
            update(self.model).where(self.model.login == login).values(**updating_column)
        )
        await session.commit()

    async def make_captain(self, session: AsyncSession, login: str, demotion: bool = False):
        if demotion:
            await session.execute(
                update(self.model).where(self.model.login == login).value(captain=False)
            )
        else:
            await session.execute(
                update(self.model).where(self.model.login == login).values(captain=True)
            )
        await session.commit()

    async def delete_user_from_team(self, session: AsyncSession, login: str):
        await session.execute(
            update(self.model).where(self.model.login == login).values(team_id=None)
        )
        await session.commit()

    async def set_team_by_login(self, session: AsyncSession, login: str, team_id: int):
        res = await session.execute(
            update(self.model).where(self.model.login == login).values(team_id=team_id)
        )
        await session.commit()
        res = res.scalar()
        return res

    async def get_all_members(self, session: AsyncSession, team_id: int):
        res = await session.execute(
            select(self.model).where(self.model.team_id == team_id)
        )
        res.fetchall()
        return res
