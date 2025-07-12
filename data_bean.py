from dataclasses import dataclass, field
from typing import Any, Optional, Dict


@dataclass
class DataBean:
    brokerage: str = ""
    root_path: str = ""
    branch_name: str = ""
    base_version: str = ""
    hotfix_type: str = ""

    brokerage: str = ""
    major_version: str = ""
    minor_version: str = ""
    uat_version: str = ""
    qa_version: str = ""

    repo_name: str = ""
    repo_path: str = ""

    patches_folder: str = ""
    base_patch_folder: str = ""

    hotfix_version: str = ""
    hotfix_folder: str = ""
    build_script_path: str = ""
    update_data_path: str = ""

    source_folder: str = ""

    build_script_map: Optional[Dict[str, Dict[str, int]]] = None
    update_data_map: Optional[Dict[str, Dict[str, int]]] = None

