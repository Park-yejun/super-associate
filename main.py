from flask import Flask, jsonify, request
from flask_cors import CORS
import gspread
from google.oauth2.service_account import Credentials
import os
import json

app = Flask(__name__)
CORS(app)

# --- Google Sheets API 설정 ---
creds = None
gc = None

try:
    # 1. 환경 변수에서 서비스 계정 키(JSON 문자열)를 읽어옵니다.
    key_json_str = os.environ['GCP_SA_KEY_JSON'] # .get() 대신 []를 사용해 키가 없으면 바로 에러 발생
    
    # 2. JSON 문자열을 파이썬 딕셔너리로 변환합니다.
    keyfile_dict = json.loads(key_json_str)
    
    # 3. 자격 증명을 생성합니다.
    creds = Credentials.from_service_account_info(keyfile_dict)
    
    # 4. gspread 클라이언트를 초기화합니다.
    gc = gspread.authorize(creds)

# [진단 기능 1] 환경 변수 자체가 없을 때의 에러 처리
except KeyError:
    print("ERROR: 환경 변수 'GCP_SA_KEY_JSON'을 찾을 수 없습니다.")

# [진단 기능 2] 환경 변수 값(JSON)이 잘못되었을 때의 에러 처리
except json.JSONDecodeError:
    print("ERROR: 'GCP_SA_KEY_JSON' 환경 변수의 JSON 형식이 잘못되었습니다.")

# [진단 기능 3] 그 외 모든 예외 처리
except Exception as e:
    print(f"ERROR: gspread 초기화 중 알 수 없는 에러 발생: {e}")

# -----------------------------

# 구글 시트 정보
SPREADSHEET_ID = '1F4rZbcBiuM9MDoFyfHnXVIFJ7GX99lUmaZZL_i3WZ40'
SHEET_NAME = '시트1'

@app.route('/api/verify-card')
def verify_card():
    user_id = request.args.get('id')
    if not user_id:
        return jsonify({"status": "error", "message": "ID is required"}), 400

    # gspread 클라이언트가 성공적으로 초기화되었는지 확인
    if not gc:
        # 초기화 실패 시, 구체적인 에러 메시지 반환
        return jsonify({"status": "error", "message": "서버 설정 오류: Google Sheets API에 연결할 수 없습니다. 관리자에게 문의하세요."}), 500

    try:
        spreadsheet = gc.open_by_key(SPREADSHEET_ID)
        worksheet = spreadsheet.worksheet(SHEET_NAME)

        id_column_values = worksheet.col_values(5)
        popup_type_values = worksheet.col_values(7)

        try:
            index = id_column_values.index(user_id)
            popup_type_str = popup_type_values[index]
            
            if popup_type_str.isdigit() and 1 <= int(popup_type_str) <= 5:
                return jsonify({"status": "success", "popup_type": int(popup_type_str)})
            else:
                return jsonify({"status": "success", "popup_type": "error"})

        except ValueError:
            return jsonify({"status": "not_found"}), 404

    # [진단 기능 4] 구글 시트 API 호출 중 발생하는 모든 에러 처리
    except gspread.exceptions.APIError as e:
        print(f"Google Sheets API Error: {e}")
        # API 에러(권한 부족 등) 발생 시 구체적인 메시지 반환
        return jsonify({"status": "error", "message": f"Google Sheets API 오류: {e.response.json()['error']['message']}"}), 500
    except Exception as e:
        print(f"An error occurred during sheet processing: {e}")
        return jsonify({"status": "error", "message": "An internal error occurred"}), 500

@app.route('/')
def index():
    return "Card Verification Backend is running."

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
