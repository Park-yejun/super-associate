# 베이스 이미지: 파이썬 3.9 버전 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install -r requirements.txt

# 소스 코드 전체 복사
COPY . .

# Cloud Run이 사용할 포트 지정
EXPOSE 8080

# 웹 서버 실행 (Gunicorn 사용)
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "main:app"]
