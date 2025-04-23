import sys
import connector
connector.duckdb_con.execute(sys.argv[1])
