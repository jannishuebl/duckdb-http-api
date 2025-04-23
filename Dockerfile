FROM python:3.10-slim

WORKDIR /app

ARG DUCKDB_VERSION=1.0.0

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir duckdb==${DUCKDB_VERSION} && \
    pip install --no-cache-dir -r requirements.txt

COPY connector.py .
COPY execute.py .
COPY execute_file.py .
COPY server.py .

ENV GUNICORN_CMD_ARGS="-w 4 -b 0.0.0.0:3000"
EXPOSE 3000

CMD ["gunicorn", "server:app"]
