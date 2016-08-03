johns_path_to_database = 'sqlite:////Users/hlarsson/repos/AndOre/AndOre/ai_storage/database.db'
production_path_to_database = 'sqlite:////home/andore/AndOre/ai_storage/database.db'
developing = True


def path_to_db():
    if developing:
        return johns_path_to_database
    else:
        return production_path_to_database
