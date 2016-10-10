from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup_ import Base, User
import helper_functions_
import config, uuid
from typing import Tuple

# Connects to the database
engine = create_engine(config.path_to_db())
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def create_user(username, password):
    if session.query(User).filter(User.username == username).first() is not None:
        return False, "Username taken"
    aid = str(uuid.uuid4())
    hashed_password = helper_functions_.encrypt_new_password(password)
    session.add(User(uid=aid,
                     game_id='',
                     username=username,
                     hashed_password=hashed_password
                     ))
    session.commit()
    return True, aid


def login(username, password):
    stored_user = session.query(User).filter(User.username == username).first()
    if stored_user is None:
        return False, "username doesn't exist"
    stored_password = stored_user.hashed_password
    if helper_functions_.encrypt_password(stored_password, password) == stored_password:
        return True, stored_user.uid
    else:
        return False, "wrong password"


def valid_aid(aid):
    stored_user = session.query(User).filter(User.uid == aid).first()
    return stored_user is not None


def update_game_id(uid, new_game_id):
    stored_user = session.query(User).filter(User.uid == uid).first()
    if stored_user is None:
        return False, "uid doesn't exist"
    stored_user.game_id = new_game_id
    session.commit()
    return True, "uid updated"


def get_game_id(uid):
    stored_user = session.query(User).filter(User.uid == uid).first()
    if stored_user is None:
        return False, "uid doesn't exist"
    return True, stored_user.game_id


def get_username_from_aid(aid: str) -> Tuple[bool, str]:
    row = session.query(User).filter(User.uid == aid).first()
    if row is not None:
        return True, row.username
    else:
        return False, ''
