paths_to_databases = {
    'hal': 'sqlite:////Users/hlarsson/repos/AndOre/ai_storage/database.db',
    'john': 'sqlite:////home/jcharante/Projects/AndOre/ai_storage/database.db',
    'production': 'sqlite:////home/andore/AndOre/ai_storage/database.db'
}

user = 'john'  # THIS HAS TO BE CHANGED TO PRODUCTION BEFORE CREATING A PULL REQUEST


def path_to_db():
    return paths_to_databases[user]
