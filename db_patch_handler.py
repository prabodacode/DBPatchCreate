import re
import shutil
from collections import defaultdict

import yaml

import file_utils
from BlockStatus import BlockStatus
from file_utils import *
from sql_utils import *

def clean_temporary_files(data_bean):
    delete_folder_if_exists(data_bean.hotfix_folder)
    delete_folder_if_exists('temp')
    delete_folder_if_exists('source_validation')
    delete_folder_if_exists('patch_validation')
    return None

def read_config_file():
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config


def get_repo_name(brokerage):
    return r"sa_" + brokerage.lower() + r"_ntpdb"


def pre_populate(config_data, data_bean):
    pattern =  r"DFNNTP-DB_SA_(\w+)_(\d+)\.(\d+)\.(\d+)\.(\d+)$"
    match = re.search(pattern, data_bean.base_version)

    if match:
        data_bean.brokerage = str(match.group(1))
        data_bean.major_version = str(match.group(2))
        data_bean.minor_version = str(match.group(3))
        data_bean.qa_version = str(match.group(4))
        data_bean.uat_version = str(match.group(5))
    else:
        raise ValueError("Invalid format: Unable to extract brokerage and version.")

    data_bean.repo_name = get_repo_name(data_bean.brokerage)  # sa_alkb_ntpdb
    data_bean.repo_path = os.path.join(data_bean.root_path, data_bean.repo_name)  # D:\GitDev\DB + \sa_alkb_ntpdb

    data_bean.patches_folder = os.path.join(data_bean.repo_path,
                                            r"Database\Patches")  # D:\GitDev\DB\sa_alkb_ntpdb + Database\Patches
    data_bean.base_patch_folder = os.path.join(data_bean.patches_folder,
                                               data_bean.base_version)  # D:\GitDev\DB\sa_alkb_ntpdb\Database\Patches + \DFNNTP-DB_SA_ALKB_10.043.3.0

    set_next_hotfix_version(data_bean)


def populate_configs(config_data, data_bean):
    data_bean.root_path = config_data["project"]["root_path"]
    data_bean.branch_name = config_data["project"]["branch_name"]
    data_bean.base_version = config_data["base_release"]["base_version"]

    data_bean.hotfix_type = config_data["hotfix_release"]["hotfix_type"]
    data_bean.source_folder = config_data["scripts_source"]["source_folder"]

    print(f"LN:54, populate_configs, root_path={data_bean.root_path}"
          f"\nbranch_name={data_bean.branch_name}"
          f"\nbase_version={data_bean.base_version}"
          f"\nhotfix_type={data_bean.hotfix_type}"
          f"\nsource_folder={data_bean.source_folder}")


def set_next_hotfix_version(data_bean):
    qa_hotfix_version = data_bean.qa_version
    uat_hotfix_version = data_bean.uat_version

    if data_bean.hotfix_type.upper() == "QA":
        qa_hotfix_version = str(int(qa_hotfix_version) + 1).zfill(len(qa_hotfix_version))
        uat_hotfix_version = 0
    elif data_bean.hotfix_type.upper() == "UAT":
        uat_hotfix_version = str(int(uat_hotfix_version) + 1).zfill(len(uat_hotfix_version))

        # DFNNTP-DB_SA_ALKB_10.043.4.0
    data_bean.hotfix_version = f"DFNNTP-DB_SA_{data_bean.brokerage}_{data_bean.major_version}.{data_bean.minor_version}.{qa_hotfix_version}.{uat_hotfix_version}"
    print(f"LN:66, set_next_hotfix_version, hotfix_version={data_bean.hotfix_version}")
    data_bean.hotfix_folder = os.path.join(data_bean.patches_folder, data_bean.hotfix_version)
    # data_bean.hotfix_folder='patch' #temp change

    data_bean.build_script_path = os.path.join(data_bean.hotfix_folder + f"/02 New DB Release/Build-Scripts")
    data_bean.update_data_path = os.path.join(data_bean.hotfix_folder + f"/02 New DB Release/UpdateData")

def copy_patch_template_folder_structure_to_new_hotfix_folder(data_bean):
    template_folder = os.path.join(data_bean.patches_folder, "PatchTemplate")
    destination_folder = data_bean.hotfix_folder

    for root, dirs, _ in os.walk(template_folder):
        # Construct the relative path from the template folder
        rel_path = os.path.relpath(root, template_folder)
        # Target directory path in destination
        target_dir = os.path.join(destination_folder, rel_path)
        os.makedirs(target_dir, exist_ok=True)

