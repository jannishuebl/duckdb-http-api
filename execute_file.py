import sys
import connector
with open(sys.argv[1], 'r') as file:
    connector.duckdb_con.execute(file.read())
