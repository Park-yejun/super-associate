from flask import Flask, jsonify
from flask_cors import CORS
import os

# Flask 앱을 생성합니다.
app = Flask(__name__)

# CORS(Cross-Origin Resource Sharing)를 설정합니다.
# 이렇게 해야 다른 도메인(Firebase)에서 보낸 요청을 Cloud Run이 허용합니다.
CORS(app)

# '/api/message' 경로로 GET 요청이 오면 이 함수가 실행됩니다.
@app.route('/api/message')
def get_message():
    # JSON 형태로 응답 메시지를 만듭니다.
    response_data = {
        "message": "안녕하세요! 파이썬 백엔드에서 성공적으로 응답을 보냈습니다. 🎉"
    }
    return jsonify(response_data)

# 기본 경로 '/'로 접속했을 때 안내 메시지를 보여줍니다.
@app.route('/')
def index():
    return "Cloud Run 백엔드 서버가 정상적으로 작동 중입니다."

# 서버를 실행합니다.
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
