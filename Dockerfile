# 베이스 이미지: 파이썬 3.9 버전 사용
FROM python:3.9-slim

# 작업 디렉토리 설정
WORKDIR /app

# [추가] 파이썬이 가상 환경을 인식하도록 환경 변수 설정
# 앞으로 모든 명령어는 이 가상 환경 안에서 실행됨
ENV VIRTUAL_ENV=/app/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# [추가] /app/venv 라는 이름의 가상 환경(안전지대) 생성
RUN python3 -m venv $VIRTUAL_ENV

# 의존성 파일 복사
COPY requirements.txt .

# [수정] 전역 공간이 아닌, 오직 가상 환경 안에만 패키지 설치
RUN pip install -r requirements.txt

# 소스 코드 전체 복사
COPY . .

# run.sh 파일을 실행 가능하도록 권한 부여
RUN chmod +x run.sh

EXPOSE 8080

# run.sh 스크립트 실행
CMD ["./run.sh"]
