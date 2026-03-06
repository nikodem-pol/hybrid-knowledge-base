def format_schema(schema_dict):
    output = ""
    for table, columns in schema_dict.items():
        output += f"Table {table}: {', '.join(columns)}\n"
    return output

def format_schema_with_types(schema_dict):
    output = ""
    for table, columns in schema_dict.items():
        output += f"Table {table}:"
        for column in columns:
            output += f" {column['name']}({column['type']})"
        output += '\n'
    return output

def validate_sql(sql: str):
    sql = sql.strip().lower()

    if not sql.startswith("select"):
        raise ValueError("Only SELECT queries allowed")

    forbidden = ["delete", "update", "insert", "drop", "alter"]
    if any(word in sql for word in forbidden):
        raise ValueError("Unsafe SQL detected")

    return True