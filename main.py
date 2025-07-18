import os
import io
from datetime import datetime, timezone, timedelta

from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS

# --- Google Cloud & 3rd Party Libraries ---
from google.cloud import firestore
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

app = Flask(__name__)

# --- [수정] CORS 설정 강화 ---
# 특정 출처(프론트엔드 주소)를 명시적으로 허용하여 보안을 강화하고 문제를 해결합니다..
CORS(
    app,
    origins=["https://super-associate.web.app"], # 이 주소에서의 요청만 허용
    methods=["POST", "GET", "OPTIONS"],      # 허용할 HTTP 메소드
    allow_headers=["Content-Type"],          # 허용할 헤더
    expose_headers=["X-User-ID"]             # 프론트엔드가 읽을 수 있도록 허용할 커스텀 헤더
)
# -----------------------------


# --- Initialize Firestore Client ---
db = firestore.Client()

@app.route('/api/register-and-download-card', methods=['POST'])
def register_and_download_card():
    """
    사용자 등록을 처리하고, Firestore에 저장한 뒤,
    PDF 카드를 생성하여 직접 다운로드하도록 반환합니다.
    """
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')

        if not name or not email or '@' not in email:
            return jsonify({"message": "이름과 올바른 이메일 주소를 입력해주세요."}), 400

        # --- 1. 사용자 데이터 생성 및 Firestore에 저장 ---
        kst = timezone(timedelta(hours=9))
        now = datetime.now(kst)
        timestamp_for_id = now.strftime('%Y%m%d-%H%M%S')
        email_part = email.split('@')[0][:5]
        unique_id = f"C{timestamp_for_id}-{email_part}"

        user_doc_ref = db.collection('users').document(unique_id)
        user_doc_ref.set({
            'name': name,
            'email': email,
            'uniqueId': unique_id,
            'registrationTimestamp': now,
            'status': 'CARD_GENERATED'
        })

        # --- 2. 메모리에서 PDF 사용자 카드 생성 ---
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        p.drawString(100, height - 100, "Super Associate - Digital User Card")
        p.drawString(100, height - 150, f"Name: {name}")
        p.drawString(100, height - 170, f"Email: {email}")
        p.drawString(100, height - 190, f"Unique ID: {unique_id}")
        
        link_url = f"https://super-associate.web.app?id={unique_id}"
        p.linkURL(link_url, (95, height - 255, 205, height - 225), relative=1)
        p.setFillColorRGB(0, 0, 1)
        p.drawString(100, height - 240, "Click here to START")
        
        p.showPage()
        p.save()
        
        buffer.seek(0)

        # --- 3. 생성된 PDF를 프론트엔드로 직접 반환 ---
        response = make_response(send_file(
            buffer,
            as_attachment=True,
            download_name=f'SA_User_Card_{unique_id}.pdf',
            mimetype='application/pdf'
        ))
        response.headers['X-User-ID'] = unique_id
        return response

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"message": f"서버 내부 오류가 발생했습니다: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
