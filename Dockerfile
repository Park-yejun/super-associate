# 베이스 이미지로 Python 3.9-slim 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt를 먼저 복사하여 종속성을 캐시
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 현재 디렉토리의 모든 파일을 컨테이너의 /app 디렉토리로 복사
COPY . .

# 컨테이너가 8080 포트를 외부에 노출하도록 설정
EXPOSE 8080

# 컨테이너 시작 시 실행할 명령어
CMD ["python", "main.py"]
