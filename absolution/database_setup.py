from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import config

Base = declarative_base()


# The table for user accounts.
class Model(Base):
    __tablename__ = 'Model'
    id = Column(Integer, primary_key=True)
    mid = Column(String(), nullable=False)
    data = Column(String(), nullable=False)

# Create an engine that stores data in the local directory's
# database.db file.
engine = create_engine(config.path_to_db())

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)