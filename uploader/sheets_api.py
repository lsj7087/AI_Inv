import os
import json
import gspread
from google.oauth2.service_account import Credentials

def get_google_sheet():
    """
    환경 변수에서 인증 정보를 읽어 구글 시트 객체를 반환합니다.
    """
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # GitHub Action Secrets 등에서 주입받을 환경변수
    creds_json_str = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    spreadsheet_id = os.environ.get('SPREADSHEET_ID')
    
    if not creds_json_str or not spreadsheet_id:
        print("경고: GOOGLE_SERVICE_ACCOUNT_JSON 또는 SPREADSHEET_ID 환경 변수가 없습니다.")
        return None
        
    try:
        creds_dict = json.loads(creds_json_str)
        credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(credentials)
        sheet = client.open_by_key(spreadsheet_id)
        return sheet
    except Exception as e:
        print(f"구글 시트 인증 실패: {e}")
        return None

def insert_row_top(sheet_instance, tab_name, row_data):
    """
    지정된 탭의 2번째 행(헤더 바로 아래)에 새 데이터를 삽입합니다.
    """
    if not sheet_instance:
        return False
        
    try:
        worksheet = sheet_instance.worksheet(tab_name)
        # 2번째 행에 빈 행을 추가
        worksheet.insert_row(row_data, 2)
        print(f"[{tab_name}] 탭에 새 행 업데이트 완료.")
        return True
    except Exception as e:
        print(f"[{tab_name}] 시트 업데이트 실패: {e}")
        return False

def update_dashboard(sheet_instance, last_updated, status, summary):
    """
    Dashboard 탭의 특정 위치(B열 2,3,4행)를 고정적으로 업데이트합니다.
    (헤더: A열 1~3행이 Last Updated, System Status, Daily Summary 임을 가정)
    """
    if not sheet_instance:
        return False
        
    try:
        worksheet = sheet_instance.worksheet("Dashboard")
        # Dashboard는 로그가 쌓이는 구조가 아니라 단일 상태창이므로 셀을 명시적으로 업데이트
        worksheet.update_acell('B2', last_updated)
        worksheet.update_acell('B3', status)
        worksheet.update_acell('B4', summary)
        print("[Dashboard] 업데이트 완료.")
        return True
    except Exception as e:
        print(f"[Dashboard] 시트 업데이트 실패: {e}")
        return False

def insert_multiple_rows_top(sheet_instance, tab_name, rows_data):
    """
    지정된 탭의 2번째 행에 여러 행을 일괄 삽입합니다.
    (API Rate Limit 초과 방지용)
    rows_data: 리스트의 리스트 (예: [[val1, val2], [val3, val4]])
    """
    if not sheet_instance or not rows_data:
        return False
        
    try:
        worksheet = sheet_instance.worksheet(tab_name)
        # 여러 행을 한 번에 가장 윗줄(2번 행)에 삽입합니다.
        # insert_rows는 값이 들어갈 범위를 아래로 밀어내면서 삽입합니다.
        worksheet.insert_rows(rows_data, 2)
        print(f"[{tab_name}] 탭에 {len(rows_data)}개 행 일괄 업데이트 완료.")
        return True
    except Exception as e:
        print(f"[{tab_name}] 다중 행 시트 일괄 업데이트 실패: {e}")
        return False

def clear_sheet_data(sheet_instance, tab_name):
    """
    지정된 탭의 헤더(1행)를 제외한 기존의 모든 데이터를 삭제합니다.
    (Snapshot 구조용: 과거 분량을 지우고 최신 내용만 남기기 위함)
    """
    if not sheet_instance:
        return False
        
    try:
        worksheet = sheet_instance.worksheet(tab_name)
        # 1행은 헤더이므로 유지하고, 2행부터 1000행까지 데이터 및 행 삭제 (혹은 clear)
        # delete_rows(start_index) 는 start_index 부터 비우게 됩니다.
        
        # gspread에서 값을 지우려면 clear() 후 헤더를 쓰거나 기본 1000줄 범위를 지울 수 있음
        # 범위 데이터 초기화 : 'A2:Z1000'
        worksheet.batch_clear(["A2:Z1000"])
        print(f"[{tab_name}] 기존 누적 데이터 클리어 완료 (Snapshot 준비).")
        return True
    except Exception as e:
        print(f"[{tab_name}] 데이터 클리어 실패: {e}")
        return False

