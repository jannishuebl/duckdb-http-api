# DuckDB HTTP API

The DuckDB HTTP API Server provides a simple and efficient way to interact with a DuckDB instance through HTTP requests. It allows you to run SQL queries and retrieve results in various formats (such as CSV and JSON) by sending requests to the server.

Key Features:

    HTTP-based Interface: Query DuckDB databases over HTTP without the need for a dedicated client.
    SQL Query Execution: Submit SQL queries using HTTP POST requests and receive query results in CSV or JSON format.
    Flexible Data Access: Mount external data (such as CSV files) into the container and query them using DuckDB's SQL engine.
    Extension Support: Easily install DuckDB extensions (such as spatial or other specialized extensions) to extend functionality.
    Initialization Scripts: Run custom SQL scripts on server startup for setting up helper functions, configuring extensions, or preparing your database.

This server is lightweight and highly customizable, making it ideal for local development, data analysis tasks, and integration with other tools and platforms.

## ⚠️ Warning: Security Considerations

**Do not expose this server to the public internet without proper authorization and security measures.** 

By default, the DuckDB HTTP API grants access to all data on the machine, including any files the DuckDB instance has root access to. If exposed without proper configuration, **anyone** could send SQL queries to the server, potentially gaining access to sensitive data or performing destructive operations.

### Key Security Recommendations:
- **Only use the server locally** or behind a properly configured firewall.
- **Do not expose it to the internet** unless you have implemented adequate authentication and authorization mechanisms.
- If using in a production environment, ensure:
  - You have restricted access through a reverse proxy with authentication (e.g., Nginx, Traefik).
  - You are aware of the data exposure risks associated with DuckDB having access to the root file system.

## Configure the Server

You can configure the server by using Gunicorn's settings. Refer to the [Gunicorn documentation](https://docs.gunicorn.org/en/latest/settings.html#settings) for more details.

To pass Gunicorn settings, you can use the environment variable:

```bash
export GUNICORN_CMD_ARGS="<your gunicorn args here>"
```

## Configure DuckDB via Environment Variables

DuckDB can be configured using environment variables prefixed with `DUCKDB_XXX`. Please refer to the [DuckDB configuration reference](https://duckdb.org/docs/configuration/overview#configuration-reference) for detailed options.

## Running DuckDB HTTP API with Docker

You can run the DuckDB HTTP API using Docker with the following command:

```bash
docker run --rm -p 127.0.0.1:3000:3000 duckdb-http-api
```

### CSV Output Example

To query the server and get a CSV output, run:

```bash
curl -X POST --data "select 1 as col1, 2 as col2;" http://127.0.0.1:3000/query
```

### JSON Output Example

To retrieve the result as JSON, you can include the `Accept: application/json` header:

```bash
curl -X POST --data "select 1 as col1, 2 as col2;" -H "Accept: application/json" http://127.0.0.1:3000/query
```

## Mounting Data with Docker

You can mount your data directory into the Docker container and run DuckDB queries on it:

```bash
docker run --rm -p 127.0.0.1:3000:3000 -v /path/to/your/data:/data duckdb-http-api
```

Then, to query a CSV file inside the mounted data:

```bash
curl -X POST --data "SELECT * FROM read_csv('/data/example.csv')" -H "Accept: application/json" http://127.0.0.1:3000/query
```

## Installing Extensions

You can install DuckDB extensions in your own Docker image. Below is an example Dockerfile:

```Dockerfile
FROM duckdb-http-api:latest

# Install the spatial extension
RUN python execute.py "INSTALL spatial;"

# Add an installation SQL script to the container
ADD install.sql .
RUN python execute_file.py "install.sql"
```

## Running an Initialization Script

You can use an initialization script that is executed when the server starts. This can be useful for loading extensions or adding helper functions. The following environment variables are available for configuring this:

- `DUCKDB_HTTP_API_INIT_FILE` (default: `/init.sql`)
- `DUCKDB_HTTP_API_INIT_SCRIPT` (default: empty)

The initialization script can contain any custom SQL commands to be executed at startup.

## Further Documentation

For more detailed information, refer to the code, which consists of only 100 lines, making it more complicated to read a extensive Documentation than simply understanding the code.

## 📜 License

This project is licensed under the **GNU Lesser General Public License (LGPL)**. 

You are free to use, modify, and distribute the software under the following conditions:
- **Modification and Distribution:** You can modify and distribute the software, but you must ensure that any modifications are also licensed under the LGPL.
- **Dynamic Linking:** You may dynamically link this project with non-LGPL software, as long as you comply with the LGPL when distributing the combined work.
- **Notice of License:** When distributing the software, or any modifications to it, you must include a copy of this license and provide notice that the software is under the LGPL.

For more details, you can read the full license text at: [LGPL License](https://www.gnu.org/licenses/lgpl-3.0.html).

**Note:** By contributing to this project, you agree that your contributions will be licensed under the same LGPL license.
