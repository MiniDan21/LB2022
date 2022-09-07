from .base import async_engine, async_session, Base
from .models import User, Team
from .func import TeamsTable, UsersTable


users_table = UsersTable(User)
teams_table = TeamsTable(Team)