def add_additional_files(data_bean):
    template_folder = os.path.join(data_bean.patches_folder, "PatchTemplate")
    destination_folder = data_bean.hotfix_folder

    for root, _, files in os.walk(template_folder):
        rel_path = os.path.relpath(root, template_folder)
        dest_dir = os.path.join(destination_folder, rel_path)

        for file_name in files:
            src_file = os.path.join(root, file_name)
            dest_file = os.path.join(dest_dir, file_name)

            if not os.path.exists(dest_file):
                os.makedirs(dest_dir, exist_ok=True)  # In case folder was skipped earlier
                shutil.copy2(src_file, dest_file)

def read_source_folder(source_folder):
    sql_files = [f for f in os.listdir(source_folder) if f.endswith(".sql")]
    for sql_file in sql_files:
        input_file = os.path.join(source_folder, sql_file)
        output_temp_file = os.path.join('temp', f"temp_{sql_file}")
        process_sql_file_and_add_end_markers(input_file, output_temp_file)

    return True

def process_sql_file_and_add_end_markers(input_f, output_f):
    file_utils.create_folder_if_not_exists(output_f)

    with open(input_f, "r") as file, open(output_f, "w") as output_file:
        status = BlockStatus()

        for line_number, line in enumerate(file, start=1):
            # Detect start of a CREATE object (like PROCEDURE, FUNCTION, PACKAGE)
            if not (status.is_ddl_block or status.is_plsql_block):
                ddl_info = is_ddl_start_line(line_number, line)
                if ddl_info:
                    output_file.write("\n--END--\n")
                    ddl_type, object_type, schema, db_object = ddl_info
                    status.set_is_ddl_block()
                    output_file.write(line)
                    continue

            # If we are inside a CREATE object block
            if status.is_ddl_block:
                output_file.write(line)

                # Detect end of the object using '/' in a separate line
                if is_slash_line(line_number, line):
                    status.reset()
                continue

            # Skip block detection if we're inside a CREATE PROCEDURE/FUNCTION etc.
            if not (status.is_ddl_block or status.is_plsql_block):
                is_block_start, block_type = is_plsql_block_start_line(line_number, line)
                if is_block_start:
                    output_file.write("\n--END--\n")
                    if block_type == 'DECLARE':
                        if status.block_depth == 0:
                            status.set_is_plsql_block()
                        status.increase_block_depth(block_type)

                    elif block_type == 'BEGIN':
                        if status.block_depth == 0:
                            status.set_is_plsql_block()
                            status.increase_block_depth(block_type)
                        elif status.block_depth > 0:
                            if status.block_stack[-1] == 'DECLARE':
                                status.update_stack('DECLARE_BEGIN')
                            elif status.block_stack[-1] == 'DECLARE_BEGIN' or status.block_stack[-1] == 'BEGIN':
                                status.increase_block_depth(block_type)
                    output_file.write(line)
                    continue

            # Handle block end
            if status.is_ddl_block and status.block_depth > 0:
                output_file.write(line)
                if is_block_end_line(line_number, line):
                    status.decrease_block_depth()
                continue

            if not status.is_ddl_block and not status.is_plsql_block:
                # Process DML statements
                dml_info = is_dml_start_line(line_number, line)
                if dml_info:
                    output_file.write("\n--END--\n")
                    status.set_is_dml_block()
                    dml_type, schema, table = dml_info
                    output_file.write(line)
                    continue

            # Handle / statements
            if is_slash_line(line_number, line):
                status.reset()
                inside_create_object = False
                output_file.write(line)
                continue

            if status.is_dml_block and is_commit_line(line_number, line):
                status.reset()
                output_file.write(line)
                continue

            # Write other lines as they are
            output_file.write(line)

        # Final end marker
        output_file.write("\n--END--\n")


def populate_build_script_master_file(data_bean):
    lines_to_insert = []

    for schema, types in data_bean.build_script_map.items():
        for obj_type in types:
            if types.get(obj_type, 0) > 0:
                matching_files = file_utils.get_sql_files_starting_with(f"{data_bean.build_script_path}/{schema}/{obj_type}s", f"run.")
                for file_name in matching_files:
                    lines_to_insert.append(f"@@./{file_name}")

        master_file_name = data_bean.build_script_path + f"/{schema}/master.sql"
        insert_before_search_string(master_file_name, "exit", lines_to_insert)
    return lines_to_insert

