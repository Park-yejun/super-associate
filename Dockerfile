# 베이스 이미지로 Python 3.9-slim 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# requirements.txt를 먼저 복사하여 종속성을 캐시
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 현재 디렉토리의 모든 파일을 컨테이너의 /app 디렉토리로 복사
COPY . .

# Cloud Run이 자동으로 PORT 환경 변수를 제공합니다.
# EXPOSE 8080은 문서화 목적으로는 좋지만, 실제 포트는 아래 CMD에서 결정됩니다.
ENV PORT 8080

# [수정된 부분] Flask 개발 서버 대신 Gunicorn 프로덕션 서버로 실행
CMD ["gunicorn", "--bind", "0.0.0.0:${PORT}", "--workers", "1", "main:app"]
