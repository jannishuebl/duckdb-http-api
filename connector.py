import duckdb
import os

duckdb_env_vars = {
    key[7:].lower(): value
    for key, value in os.environ.items()
    if key.startswith("DUCKDB_") and not key.startswith("DUCKDB_HTTP_API_")
}

duckdb_con = duckdb.connect(database=os.environ.get("DUCKDB_HTTP_API_DATABASE", ':memory:'), config=duckdb_env_vars)

init_file = os.environ.get("DUCKDB_HTTP_API_INIT_FILE", '/init.sql')

if os.path.exists(init_file):
    with open(init_file, 'r') as file:
        duckdb_con.execute(file.read())

init_script = os.environ.get("DUCKDB_HTTP_API_INIT_SCRIPT")
if init_script: 
    duckdb_con.execute(init_script)
