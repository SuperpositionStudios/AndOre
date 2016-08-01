johns_path_to_database = 'sqlite:////home/jcharante/Projects/AndOre/AndOre/ai_storage/database.db'
production_path_to_database = 'sqlite:////home/andore/AndOre/ai_storage/database.db'
developing = False


def path_to_db():
    if developing:
        return johns_path_to_database
    else:
        return production_path_to_database
