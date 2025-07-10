import re

def is_dml_block(block_no, content):
    pattern = re.compile(r'^\s*(INSERT\s+INTO|UPDATE|DELETE\s+FROM|MERGE\s+INTO)\s+(?:(\w+)\.)?(\w+)(\s+.*)?', re.IGNORECASE)
    match = pattern.match(content)
    if match:
        dml_type, schema, table, rest = match.groups()
        schema = schema if schema else 'dfn_ntp'  # Default to 'dfn_ntp' if schema is not provided
        print(f"BLOCK:{block_no}, DML Type: {dml_type}, Schema: {schema}, Table: {table}")
        return dml_type.upper(), schema.lower(), table.lower()
    return None

def is_ddl_block(block_no, content):
    pattern = r'^\s*(CREATE(?:\s+OR\s+REPLACE)?|ALTER|DROP|TRUNCATE)\s+(TABLE|VIEW|INDEX|PROCEDURE|FUNCTION)?\s*(?:(\w+)\.)?(\w+)(\s+.*)?'
    match = re.match(pattern, content, re.IGNORECASE)
    if match:
        ddl_type, object_type, schema, db_object, rest = match.groups()
        schema = schema if schema else 'dfn_ntp'  # Default to 'dfn_ntp' if schema is not provided
        object_type = object_type.lower() if object_type else "unknown"
        print(f"BLOCK:{block_no}, DDL Type: {ddl_type}, Object Type: {object_type}, Schema: {schema}, Object: {db_object}")
        return ddl_type.upper(), object_type.lower(), schema.lower(), db_object.lower()
    return None

def is_plsql_ddl_block(block_no, content):
    # Step 1: Extract the string inside the l_ddl assignment
    ddl_string_match = re.search(r":=\s*'([^']+)'", content, re.DOTALL)
    ddl_string = ddl_string_match.group(1) if ddl_string_match else ""

    # Step 2: Apply the regex to the extracted DDL
    ddl_regex = re.compile(r"(CREATE(?:\s+OR\s+REPLACE)?|ALTER|DROP|TRUNCATE)\s+"
                           r"(TABLE|VIEW|INDEX|PROCEDURE|FUNCTION)?\s*"
                           r"(?:(\w+)\.)?(\w+)", re.IGNORECASE)

    match = ddl_regex.search(ddl_string)

    if match:
        ddl_type, object_type, schema, db_object = match.groups()
        schema = schema if schema else 'dfn_ntp'  # Default to 'dfn_ntp' if schema is not provided
        object_type = object_type.lower() if object_type else "unknown"
        print(f"BLOCK:{block_no}, DDL Type: {ddl_type}, Object Type: {object_type}, Schema: {schema}, Object: {db_object}")
        return ddl_type.upper(), object_type.lower(), schema.lower(), db_object.lower()
    else:
        print("No match found.")
    return None

def is_plsql_block_(block_no, content):
    pattern = re.compile(
        r"\s*(DECLARE|BEGIN)\b.*?"
        r"(dfn_ntp|dfn_arc|dfn_csm|dfn_ipo)\.\s*"
        r".*?"
        r"(END\s*;)\s*"
        r"/\s*",
        re.IGNORECASE | re.DOTALL
    )
    match = pattern.match(content)
    if match:
        start, schema, end = match.groups()
        schema = schema if schema else 'dfn_ntp'
        print(f"BLOCK:{block_no}, start:{start}, schema:{schema}, end: {end}")
        return start, schema.lower(), end
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


def is_plsql_block_start_line(line_number, line):
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
