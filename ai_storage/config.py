import os


def path_to_this_files_directory():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return dir_path + '/'


def path_to_db():
    return 'sqlite:///' + str(path_to_this_files_directory()) + 'database.db'
