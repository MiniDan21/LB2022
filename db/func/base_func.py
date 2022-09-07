from typing import TypeVar, Type, Optional, Dict
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from db.base import Base


ModelType = TypeVar("ModelType", bound=Base)


class BaseFunc:
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def create(self, session: AsyncSession, obj_model: ModelType) -> ModelType:
        session.add(obj_model)
        await session.commit()
        await session.refresh(obj_model)

        return obj_model

    async def get_all(self, session: AsyncSession):
        res = await session.execute(
            select(self.model)
        )
        return res.fetchall()
