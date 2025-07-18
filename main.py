import os
import json
from flask import Flask, request, jsonify, render_template
import firebase_admin
from firebase_admin import credentials, firestore

# --- Firebase Admin SDK 초기화 ---
SERVICE_ACCOUNT_FILE = 'serviceAccountKey.json'
PROJECT_ID = 'super-associate' # 본인의 Firebase 프로젝트 ID

try:
    # 1. 깃허브 시크릿(환경 변수)에서 인증 정보 로드 (배포 환경용)
    firebase_creds_json_str = os.environ.get('FIREBASE_CREDENTIALS')
    if firebase_creds_json_str:
        print("환경 변수에서 Firebase 인증 정보를 로드합니다.")
        cred_json = json.loads(firebase_creds_json_str)
        cred = credentials.Certificate(cred_json)
    else:
        # 2. 로컬 파일에서 인증 정보 로드 (로컬 개발 환경용)
        print(f"로컬 파일({SERVICE_ACCOUNT_FILE})에서 Firebase 인증 정보를 로드합니다.")
        cred = credentials.Certificate(SERVICE_ACCOUNT_FILE)
    
    # Firebase 앱 초기화
    firebase_admin.initialize_app(cred, {'projectId': PROJECT_ID})

except Exception as e:
    print(f"Firebase 초기화 중 오류 발생: {e}")

# Firestore 클라이언트 인스턴스 생성
db = firestore.client()
# --- 초기화 끝 ---


app = Flask(__name__)

# --- 웹 페이지 라우팅 ---
@app.route('/')
def index():
    """메인 페이지를 보여주고, DB에 저장된 데이터를 시간순으로 표시합니다."""
    try:
        # 'entries' 컬렉션의 모든 문서를 'timestamp' 필드를 기준으로 내림차순(최신순) 정렬
        entries_ref = db.collection('entries').order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
        entries = [doc.to_dict() for doc in entries_ref]
        return render_template('index.html', entries=entries)
    except Exception as e:
        error_message = f"데이터 로딩 오류: {e}"
        return render_template('index.html', entries=[], error=error_message)

# --- 데이터 추가 API ---
@app.route('/add-data', methods=['POST'])
def add_data():
    """프론트엔드에서 보낸 데이터를 Firestore에 추가합니다."""
    try:
        data = request.get_json()
        user_input = data.get('text')

        if not user_input:
            return jsonify({"status": "error", "message": "입력 내용이 없습니다."}), 400
        
        # Firestore에 저장할 데이터
        doc_data = {
            'text': user_input,
            'timestamp': firestore.SERVER_TIMESTAMP # 서버 시간을 기준으로 타임스탬프 기록
        }
        
        # 'entries' 라는 새 컬렉션에 데이터 추가
        db.collection('entries').add(doc_data)
        
        return jsonify({"status": "success", "message": f"'{user_input}' 저장 완료!"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# --- 서버 실행 ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
