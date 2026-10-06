"""เปิด FastAPI server รอจนพร้อม รัน Newman ทุกชุด แล้วปิด server

วิธีใช้: python scripts/run_postman.py
ต้องติดตั้ง Newman ก่อน: npm install -g newman newman-reporter-htmlextra
"""

import subprocess
import sys
import time
import urllib.request

BASE_URL = "http://127.0.0.1:8000"
COLLECTION = "postman/API-Testing-Lab.postman_collection.json"
ENVIRONMENT = "postman/local.postman_environment.json"

def wait_for_server(url: str, timeout: float = 30) -> bool:
    """เรียก url ซ้ำจนได้ 200 หรือหมดเวลา"""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url) as response:
                if response.status == 200:
                    return True
        except OSError:
            time.sleep(0.5)
    return False

def run_newman(*args: str) -> int:
    command = ["newman", "run", COLLECTION, "-e", ENVIRONMENT, *args]
    # บน Windows คำสั่ง newman เป็นไฟล์ .cmd จึงต้องรันผ่าน shell
    use_shell = sys.platform == "win32"
    return subprocess.run(command, shell=use_shell).returncode

def main() -> int:
    server = subprocess.Popen([
        sys.executable, "-m", "uvicorn",
        "app.main:app", "--port", "8000",
    ])
    try:
        if not wait_for_server(f"{BASE_URL}/health"):
            print("Server did not start in time")
            return 1
        exit_code = run_newman(
            "--folder", "01-Unit-API-Tests",
            "--folder", "02-Integration-Flow",
            "-r", "cli,htmlextra",
            "--reporter-htmlextra-export", "reports/postman-report.html",
        )
        if exit_code == 0:
            exit_code = run_newman(
                "--folder", "03-Data-Driven",
                "-d", "postman/data/products.csv",
            )
        return exit_code
    finally:
        server.terminate()
        server.wait()

if __name__ == "__main__":
    sys.exit(main())
