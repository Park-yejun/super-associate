#!/bin/sh

# 컨테이너가 시작될 때, 설치된 모든 패키지 목록을 로그에 출력합니다.
echo "--- Checking installed packages in the virtual environment ---"
pip freeze
echo "--------------------------------------------------------"

# 패키지 목록을 출력한 후, 웹 서버를 시작합니다.
echo "Starting Gunicorn web server..."
gunicorn --bind 0.0.0.0:8080 main:app
