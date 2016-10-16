from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import config

Base = declarative_base()


# The table for user accounts.
class User(Base):
    __tablename__ = 'Users'
    pk = Column(Integer, primary_key=True)
    aid = Column(String())
    game_id = Column(String())
    username = Column(String())
    hashed_password = Column(String())
    last_login = Column(DateTime)

# Create an engine that stores data in the local directory's
# database.db file.
engine = create_engine(config.path_to_db())

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
