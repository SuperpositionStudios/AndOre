from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Model
import config

# Connects to the database
engine = create_engine(config.path_to_database)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def save_model(mid, data):
    if session.query(Model).filter(Model.mid == mid).first() is None:
        session.add(Model(mid=mid, data=data))
        session.commit()
        return "Saved new model"
    else:
        session.query(Model).filter(Model.mid == mid).first().data = data
        session.commit()
        return "Updated existing model"


def retrieve_model(mid):
    if session.query(Model).filter(Model.mid == mid).first() is None:
        return None
    else:
        return session.query(Model).filter(Model.mid == mid).first().data


def clone_model(original_mid, clone_mid):
    original = retrieve_model(original_mid)
    if original is not None:
        save_model(clone_mid, original.data)
    else:
        return None