def populate_update_data_master_file(data_bean):
    lines_to_insert = []

    for schema, types in data_bean.update_data_map.items():
        for obj_type in types:
            if types.get(obj_type, 0) > 0:
                matching_files = file_utils.get_sql_files_starting_with(f"{data_bean.update_data_path}/{schema}/{obj_type}", f"run.")
                for file_name in matching_files:
                    lines_to_insert.append(f"@@./{file_name}")

        update_file_name = data_bean.update_data_path + f"/{schema}/update.sql"
        insert_before_search_string(update_file_name, "exit", lines_to_insert)
    return lines_to_insert

def repopulate_update_data_run_files(data_bean):
    lines_to_insert = []

    for schema, types in data_bean.update_data_map.items():
        for obj_type in types:
            if types.get(obj_type, 0) > 0:
                run_file_name = file_utils.get_first_sql_file_starting_with(f"{data_bean.update_data_path}/{schema}/{obj_type}", f"run.")
                matching_files = file_utils.get_sql_files_starting_with(f"{data_bean.update_data_path}/{schema}/{obj_type}", f"{schema}.")
                for file_name in matching_files:
                    lines_to_insert.append(f"@@{file_name}")

                run_file_name = data_bean.update_data_path + f"/{schema}/{obj_type}/{run_file_name}"
                insert_before_search_string(run_file_name, "spool off", lines_to_insert)
    return lines_to_insert



def read_temp_folder(data_bean):
    sql_files = [f for f in os.listdir('temp') if f.endswith(".sql")]

    build_script_map = defaultdict(lambda: {
        "table": 0,
        "procedure": 0,
        "package": 0,
        "trigger": 0,
        "view": 0
    })
    update_data_map = defaultdict(lambda: {
        "data": 0
    })

    for sql_file in sql_files:
        input_file = os.path.join('temp', sql_file)
        blocks = read_blocks_from_file(input_file)

        for i, block in enumerate(blocks, 1):
            if block is None:
                continue

            dml_info = is_dml_block(i, block)
            if dml_info:
                dml_type, schema, table = dml_info
                file_utils.create_folder_if_not_exists(os.path.join(data_bean.update_data_path + f"/{schema}/data"))
                file_name = f"{schema}.data_fixes.data.sql"
                with open(data_bean.update_data_path + f"/{schema}/data/{file_name}", "a") as output_file:
                    output_file.write(block)

                create_update_data_run_files(data_bean, file_name, schema)
                update_file_create(data_bean, schema)
                update_data_map[f"{schema}"][f"data"] = 1

            ddl_info = is_ddl_block(i, block)
            if ddl_info:
                file_utils.create_folder_if_not_exists(os.path.join(data_bean.build_script_path))
                ddl_type, object_type, schema, db_object = ddl_info
                file_utils.create_folder_if_not_exists(os.path.join(data_bean.build_script_path + f"/{schema}/{object_type}s"))
                file_suffix = get_file_suffix(object_type)
                file_name = f"{schema}.{db_object}.{file_suffix}.sql"
                with open(data_bean.build_script_path + f"/{schema}/{object_type}s/{file_name}", "a") as output_file:
                    output_file.write(block)

                create_build_script_run_files(data_bean, file_name, object_type, schema)
                master_file_create(data_bean, schema)
                build_script_map[f"{schema}"][f"{object_type}"] = 1

            plsql_info = is_plsql_ddl_block(i, block)
            if plsql_info:
                file_utils.create_folder_if_not_exists(os.path.join(data_bean.build_script_path))
                ddl_type, object_type, schema, db_object = plsql_info
                file_utils.create_folder_if_not_exists(os.path.join(data_bean.build_script_path + f"/{schema}/{object_type}s"))
                file_suffix = get_file_suffix(object_type)
                file_name = f"{schema}.{db_object}.{file_suffix}.sql"
                with open(data_bean.build_script_path + f"/{schema}/{object_type}s/{file_name}", "a") as output_file:
                    output_file.write(block)

                create_build_script_run_files(data_bean, file_name, object_type, schema)
                master_file_create(data_bean, schema)
                build_script_map[f"{schema}"][f"{object_type}"] = 1
            else:
                plsql_block_info = is_plsql_block_(i, block)
                if plsql_block_info:
                    start, schema, end = plsql_block_info
                    file_utils.create_folder_if_not_exists(os.path.join(data_bean.update_data_path + f"/{schema}/data"))
                    file_name = f"{schema}.data_fixes.data.sql"
                    with open(data_bean.update_data_path + f"/{schema}/data/{file_name}", "a") as output_file:
                        output_file.write(block)

                    create_update_data_run_files(data_bean, file_name, schema)
                    update_file_create(data_bean, schema)
                    update_data_map[f"{schema}"][f"data"] = 1

    data_bean.build_script_map = build_script_map
    data_bean.update_data_map = update_data_map
    return True


