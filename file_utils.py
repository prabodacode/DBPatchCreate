import os
import shutil


def create_folder_if_not_exists(path):
    folder = path if not path.endswith(".sql") else os.path.dirname(path)

    if folder:
        os.makedirs(folder, exist_ok=True)

def delete_folder_if_exists(folder_path):
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        shutil.rmtree(folder_path)
        print(f"delete_folder_if_exists, folder deleted. folder_path={folder_path}")


def find_block_in_files(folder_path, target_content):
    if not os.path.exists(folder_path):
        print("Path does not exist:", folder_path)
        return None

    for root, _, files in os.walk(folder_path):
        for file_name in sorted(files):
            file_path = os.path.join(root, file_name)

            with open(file_path, 'r', encoding='utf-8') as f:
                file_content = f.read()
                if target_content in file_content:
                    return file_path

    return None

def remove_first_block_from_file(file_path, block_to_remove):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove only the first occurrence
    updated_content = content.replace(block_to_remove, '', 1)

    # Optional: clean up extra newlines
    # updated_content = '\n'.join(line for line in updated_content.splitlines() if line.strip())

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

def is_file_empty(file_path):
    return os.path.isfile(file_path) and os.path.getsize(file_path) == 0

def is_file_blank(file_path):
    if not os.path.isfile(file_path):
        return False
    with open(file_path, 'r', encoding='utf-8') as f:
        return not f.read().strip()