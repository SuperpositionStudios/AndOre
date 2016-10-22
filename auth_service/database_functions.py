from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User
import helper_functions
import config, uuid
from typing import Tuple
from datetime import datetime

# Connects to the database
engine = create_engine(config.path_to_db())
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def create_user(username, password):
    if session.query(User).filter(User.username == username).first() is not None:
        return False, "Username taken"
    aid = str(uuid.uuid4())
    hashed_password = helper_functions.encrypt_new_password(password)
    session.add(User(aid=aid,
                     game_id='',
                     username=username,
                     hashed_password=hashed_password,
                     last_login=datetime.now(),
                     privilege="player"
                     ))
    session.commit()
    return True, aid


def login(username, password):
    stored_user = session.query(User).filter(User.username == username).first()
    if stored_user is None:
        return False, "username doesn't exist"
    stored_password = stored_user.hashed_password
    if helper_functions.encrypt_password(stored_password, password) == stored_password:
        update_last_login(stored_user.aid)
        return True, stored_user.aid
    else:
        return False, "wrong password"


def valid_aid(aid):
    stored_user = session.query(User).filter(User.aid == aid).first()
    return stored_user is not None


def update_game_id(aid, new_game_id):
    stored_user = session.query(User).filter(User.aid == aid).first()
    if stored_user is None:
        return False, "aid doesn't exist"
    stored_user.game_id = new_game_id
    session.commit()
    return True, "game_id updated"


def get_game_id(aid):
    stored_user = session.query(User).filter(User.aid == aid).first()
    if stored_user is None:
        return False, "aid doesn't exist"
    return True, stored_user.game_id


def get_username_from_aid(aid: str) -> Tuple[bool, str]:
    row = session.query(User).filter(User.aid == aid).first()
    if row is not None:
        return True, row.username
    else:
        return False, ''


def update_last_login(aid):
    user = session.query(User).filter(User.aid == aid).first()
    if user is not None:
        user.last_login = datetime.now()
        session.commit()
