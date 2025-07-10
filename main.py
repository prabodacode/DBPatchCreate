import os
import sys

from data_bean import *
from db_patch_handler import *
from git_utils import *




if __name__ == "__main__":
    # sys.exit(0);
    clean_temporary_files()
    config_data = read_config_file()
    data_bean = DataBean()

    populate_configs(config_data, data_bean)
    pre_populate(config_data, data_bean)

    # git_checkout_and_pull(data_bean.branch_name, data_bean.repo_path)
    copy_patch_template_to_new_hotfix_folder(data_bean)
    read_source_folder(data_bean.source_folder)
    source_validation(data_bean)
    read_temp_folder(data_bean)
    # validation(data_bean)
    i=10

    # create_next_hotfix_folder_from_base_patch(base_patch_folder, next_hotfix_folder)
    #
    # # ----------------------------
    # source_repo_path = r"D:\GitDev\OMS\v3\sa_x_ntpoms"
    # source_branch_name = "DFNNTPOMS_X_SA_3.029.00.0-hotfix"  # Replace with the branch you want to check out
    # # checkout_branch(source_repo_path, source_branch_name)
    #
    # source_scripts_path = r"D:\GitDev\OMS\v3\sa_x_ntpoms\hotfix_db_changes"
    # create_patch_files(source_scripts_path, next_hotfix_folder, base_patch_folder)
    # add_to_git(next_hotfix_folder)