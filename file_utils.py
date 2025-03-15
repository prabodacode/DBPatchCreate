import os

def validate_folder(folder_path):
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        raise FileNotFoundError(f"Folder does not exist: {folder_path}")
