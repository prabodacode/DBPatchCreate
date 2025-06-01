import re

def is_dml_block(block_no, content):
    pattern = re.compile(r'^\s*(INSERT\s+INTO|UPDATE|DELETE\s+FROM|MERGE\s+INTO)\s+(?:(\w+)\.)?(\w+)(\s+.*)?', re.IGNORECASE)
    match = pattern.match(content)
    if match:
        dml_type, schema, table, rest = match.groups()
        schema = schema if schema else 'dfn_ntp'  # Default to 'dfn_ntp' if schema is not provided
        print(f"BLOCK:{block_no}, DML Type: {dml_type}, Schema: {schema}, Table: {table}")
        return dml_type, schema, table
    return None

def is_ddl_block(block_no, content):
    pattern = r'^\s*(CREATE(?:\s+OR\s+REPLACE)?|ALTER|DROP|TRUNCATE)\s+(TABLE|VIEW|INDEX|PROCEDURE|FUNCTION)?\s*(?:(\w+)\.)?(\w+)(\s+.*)?'
    match = re.match(pattern, content, re.IGNORECASE)
    if match:
        ddl_type, object_type, schema, db_object, rest = match.groups()
        schema = schema if schema else 'dfn_ntp'  # Default to 'dfn_ntp' if schema is not provided
        object_type = object_type.lower() if object_type else "unknown"
        print(f"BLOCK:{block_no}, DDL Type: {ddl_type}, Object Type: {object_type}, Schema: {schema}, Object: {db_object}")
        return ddl_type.upper(), object_type, schema, db_object
    return None


def is_dml_start_line(line_number, line):
    pattern = re.compile(r'^\s*(INSERT\s+INTO|UPDATE|DELETE\s+FROM|MERGE\s+INTO)\s+(?:(\w+)\.)?(\w+)\s*', re.IGNORECASE)
    match = pattern.match(line)
    if match:
        dml_type, schema, table = match.groups()
        schema = schema if schema else 'dfn_ntp'  # Default to 'dfn_ntp' if schema is not provided
        print(f"LN:{line_number}, DML Type: {dml_type}, Schema: {schema}, Table: {table}")
        return dml_type, schema, table
    return None


def is_ddl_start_line(line_number, line):
    pattern = r'^\s*(CREATE(?:\s+OR\s+REPLACE)?|ALTER|DROP|TRUNCATE)\s+(TABLE|VIEW|INDEX|PROCEDURE|FUNCTION)?\s*(?:(\w+)\.)?(\w+)\s*'
    match = re.match(pattern, line, re.IGNORECASE)
    if match:
        ddl_type, object_type, schema, db_object = match.groups()
        schema = schema if schema else 'dfn_ntp'  # Default to 'dfn_ntp' if schema is not provided
        object_type = object_type.lower() if object_type else "unknown"
        print(f"LN:{line_number}, DDL Type: {ddl_type}, Object Type: {object_type}, Schema: {schema}, Object: {db_object}")
        return ddl_type.upper(), object_type, schema, db_object
    return None


def get_is_block_start_line(line_number, line):
    pattern = r'^\s*(DECLARE|BEGIN)\s*(--.*|/\*.*\*/)?\s*$' # DECLARE or BEGIN followed by optional semicolon followed by optional (--comment or /* comment */)
    match = re.match(pattern, line, re.IGNORECASE)
    if match:
        block_type = match.group(1).upper()
        print(f"LN:{line_number}, BLOCK Type: {block_type}")
        return True, block_type
    return False, None


def is_block_end_line(line_number, line):
    pattern = r'^\s*(END\s*;?)\s*(--.*|/\*.*\*/)?\s*$'  # END followed by optional semicolon followed by optional (--comment or /* comment */)
    match = re.match(pattern, line, re.IGNORECASE)
    if match:
        block_type = match.group(1).upper()
        print(f"LN:{line_number}, BLOCK END Type: {block_type}")
        return True
    return False


def is_slash_line(line_number, line):
    pattern = r'^\s*(/+)\s*(--.*|/\*.*\*/)?\s*$'    # slash followed by optional (--comment or /* comment */)
    match = re.match(pattern, line, re.IGNORECASE)
    if match:
        block_type = match.group(1).upper()
        print(f"LN:{line_number}, SLASH Line: {block_type}")
        return True
    return False


def is_commit_line(line_number, line):
    pattern = r'^\s*(COMMIT\s*;)\s*(--.*|/\*.*\*/)?\s*$'    # COMMIT followed by semicolon, followed by optional (--comment or /* comment */)
    match = re.match(pattern, line, re.IGNORECASE)
    if match:
        block_type = match.group(1).upper()
        print(f"LN:{line_number}, COMMIT Line: {block_type}")
        return True
    return False
