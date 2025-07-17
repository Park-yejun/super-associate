from flask import Flask, jsonify, request
from flask_cors import CORS
import gspread
from google.oauth2.service_account import Credentials
import os

app = Flask(__name__)
CORS(app)

# --- Google Sheets API 설정 ---
# Google Cloud 서비스 계정 키를 사용하기 위한 설정
# GitHub Actions Secret에 GCP_SA_KEY를 등록해야 함
# 로컬 테스트 시에는 'your-service-account-file.json' 파일을 사용
try:
    # Cloud Run 환경 (환경 변수에서 키 읽기)
    # 이 부분은 실제 서비스 계정 키(JSON 내용 전체)를 환경 변수로 설정해야 함
    # Cloud Run 배포 설정의 '변수' 탭에서 설정 가능
    import json
    keyfile_dict = json.loads(os.environ.get('GCP_SA_KEY_JSON'))
    creds = Credentials.from_service_account_info(keyfile_dict)
except:
    # 로컬 테스트 환경 (파일에서 키 읽기)
    # creds = Credentials.from_service_account_file('your-local-key.json')
    # 지금은 간단하게 예외 처리
    creds = None
    print("Warning: Service account key not found. Google Sheets API will not work.")

# gspread 클라이언트 초기화
if creds:
    gc = gspread.authorize(creds)
# -----------------------------

# 구글 시트 정보
SPREADSHEET_ID = '1F4rZbcBiuM9MDoFyfHnXVIFJ7GX99lUmaZZL_i3WZ40'
SHEET_NAME = '시트1'


@app.route('/api/verify-card')
def verify_card():
    user_id = request.args.get('id')
    if not user_id:
        return jsonify({"status": "error", "message": "ID is required"}), 400

    if not gc:
        return jsonify({"status": "error", "message": "Google Sheets API not configured"}), 500

    try:
        # 구글 시트 열기
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        worksheet = spreadsheet.worksheet(SHEET_NAME)

        # E열(ID)과 G열(팝업 타입)의 모든 데이터 가져오기
        id_column_values = worksheet.col_values(5)  # E열은 5번째 열
        popup_type_values = worksheet.col_values(7) # G열은 7번째 열

        # ID 검색
        try:
            index = id_column_values.index(user_id)
            popup_type_str = popup_type_values[index]
            
            # G열의 값이 1~5 사이의 숫자인지 확인
            if popup_type_str.isdigit() and 1 <= int(popup_type_str) <= 5:
                return jsonify({"status": "success", "popup_type": int(popup_type_str)})
            else:
                # 1~5가 아닌 다른 값이면 에러 팝업을 위한 타입 반환
                return jsonify({"status": "success", "popup_type": "error"})

        except ValueError:
            # ID를 찾지 못한 경우
            return jsonify({"status": "not_found"}), 404

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"status": "error", "message": "An internal error occurred"}), 500


@app.route('/')
def index():
    return "Card Verification Backend is running."


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
