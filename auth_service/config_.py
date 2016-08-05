paths_to_databases = {
    'hal': 'sqlite:////Users/hlarsson/repos/AndOre/auth_service/database.db',
    'john': 'sqlite:////home/jcharante/Projects/AndOre/AndOre/auth_service/database.db',
    'production': 'sqlite:////home/andore/AndOre/auth_service/database.db'
}

user = 'john'  # change this


def path_to_db():
    return paths_to_databases[user]
