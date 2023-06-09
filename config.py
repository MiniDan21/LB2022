from random import choice
from pydantic import BaseSettings


class Settings(BaseSettings):
    FastApi_secret: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRESQL_HOST: str

    @property
    def sqlalchemy_url(self):
        return (
            'postgresql+asyncpg://'
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRESQL_HOST}/{self.POSTGRES_DB}"
        )

    @property
    def invitation_code(self):
        char = lambda: chr(choice([i for i in range(65, 91)] + [j for j in range(97, 123)]))
        return '22' + char() + char() + char() + char() + 'LB'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


settings = Settings()
