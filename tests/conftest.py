import subprocess
import time
import pytest
import requests

API_URL = "http://127.0.0.1:3000/query"

@pytest.fixture(scope="session", autouse=True)
def build_and_start_test_image():
    print("🔧 Building test Docker image...")
    subprocess.run([
        "docker", "build",
        "-f", "Dockerfile.test",
        "-t", "duckdb-http-api:test", "."
    ], check=True)

    print("🚀 Starting test Docker container...")
    proc = subprocess.Popen([
        "docker", "run", "--rm",
        "-p", "127.0.0.1:3000:3000",
        "--name", "duckdb_test_api",
        "duckdb-http-api:test"
    ])

    # Wait for server to be ready
    for _ in range(10):
        try:
            response = requests.post(API_URL, data="SELECT 1;")
            print(response)
            if response.status_code == 200:
                break
        except requests.ConnectionError:
            time.sleep(1)
    else:
        proc.terminate()
        raise RuntimeError("DuckDB HTTP API server failed to start")

    yield

    print("🛑 Stopping Docker container...")
    proc.terminate()

