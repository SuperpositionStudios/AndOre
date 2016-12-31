from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, UserV2
import config

# Connects to the database
engine = create_engine(config.path_to_db())
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

Base.metadata.create_all(engine)

print("Updating User Tables from User to UserV2...\n")

for row in session.query(User).all():
	row = row  # type: User

	if session.query(UserV2).filter(UserV2.username == row.username).first() is None:
		print("Transferring {}".format(row.username))
		session.add(UserV2(aid=row.aid,
						   username=row.username,
						   hashed_password=row.hashed_password,
						   last_login=row.last_login,
						   privilege_level=row.privilege
						   ))

session.commit()
