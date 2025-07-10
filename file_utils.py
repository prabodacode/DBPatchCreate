import os


def create_folder_if_not_exists(path):
    folder = path if not path.endswith(".sql") else os.path.dirname(path)

    if folder:
        os.makedirs(folder, exist_ok=True)


def find_block_in_files(folder_path, content):
    files = sorted(
        [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    )
    for file_name in files:
        file_path = os.path.join(folder_path, file_name)

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if content in content:
                return file_name, content

    return None, None
