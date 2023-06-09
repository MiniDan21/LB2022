from sqlalchemy.sql import func
from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Boolean, PickleType
from sqlalchemy.orm import relationship
from sqlalchemy.ext.mutable import MutableDict
from .base import Base
from config import settings


class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    amount_of_members = Column(Integer, default=0)
    points = Column(Integer, default=0)
    invitation_code = Column(String, unique=True)
    missed_tasks = Column(Integer, default=0)
    completed_tasks = Column(Integer, default=0)

    def __repr__(self):
        return 'Team_' + self.name + '_' + self.invitation_code

    # @property
    # def data(self):
    #     return {
    #         'id': self.id,
    #         'name': self.name,
    #         'amount_of_members': self.amount_of_members,
    #         'points': self.points,
    #         'invatation_code': self.invitation_code
    #     }


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    vk_ref = Column(String)
    login = Column(String, unique=True)
    password = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    group_number = Column(String)
    team_id = Column(Integer, nullable=True, default=None)
    captain = Column(Boolean, default=False)

    def __repr__(self):
        return 'User_' + self.surname + '_' + self.name + '_' + self.team_id

    @property
    def data(self):
        return {
            'id': self.id,
            'vk_ref': self.vk_ref,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'group_number': self.group_number,
            'team_id': self.team_id,
            'captain': self.captain
        }
