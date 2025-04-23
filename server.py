from flask import Flask, request, Response, jsonify
import connector
import csv
import io
import json
from datetime import datetime, date

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

app = Flask(__name__)

def stream_query_as_csv(result, columns):
    def generate_csv():
        buffer = io.StringIO()
        writer = csv.writer(buffer)

        writer.writerow(columns)
        yield buffer.getvalue()
        buffer.seek(0)
        buffer.truncate(0)

        for row in result.fetchall():
            try:
                writer.writerow(row)
            except TypeError as e:
                writer.writerow([f"serialization_error: {str(e)}"])
            yield buffer.getvalue()
            buffer.seek(0)
            buffer.truncate(0)
    return generate_csv()


def stream_query_as_json(result, columns):
    def generate_json():
        for row in result.fetchall():
            data = {columns[i]: value for i, value in enumerate(row)}
            try:
                yield f"{json.dumps(data, cls=CustomJSONEncoder)}\n"
            except TypeError as e:
                yield json.dumps({
                    "error": "serialization_error",
                    "detail": str(e),
                    "row": str(data)
                }) + "\n"
    return generate_json()

def execute_and_stream(query, params=None, mimetype='text/csv'):
    result = connector.duckdb_con.execute(query, params or [])
    columns = [col[0] for col in result.description]
    generator = stream_query_as_json(result, columns) if mimetype == 'application/json' else stream_query_as_csv(result, columns)
    response = Response(generator, mimetype=mimetype)
    if mimetype == 'text/csv':
        response.headers['Content-Disposition'] = 'attachment; filename=result.csv'
    return response

@app.route('/raw', methods=['POST'])
def handle_raw():
    query = request.get_data(as_text=True)
    mimetype = request.headers.get('Accept', 'text/csv')
    return execute_and_stream(query, mimetype=mimetype)

@app.route('/stmt', methods=['POST'])
def handle_stmt():
    data = request.get_json()
    query = data.get('sql')
    params = data.get('params', [])
    mimetype = request.headers.get('Accept', 'application/json')
    return execute_and_stream(query, params, mimetype=mimetype)

@app.route('/query', methods=['POST'])
def smart_dispatch():
    content_type = request.headers.get('Content-Type', '')
    if content_type == 'application/json':
        return handle_stmt()
    else:
        return handle_raw()

if __name__ == '__main__':
    app.run(debug=True)
