from dataclasses import dataclass, field
from typing import List


@dataclass
class BlockStatus:
    is_dml_block: bool = False
    is_ddl_block: bool = False
    is_plsql_block: bool = False
    block_stack: List[str] = field(default_factory=list)
    block_depth: int = 0
    current_sql_type: str = ""

    def reset(self):
        self.is_plsql_block = False
        self.block_depth = 0
        self.block_stack = []
        self.is_ddl_block = False
        self.is_dml_block = False

    def set_is_plsql_block(self):
        self.is_plsql_block = True
        self.block_depth = 0
        self.block_stack = []
        self.is_ddl_block = False
        self.is_dml_block = False

    def set_is_ddl_block(self):
        self.is_plsql_block = False
        self.block_depth = 0
        self.block_stack = []
        self.is_ddl_block = True
        self.is_dml_block = False

    def set_is_dml_block(self):
        self.is_plsql_block = False
        self.block_depth = 0
        self.block_stack = []
        self.is_ddl_block = False
        self.is_dml_block = True

    def increase_block_depth(self, block_type: str):
        self.block_depth += 1
        self.block_stack.append(block_type)
        print(f"block_depth: {self.block_depth}")

    def decrease_block_depth(self):
        self.block_depth -= 1
        self.block_stack.pop()
        if self.block_depth == 0:
            self.is_ddl_block = False
        print(f"block_depth: {self.block_depth}")

    def update_stack(self, param):
        self.block_stack[-1] = param
