import re
import shutil

import yaml

import file_utils
from BlockStatus import BlockStatus
from file_utils import *
from sql_utils import *

def clean_temporary_files():
    delete_folder_if_exists('output')
    delete_folder_if_exists('temp')
    delete_folder_if_exists('source_validation')
    delete_folder_if_exists('validation')
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

def copy_patch_template_to_new_hotfix_folder(data_bean):
    template_folder = os.path.join(data_bean.patches_folder, "PatchTemplate")
    shutil.copytree(template_folder, data_bean.hotfix_folder, dirs_exist_ok=True)

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



def read_temp_folder(data_bean):
    sql_files = [f for f in os.listdir('temp') if f.endswith(".sql")]
    data_bean.hotfix_folder="output"
    build_script_path = os.path.join(data_bean.hotfix_folder + f"/02 New DB Release/Build-Scripts")
    update_data_path = os.path.join(data_bean.hotfix_folder + f"/02 New DB Release/UpdateData")

    for sql_file in sql_files:
        input_file = os.path.join('temp', sql_file)
        blocks = read_blocks_from_file(input_file)

        for i, block in enumerate(blocks, 1):
            if block is None:
                continue

            dml_info = is_dml_block(i, block)
            if dml_info:
                dml_type, schema, table = dml_info
                file_utils.create_folder_if_not_exists(os.path.join(update_data_path + f"/{schema}/data"))
                with open(update_data_path + f"/{schema}/data/{schema}.data_fixes.data.sql", "a") as output_file:
                    output_file.write(block)

            ddl_info = is_ddl_block(i, block)
            if ddl_info:
                file_utils.create_folder_if_not_exists(os.path.join(build_script_path))
                ddl_type, object_type, schema, db_object = ddl_info
                file_utils.create_folder_if_not_exists(os.path.join(build_script_path + f"/{schema}/{object_type}s"))
                file_suffix = get_file_suffix(object_type)
                with open(build_script_path + f"/{schema}/{object_type}s/{schema}.{db_object}.{file_suffix}.sql", "a") as output_file:
                    output_file.write(block)

            plsql_info = is_plsql_ddl_block(i, block)
            if plsql_info:
                file_utils.create_folder_if_not_exists(os.path.join(build_script_path))
                ddl_type, object_type, schema, db_object = plsql_info
                file_utils.create_folder_if_not_exists(os.path.join(build_script_path + f"/{schema}/{object_type}s"))
                file_suffix = get_file_suffix(object_type)
                with open(build_script_path + f"/{schema}/{object_type}s/{schema}.{db_object}.{file_suffix}.sql", "a") as output_file:
                    output_file.write(block)
            else:
                plsql_block_info = is_plsql_block_(i, block)
                if plsql_block_info:
                    start, schema, end = plsql_block_info
                    file_utils.create_folder_if_not_exists(os.path.join(update_data_path + f"/{schema}/data"))
                    with open(update_data_path + f"/{schema}/data/{schema}.data_fixes.data.sql", "a") as output_file:
                        output_file.write(block)
    return True

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
    blocks = [block.strip() if block.strip() else None for block in content.split('\n--END--\n') if block.strip()]
    return blocks

#############################
def source_validation(data_bean):
    shutil.copytree('source', 'source_validation',dirs_exist_ok=True)
    sql_files = [f for f in os.listdir('temp') if f.endswith(".sql")]

    status = True
    for sql_file in sql_files:
        input_file = os.path.join('temp', sql_file)
        validation_file = os.path.join('source_validation', sql_file.removeprefix('temp_'))
        blocks = read_blocks_from_file(input_file)
        for i, block in enumerate(blocks, 1):
            file_1 = find_block_in_files('source_validation', block)
            if file_1:
                print(f"source_validation, block found, :sql_file={sql_file},i={i}, destination_file={file_1}")
                remove_first_block_from_file(validation_file, block)

        if(is_file_empty(validation_file) or is_file_blank(validation_file)):
            print(f"LN:269, source_validation success for file={validation_file}")
        else:
            print(f"LN:272, source_validation failed for file={validation_file}")
            status = False

    if(status):
        print(f"LN:276, =====source_validation successful=====")

    return status

#############################
def validation(data_bean):
    shutil.copytree('temp', 'validation',dirs_exist_ok=True)
    sql_files = [f for f in os.listdir('temp') if f.endswith(".sql")]
    data_bean.hotfix_folder="output"
    output_path = os.path.join(data_bean.hotfix_folder , "02 New DB Release")

    for sql_file in sql_files:
        input_file = os.path.join('temp', sql_file)
        validation_file = os.path.join('validation', sql_file)
        blocks = read_blocks_from_file(input_file)
        for i, block in enumerate(blocks, 1):
            file_1 = find_block_in_files(output_path, block)
            if file_1:
                print(f"File found, :sql_file={sql_file},i={i}, destination_file={file_1}")
                remove_first_block_from_file(validation_file, block)

    return True
