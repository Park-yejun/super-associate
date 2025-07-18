FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# [수정] 모든 소스 코드를 복사합니다.
COPY . .

# [추가] run.sh 파일을 실행 가능하도록 권한을 부여합니다.
RUN chmod +x run.sh

EXPOSE 8080

# [수정] gunicorn을 직접 실행하는 대신, run.sh 스크립트를 실행합니다.
CMD ["./run.sh"]