def create_build_script_run_files(data_bean, file_name, object_type, schema):
    run_file_name = data_bean.build_script_path + f"/{schema}/{object_type}s/run.{schema}.{object_type}s.sql"
    tags = {"[#SCHEMA]": f"{schema}", "[#OBJECT_TYPE]": f"{object_type}s"}
    file_utils.create_file_if_not_exists(run_file_name, f"templates/run_file_template.sql",
                                         tags)
    run_file_line = [f"@@{file_name}"]
    file_utils.insert_before_search_string(run_file_name, "spool off", run_file_line)

def create_update_data_run_files(data_bean, file_name, schema):
    run_file_name = data_bean.update_data_path + f"/{schema}/data/run.{schema}.data.sql"
    tags = {"[#SCHEMA]": f"{schema}", "[#OBJECT_TYPE]": f"data"}
    file_utils.create_file_if_not_exists(run_file_name, f"templates/run_file_template.sql",
                                         tags)
    run_file_line = [f"@@{file_name}"]
    file_utils.insert_before_search_string(run_file_name, "spool off", run_file_line)


def master_file_create(data_bean, schema):
    master_file_name = data_bean.build_script_path + f"/{schema}/master.sql"
    file_utils.create_file_if_not_exists(master_file_name, f"templates/master_file_template.sql",None)

def update_file_create(data_bean, schema):
    master_file_name = data_bean.update_data_path + f"/{schema}/update.sql"
    file_utils.create_file_if_not_exists(master_file_name, f"templates/master_file_template.sql",None)

def get_file_suffix(object_type):
    match object_type:
        case "table":
            return "tab"
        case "procedure":
            return "proc"
        case "package":
            return "pkg"
        case "trigger":
            return "trig"
        case "view":
            return "view"
        case "function":
            return "func"
        case _:
            return "unknown"


def read_blocks_from_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Split the content into blocks using the tag "--END--"
    blocks = [block if block.strip() else None for block in content.split('\n--END--\n') if block.strip()]
    return blocks

#############################
def source_validation(data_bean):
    shutil.copytree('source', 'source_validation',dirs_exist_ok=True)
    sql_files = [f for f in os.listdir('temp') if f.endswith(".sql")]

    for sql_file in sql_files:
        input_file = os.path.join('temp', sql_file)
        blocks = read_blocks_from_file(input_file)
        for i, block in enumerate(blocks, 1):
            file_1 = find_block_in_files('source_validation', block)
            if file_1:
                print(f"source_validation, block found, :sql_file={sql_file},i={i}, destination_file={file_1}")
                remove_first_block_from_file(file_1, block)

    status = is_empty_file_folder('source_validation')

    if(status):
        print(f"LN:276, =====source_validation successful=====")

    return status

#############################
def patch_validation(data_bean):
    patch_folder = os.path.join(data_bean.hotfix_folder, f"02 New DB Release")
    shutil.copytree(patch_folder, 'patch_validation',dirs_exist_ok=True)
    sql_files = [f for f in os.listdir('temp') if f.endswith(".sql")]

    for sql_file in sql_files:
        input_file = os.path.join('temp', sql_file)
        blocks = read_blocks_from_file(input_file)
        for i, block in enumerate(blocks, 1):
            file_1 = find_block_in_files('patch_validation', block)
            if file_1:
                print(f"patch_validation, block found, :sql_file={sql_file}, i={i}, destination_file={file_1}")
                remove_first_block_from_file(file_1, block)

    status = is_empty_file_folder('patch_validation')

    if(status):
        print(f"LN:291, =====patch_validation successful=====")

    return status

def populate_master_files(data_bean):
    populate_build_script_master_file(data_bean)
    populate_update_data_master_file(data_bean)
    return True