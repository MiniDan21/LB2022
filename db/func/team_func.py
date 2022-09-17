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
        return res.name if res else None
