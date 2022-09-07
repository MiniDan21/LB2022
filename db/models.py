from sqlalchemy.sql import func
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from .base import Base


class Team(Base):
    __tablename__ = 'teams'
    name = Column(String, primary_key=True)

    def __repr__(self):
        return 'Team_' + self.name


class User(Base):
    __tablename__ = 'users'

    id = Column(String, index=True, autoincrement=True)
    link = Column(String)
    login = Column(String, primary_key=True)
    password = Column(String)
    name = Column(String)
    surname = Column(String)
    group = Column(String)
    team_name = Column(String, nullable=True)

    def __repr__(self):
        return 'User_' + self.surname + '_' + self.name
