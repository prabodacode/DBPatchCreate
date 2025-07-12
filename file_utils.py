import os, re
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

def is_empty_file_folder(folder_path):
    if not os.path.exists(folder_path):
        print("Path does not exist:", folder_path)
        return False

    status = True
    for root, _, files in os.walk(folder_path):
        for file_name in sorted(files):
            file_path = os.path.join(root, file_name)

            if (is_file_empty(file_path) or is_file_blank(file_path)):
                print(f"LN:66, is_empty_file_folder success for file={file_path}")
            else:
                print(f"LN:69, is_empty_file_folder failed for file={file_path}")
                status = False

    return status

def create_file_if_not_exists(new_file_name, template_file_name=None, tags=None):
    if not os.path.exists(new_file_name):
        os.makedirs(os.path.dirname(new_file_name), exist_ok=True)
        if template_file_name and os.path.exists(template_file_name):
            with open(template_file_name, 'r', encoding='utf-8') as f:
                content = f.read()

            # Replace tag placeholders
            if tags:
                for tag, value in tags.items():
                    content = content.replace(tag, value)

            with open(new_file_name, 'w', encoding='utf-8') as f:
                f.write(content)

def insert_before_search_string(file_path, search_string, lines_to_insert):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Normalize lines to compare ignoring whitespace
    existing_line_set = set(line.strip() for line in lines)
    insert_line_set = set(line.strip() for line in lines_to_insert)

    # Filter out lines already present
    missing_lines = [line for line in lines_to_insert if line.strip() not in existing_line_set]
    if not missing_lines:
        return  # Nothing to insert

    # Find insertion point
    for i, line in enumerate(lines):
        if line.strip().lower() == search_string.lower():
            # Ensure newlines
            insert_lines = [l if l.endswith('\n') else l + '\n' for l in missing_lines]
            lines[i:i] = insert_lines
            break

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def get_sql_files_starting_with(folder_path, start_string):
    pattern = re.compile(rf'^{re.escape(start_string)}.*\.sql$', re.IGNORECASE)

    matching_files = [
        f for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f)) and pattern.match(f)
    ]

    return matching_files

def get_first_sql_file_starting_with(folder_path, start_string):
    matching_files = get_sql_files_starting_with(folder_path, start_string)
    return matching_files[0] if matching_files else None