import requests
import json

API_URL = "http://127.0.0.1:3000/query"

def test_sql_csv_output():
    headers = {"Content-Type": "text/plain"}
    response = requests.post(API_URL, data="SELECT 1 AS col1, 2 AS col2;", headers=headers)
    assert response.status_code == 200
    assert "col1,col2" in response.text
    assert "1,2" in response.text

def test_sql_ndjson_output():
    headers = {
        "Accept": "application/json",
        "Content-Type": "text/plain"
    }
    response = requests.post(API_URL, data="SELECT 1 AS col1, 2 AS col2;", headers=headers)
    assert response.status_code == 200
    lines = response.text.strip().splitlines()
    assert len(lines) == 1
    row = json.loads(lines[0])
    assert row == {"col1": 1, "col2": 2}

def test_sql_invalid_syntax():
    headers = {"Content-Type": "text/plain"}
    response = requests.post(API_URL, data="SELEKT * FROM nowhere;", headers=headers)
    assert response.status_code in (400, 500)
    assert "error" in response.text.lower()

def parse_ndjson(text):
    return [json.loads(line) for line in text.strip().splitlines()]

def test_spatial_extension_preinstalled():
    headers = {
        "Accept": "application/json",
        "Content-Type": "text/plain"
    }
    response = requests.post(API_URL, data="SELECT ST_AsText(ST_Point(1.1, 2.2)) AS pt;", headers=headers)
    assert response.status_code == 200
    rows = parse_ndjson(response.text)
    assert rows[0]["pt"] == "POINT (1.1 2.2)"

def test_json_serialization_error_handling():
    headers = {
        "Accept": "application/json",
        "Content-Type": "text/plain"
    }
    response = requests.post(API_URL, data="SELECT ST_Point(0, 0) AS geom;", headers=headers)
    assert response.status_code == 200
    rows = parse_ndjson(response.text)
    assert "error" in rows[0]
    assert rows[0]["error"] == "serialization_error"

def test_stmt_query_with_params():
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "sql": "SELECT ? AS val, ? AS label",
        "params": [42, "hello"]
    }
    response = requests.post(API_URL, data=json.dumps(payload), headers=headers)
    assert response.status_code == 200
    rows = parse_ndjson(response.text)
    assert rows[0] == {"val": 42, "label": "hello"}

