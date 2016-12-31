from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, UserV2
import erebus_util
import config, uuid
from typing import Tuple
from datetime import datetime
import exceptions

# Connects to the database
engine = create_engine(config.path_to_db())
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
permissions = erebus_util.Permissions()


def create_user(username: str, password: str) -> Tuple[bool, str]:
	if session.query(UserV2).filter(UserV2.username == username).first() is not None:
		return False, "Username taken"
	aid = str(uuid.uuid4())
	hashed_password = erebus_util.encrypt_new_password(password)
	session.add(UserV2(aid=aid,
					 username=username,
					 hashed_password=hashed_password,
					 last_login=datetime.now(),
					 privilege_level=1
					 ))
	session.commit()
	return True, aid


def login(username: str, password: str) -> Tuple[bool, str]:
	stored_user = session.query(UserV2).filter(UserV2.username == username).first()
	if stored_user is None:
		return False, "username doesn't exist"
	stored_password = stored_user.hashed_password
	if erebus_util.encrypt_password(stored_password, password) == stored_password:
		update_last_login(stored_user.aid)
		return True, stored_user.aid
	else:
		return False, "wrong password"


def valid_aid(aid: str) -> bool:
	stored_user = session.query(UserV2).filter(UserV2.aid == aid).first()
	return stored_user is not None


def get_username(aid: str) -> str:
	row = session.query(UserV2).filter(UserV2.aid == aid).first()
	if row is not None:
		return row.username
	else:
		raise exceptions.InvalidAid(aid)


def get_privilege(aid: str) -> dict:
	row = session.query(UserV2).filter(UserV2.aid == aid).first()
	if row is not None:
		row = row  # type: UserV2
		return permissions.privilege(row.privilege_level)
	else:
		raise exceptions.InvalidAid(aid)


def update_last_login(aid: str) -> None:
	user = session.query(UserV2).filter(UserV2.aid == aid).first()
	if user is not None:
		user.last_login = datetime.now()
		session.commit()
