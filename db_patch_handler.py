import os
import re
import shutil

import yaml


def read_config_file():
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
    return config

def get_repo_name(brokerage):
    return r"sa_" + brokerage.lower() + r"_ntpdb"

def pre_populate(config_data, data_bean):
    pattern = r"DFNNTP-DB_SA_(\w+)_([\d\.]+)"
    match = re.search(pattern, data_bean.base_version)

    if match:
        brokerage = match.group(1)
        version = match.group(2)
        data_bean.brokerage = brokerage
        data_bean.version = version
    else:
        raise ValueError("Invalid format: Unable to extract brokerage and version.")

    data_bean.repo_name = get_repo_name(brokerage)  #sa_alkb_ntpdb
    data_bean.repo_path = os.path.join(data_bean.root_path, data_bean.repo_name)    #D:\GitDev\DB + \sa_alkb_ntpdb

    data_bean.patches_path = os.path.join(data_bean.repo_path, r"Database\Patches") #D:\GitDev\DB\sa_alkb_ntpdb + Database\Patches
    data_bean.base_patch_folder = os.path.join(data_bean.patches_path, data_bean.base_version)    #D:\GitDev\DB\sa_alkb_ntpdb\Database\Patches + \DFNNTP-DB_SA_ALKB_10.043.3.0

    data_bean.next_version = get_next_hotfix_version(data_bean.hotfix_type, data_bean.brokerage, data_bean.base_version)
    data_bean.next_hotfix_folder = os.path.join(data_bean.patches_path, data_bean.next_version)

def populate_configs(config_data, data_bean):
    data_bean.root_path = config_data["project"]["root_path"]
    data_bean.branch_name = config_data["project"]["branch_name"]
    data_bean.base_version = config_data["base_release"]["version"]

    data_bean.hotfix_type = config_data["hotfix_release"]["type"]

def get_next_hotfix_version(hotfix_type, brokerage, base_version_no):
    pattern = r"(\d+)\.(\d+)\.(\d+)\.(\d+)$"
    match = re.search(pattern, base_version_no)
    qa_hotfix_version = int(match.group(3))
    uat_hotfix_version = int(match.group(4))
    if match:
        if hotfix_type.upper() == "UAT":
            uat_hotfix_version += 1
        elif hotfix_type.upper() == "QA":
            qa_hotfix_version += 1

        #DFNNTP-DB_SA_ALKB_10.043.4.0
        return f"DFNNTP-DB_SA_{brokerage}_{match.group(1)}.{match.group(2)}.{qa_hotfix_version}.{uat_hotfix_version}"
    return None

def copy_base_patch_to_new_hotfix_folder(data_bean):
    shutil.copytree(data_bean.base_patch_folder, data_bean.next_hotfix_folder, dirs_exist_ok=True)



