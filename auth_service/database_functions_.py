from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup_ import Base, User
import helper_functions_
import config_, uuid

# Connects to the database
engine = create_engine(config_.path_to_db())
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def create_user(username, password):
    if session.query(User).filter(User.username == username).first() is not None:
        return False, "Username taken"
    uid = str(uuid.uuid4())
    hashed_password = helper_functions_.encrypt_new_password(password)
    session.add(User(uid=uid,
                     game_id='',
                     username=username,
                     password=hashed_password
                     ))
    return True, uid


def login(username, password):
    stored_user = session.query(User).filter(User.username == username).first()
    if stored_user is None:
        return False, "username doesn't exist"
    stored_password = stored_user.hashed_password
    if helper_functions_.encrypt_password(stored_password, password) == stored_password:
        return True, stored_user.uid
    else:
        return False, "wrong password"


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
