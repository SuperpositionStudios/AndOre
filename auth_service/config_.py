paths_to_databases = {
    'hal': 'sqlite:////Users/hlarsson/repos/AndOre/auth_service/database.db',
    'john': 'sqlite:////home/jcharante/Projects/AndOre/auth_service/database.db',
    'production': 'sqlite:////home/andore/AndOre/auth_service/database.db'
}

paths_to_game_server = {
    'john': 'http://localhost:7100',
    'production': 'http://localhost:7100'
# It's localhost for now, but in the future they may be hosted on seperate servers
}

user = 'john'  # THIS HAS TO BE SET BACK TO PRODUCTION BEFORE MAKING YOUR PULL REQUEST I SWEAR TO RNGESUS


def path_to_db():
    return paths_to_databases[user]


def game_server_url():
    return paths_to_game_server[user]
