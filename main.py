import sys
from datetime import datetime

from crawler.blog_scraper import get_latest_post_ranto28
from crawler.market_indicator import get_market_data
from crawler.finance_scraper import get_economic_news
from uploader.sheets_api import get_google_sheet, insert_multiple_rows_top, update_dashboard, clear_sheet_data

def main():
    print("="*40)
    print("AI-Inv Data Collection Engine Started (Global Update & Snapshot Mode)")
    print("="*40)
    
    # 1. 시트 연결 초기화
    print("[1] Google Sheets 연결 시도...")
    sheet = get_google_sheet()
    if not sheet:
        print("시트 연결 실패로 시스템을 종료합니다.")
        sys.exit(1)
        
    print("[2] 데이터 수집 시작...")
    
    # === A. 전문가 인사이트 (Expert Analytic) ===
    print("  - ranto28 블로그 수집중 (RSS 기반 최신 20건)...")
    blog_data_list = get_latest_post_ranto28()
    
    blog_rows = []
    # insert_rows(data, 2)는 data 배열 순서대로 2행부터 차례로 내려가며 삽입함.
    # 따라서 배열의 0번 인덱스가 2행(가장 위)에 위치함. (가장 최신 글이 와야 함)
    for blog_data in blog_data_list:
        blog_rows.append([
            blog_data['date'], 
            blog_data['source'],
            blog_data['title'],
            blog_data['content'],
            blog_data['url']
        ])
    
    if blog_rows:
        print("[Expert_Analytic] 데이터 수집 확인. 기존 데이터를 초기화합니다...")
        clear_sheet_data(sheet, "Expert_Analytic")
        insert_multiple_rows_top(sheet, "Expert_Analytic", blog_rows)


    # === B. 시장 지표 (Market Indicators) ===
    print("  - 시장 지표 데이터 수집중...")
    market_data_list = get_market_data()
    market_rows = []
    for m in market_data_list:
        market_rows.append([
            m['date'],
            m['name'],
            str(m['value']),
            m['status'],
            m['change']
        ])
    
    if market_rows:
        print("[Market_Indicators] 데이터 수집 확인. 기존 데이터를 초기화합니다...")
        clear_sheet_data(sheet, "Market_Indicators")
        insert_multiple_rows_top(sheet, "Market_Indicators", market_rows)

    # === C. 주요 뉴스 (News Calendar) ===
    print("  - 글로벌 및 국내 주요 경제 뉴스 100건 수집중...")
    news_data_list = get_economic_news()
    news_rows = []
    for n in news_data_list:
        news_rows.append([
            n['date'],
            n['category'],
            n['title'],
            n['importance'],
            n['details']
        ])
        
    if news_rows:
        print("[News_Calendar] 데이터 수집 확인. 기존 데이터를 초기화합니다...")
        clear_sheet_data(sheet, "News_Calendar")
        insert_multiple_rows_top(sheet, "News_Calendar", news_rows)

    # === D. Dashboard 업데이트 ===
    print("[3] Dashboard 상태 업데이트...")
    from datetime import timedelta
    now_kst = datetime.utcnow() + timedelta(hours=9)
    now_str = now_kst.strftime("%Y-%m-%d %H:%M:%S")
    update_dashboard(
        sheet, 
        last_updated=now_str, 
        status="Operational (Global 100 News & Full-Text Run)", 
        summary="Gemini AI: 이 셀에 Market_Indicators와 News_Calendar 탭을 읽고 글로벌 시장 요약을 입력해줘."
    )

    print("="*40)
    print("AI-Inv Data Collection Engine Finished")
    print("="*40)

if __name__ == "__main__":
    main()
