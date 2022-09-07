from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData
from sqlalchemy import create_engine
from config import settings


DATABASE_URL = settings.sqlalchemy_url

async_engine = create_async_engine(DATABASE_URL, echo=False)
Base = declarative_base()


async_session = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)
