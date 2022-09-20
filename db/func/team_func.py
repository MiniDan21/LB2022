import logging

from .base_func import *


class TeamsTable(BaseFunc):
    async def check_name(self, session: AsyncSession, name: str):
        res = await session.execute(
            select(self.model).where(self.model.name == name)
        )
        res = res.scalar()
        return res

    async def check_by_code(self, session: AsyncSession, code: str):
        res = await session.execute(
            select(self.model).where(self.model.invitation_code == code)
        )
        res = res.scalar()
        return res

    async def check_team_id(self, session: AsyncSession, team_id: int):
        res = await session.execute(
            select(self.model).where(self.model.id == team_id)
        )
        res = res.scalar()
        return res

    async def change_amount(self, session: AsyncSession, team_id: int, current_amount: int):
        await session.execute(
            update(self.model).where(self.model.id == team_id).values(amount_of_members=current_amount)
        )
        await session.commit()

    async def del_team(self, session: AsyncSession, team_id: int):
        expr = delete(self.model).where(self.model.id == team_id)
        await session.execute(
            expr
        )
        await session.commit()
