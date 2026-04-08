import requests
import yfinance as yf
import pytz
from datetime import datetime, timedelta

KST = pytz.timezone('Asia/Seoul')

def get_fear_and_greed():
    """
    CNN Fear & Greed Index를 가져옵니다.
    """
    url = "https://production.dataviz.cnn.io/index/fearandgreed/graphdata"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': 'application/json'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            score = data.get('fear_and_greed', {}).get('score')
            rating = data.get('fear_and_greed', {}).get('rating')
            if score is not None:
                return float(score), rating
    except Exception as e:
        print(f"Fear & Greed Index 수집 오류: {e}")
    return None, "수집 실패"

def calculate_changes(hist_df):
    """
    yfinance의 시간 단위 데이터프레임을 받아서
    1h, 2h, 6h, 12h, 24h, 7d, 30d, 60d 전 종가 대비 변동폭을 계산합니다.
    """
    if hist_df is None or hist_df.empty:
        return "데이터 없음"
        
    current_time = hist_df.index[-1]
    current_price = hist_df['Close'].iloc[-1]
    
    # 시간 오프셋 설정 (Label, Hours)
    # yfinance의 1h 간격은 최장 730일까지 지원하므로 시간단위 탐색 가능
    time_targets = [
        ('1h', 1),
        ('2h', 2),
        ('6h', 6),
        ('12h', 12),
        ('24h', 24),
        ('7d', 7 * 24),
        ('30d', 30 * 24),
        ('60d', 60 * 24)
    ]
    
    changes = []
    
    for label, hours_diff in time_targets:
        target_time = current_time - timedelta(hours=hours_diff)
        
        # target_time 이전의 데이터 중 가장 최근 데이터 (과거 역방향 탐색)
        past_data = hist_df[hist_df.index <= target_time]
        
        if not past_data.empty:
            past_price = past_data['Close'].iloc[-1]
            change_pct = ((current_price - past_price) / past_price) * 100
            changes.append(f"({label}전:{change_pct:+.2f}%)")
        else:
            changes.append(f"({label}전:N/A)")
            
    return " ".join(changes)

def get_market_data():
    """
    주요 지표들의 현재값 및 1, 2, 6, 12, 24시간, 7, 30, 60일 변동을 가져옵니다.
    """
    tickers = {
        # [1] 증시 및 변동성
        'KOSPI': '^KS11',
        'KOSDAQ': '^KQ11',
        'S&P 500': '^GSPC',
        'NASDAQ 종합': '^IXIC',
        'Dow Jones 산업평균': '^DJI',
        'Russell 2000 (중소형)': '^RUT',
        'VIX (변동성 지수)': '^VIX',
        'Nikkei 225 (일본)': '^N225',
        'Hang Seng (홍콩)': '^HSI',
        '상해종합 (중국)': '000001.SS',
        'Euro Stoxx 50': '^STOXX50E',
        
        # [2] 금리 (채권)
        'US 10년물 국채금리': '^TNX',
        'US 30년물 국채금리': '^TYX',
        
        # [3] 환율 및 달러인덱스
        '달러 인덱스 (DXY)': 'DX-Y.NYB',
        '원/달러 환율': 'KRW=X',
        '유로/달러 환율': 'EURUSD=X',
        '엔/달러 환율': 'JPY=X',
        '위안/달러 환율': 'CNY=X',
        '파운드/달러 환율': 'GBPUSD=X',
        
        # [4] 원자재
        'WTI 원유': 'CL=F',
        '브렌트유 (Brent)': 'BZ=F',
        '천연가스 (Nat Gas)': 'NG=F',
        '금 (Gold)': 'GC=F',
        '은 (Silver)': 'SI=F',
        '구리 (Copper)': 'HG=F',
        '옥수수 (Corn)': 'ZC=F',
        
        # [5] 암호화폐
        '비트코인 (BTC)': 'BTC-USD',
        '이더리움 (ETH)': 'ETH-USD',
        '솔라나 (SOL)': 'SOL-USD',
        
        # [6] 메가테크 & AI 리더
        'Apple': 'AAPL',
        'Microsoft': 'MSFT',
        'Alphabet (Google)': 'GOOGL',
        'Amazon': 'AMZN',
        'NVIDIA': 'NVDA',
        'Meta': 'META',
        'Tesla': 'TSLA',
        'TSMC': 'TSM',
        'ASML': 'ASML',
        'Broadcom': 'AVGO',
        'SPY (S&P500 ETF)': 'SPY',
        'SOXX (반도체 ETF)': 'SOXX',
        
        # [7] 국내 우량주
        '삼성전자': '005930.KS',
        'SK하이닉스': '000660.KS',
        '현대차': '005380.KS',
        '기아': '000270.KS',
        '삼성바이오로직스': '207940.KS',
        '셀트리온': '068270.KS',
        '네이버 (NAVER)': '035420.KS',
        '카카오 (KAKAO)': '035720.KS'
    }
    results = []
    now_str = datetime.now(KST).strftime("%Y-%m-%d %H:%M")
    # 1. CNN Fear & Greed
    score, rating = get_fear_and_greed()
    if score is not None:
        results.append({
            'date': now_str,
            'name': 'CNN Fear & Greed',
            'value': str(round(score, 1)),
            'status': rating,
            'change': '(시간별 데이터 비지원, 현재 점수만 출력)'
        })
        
    # 2. yfinance 데이터
    for name, symbol in tickers.items():
        try:
            ticker = yf.Ticker(symbol)
            # 최근 1개월(1h interval의 최대 허용치는 보통 730d지만 넉넉하게 1mo 요청) 중 최근 30개 행만 사용해도 다 커버됨.
            hist = ticker.history(period="1mo", interval="1h")
            
            if len(hist) >= 1:
                current_price = hist['Close'].iloc[-1]
                
                # 변동폭 텍스트 추출
                change_str = calculate_changes(hist)
                
                # 포맷팅
                if '환율' in name:
                    formatter = f"{current_price:,.2f}"
                elif '주가' in name or '삼성전자' in name or 'SK하이닉스' in name:
                    formatter = f"{int(current_price):,}"
                else:
                    formatter = f"{current_price:,.2f}"
                    
                results.append({
                    'date': now_str,
                    'name': name,
                    'value': formatter,
                    'status': 'Raw Data', # AI가 판단하므로 단순 상태 반환
                    'change': change_str
                })
            else:
                raise Exception("조회된 데이터가 없습니다.")
                
        except Exception as e:
            print(f"[{name}] 수집 오류: {e}")
            results.append({
                'date': now_str,
                'name': name,
                'value': '수집 실패',
                'status': 'Error',
                'change': str(e)
            })
            
    return results

if __name__ == "__main__":
    for item in get_market_data():
        print(f"{item['name']}: {item['value']} | {item['change']}")
