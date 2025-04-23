import requests
import json

API_URL = "http://127.0.0.1:3000/query"

def test_sql_csv_output():
    response = requests.post(API_URL, data="SELECT 1 AS col1, 2 AS col2;")
    assert response.status_code == 200
    assert "col1,col2" in response.text
    assert "1,2" in response.text

def test_sql_ndjson_output():
    headers = {"Accept": "application/json"}
    response = requests.post(API_URL, data="SELECT 1 AS col1, 2 AS col2;", headers=headers)
    assert response.status_code == 200

    # Parse each line as a separate JSON object
    lines = response.text.strip().splitlines()
    assert len(lines) == 1  # One row returned
    import json
    row = json.loads(lines[0])
    assert row == {"col1": 1, "col2": 2}

def test_sql_invalid_syntax():
    response = requests.post(API_URL, data="SELEKT * FROM nowhere;")
    assert response.status_code == 400 or response.status_code == 500
    assert "error" in response.text.lower()

def parse_ndjson(text):
    return [json.loads(line) for line in text.strip().splitlines()]

def test_spatial_extension_preinstalled():
    headers = {"Accept": "application/json"}
    response = requests.post(API_URL, data="SELECT ST_AsText(ST_Point(1.1, 2.2)) AS pt;", headers=headers)
    assert response.status_code == 200
    rows = [json.loads(line) for line in response.text.strip().splitlines()]
    assert rows[0]["pt"] == "POINT (1.1 2.2)"


def test_json_serialization_error_handling():
    headers = {"Accept": "application/json"}
    # This will return WKB geometry, which is not handled unless a decoder is used
    response = requests.post(API_URL, data="SELECT ST_Point(0, 0) AS geom;", headers=headers)
    assert response.status_code == 200

    rows = [json.loads(line) for line in response.text.strip().splitlines()]
    assert "error" in rows[0]
    assert "serialization_error" in rows[0]["error"]

