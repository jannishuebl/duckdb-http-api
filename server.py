from flask import Flask, request, Response, jsonify
import connector
import csv
import io
import json
from datetime import datetime
from datetime import date

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, date):
            return obj.isoformat()
        if isinstance(obj, datetime):
            return obj.isoformat()
        return json.JSONEncoder.default(self, obj)

app = Flask(__name__)

def stream_query_as_csv(query):
    result = connector.duckdb_con.execute(query)
    columns = [column[0] for column in result.description]

    def generate_csv():
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(columns)
        yield buffer.getvalue()
        buffer.truncate(0)
        buffer.seek(0)

        for row in result.fetchall():
            try:
                writer.writerow(row)
            except TypeError as e:
                writer.writerow([f"serialization_error: {str(e)}"])
            yield buffer.getvalue()
            buffer.truncate(0)
            buffer.seek(0)

    return generate_csv()

def stream_query_as_json(query):
    result = connector.duckdb_con.execute(query)
    columns = [column[0] for column in result.description]

    def generate_json():
        for row in result.fetchall():
            data = {columns[i]: value for i, value in enumerate(row)}
            try:
                yield f"{json.dumps(data, cls=CustomJSONEncoder)}\n"
            except TypeError as e:
                # Return an error in a human-readable JSON format
                error_message = {
                    "error": "serialization_error",
                    "detail": str(e),
                    "row": str(data)
                }
                yield json.dumps(error_message) + "\n"

    return generate_json()


@app.route('/query', methods=['POST'])
def execute_query():
    query = request.get_data().decode('utf-8')
    try:
        accept = request.headers.get('Accept')
        if accept == 'application/json':
            generator = stream_query_as_json(query)
            mimetype = 'application/json'
        else:
            generator = stream_query_as_csv(query)
            mimetype = 'text/csv'

        response = Response(generator, mimetype=mimetype)
        if mimetype == 'text/csv':
            response.headers['Content-Disposition'] = 'attachment; filename=result.csv'
        return response
    except Exception as e:
        print(str(e))
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run
