import os

def create_folder_if_not_exists(path):
    folder = path if not path.endswith(".sql") else os.path.dirname(path)

    if folder:
        os.makedirs(folder, exist_ok=True)