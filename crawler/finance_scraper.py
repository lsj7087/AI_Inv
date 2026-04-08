import requests
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.ElementTree as ET
import pytz

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
}

KST = pytz.timezone('Asia/Seoul')

def extract_general_body(url):
    """
    일반적인 기사 URL에서 <p> 태그를 기반으로 본문을 최대한 추출합니다.
    (블로킹 당할 경우나 파싱 실패 시 예외 처리)
    """
    try:
        res = requests.get(url, headers=HEADERS, timeout=8)
        if res.status_code != 200:
            return f"접근 차단 (HTTP {res.status_code})"
            
        # 일부 한글 사이트 인코딩 대비
        if 'naver.com' in url or 'mk.co.kr' in url:
            res.encoding = 'euc-kr' if 'naver.com' in url else 'utf-8'
            
        soup = BeautifulSoup(res.text, 'html.parser')
        paragraphs = soup.find_all('p')
        
        body = []
        for p in paragraphs:
            text = p.get_text(separator=' ', strip=True)
            if len(text) > 20: # 너무 짧은 메뉴 텍스트 제외
                body.append(text)
                
        # 특수 매체 (네이버 등) 구조 대응
        if not body and 'naver.com' in url:
            div = soup.find('div', id='newsct_article') or soup.find('div', id='articleBodyContents')
            if div:
                body.append(div.get_text(separator=' ', strip=True))
                
        if not body:
            return "본문 파싱 불가(단문 속보이거나 자바스크립트 렌더링 페이지)"
            
        full_text = "\n".join(body)
        return full_text[:40000] # 구글 시트 셀 한도 방어
    except Exception as e:
        return f"파싱 에러: {e}"

def parse_rss_to_dicts(feed_url, category_name, max_items=20):
    """
    RSS(XML) 피드에서 기사 리스트를 파싱하여 형식화합니다.
    """
    results = []
    today_str = datetime.now(KST).strftime("%Y-%m-%d %H:%M")
    
    try:
        res = requests.get(feed_url, headers=HEADERS, timeout=10)
        res.raise_for_status()
        root = ET.fromstring(res.text)
        items = root.findall('.//item')
        
        for item in items[:max_items]:
            title_el = item.find('title')
            link_el = item.find('link')
            desc_el = item.find('description')
            
            title = title_el.text.strip() if title_el is not None else ""
            link = link_el.text.strip() if link_el is not None else ""
            desc = desc_el.text.strip() if desc_el is not None else ""
            
            # 본문 직접 스크래핑 시도
            print(f"[{category_name}] 본문 추출 시도: {title[:20]}...")
            body = extract_general_body(link)
            
            # 본문에 실패하면 description으로 대체
            if "접근 차단" in body or "파싱 에러" in body or "파싱 불가" in body:
                body = desc if len(desc) > len(body) else body
                
            results.append({
                'date': today_str,
                'category': category_name,
                'title': title,
                'importance': 'RAW',
                'details': body
            })
    except Exception as e:
        print(f"[{category_name}] RSS 파싱 에러: {e}")
    return results

def get_financial_juice():
    """
    Financial Juice는 RSS가 없고 동적 렌더링이 심한 플랫폼.
    대체: HTML 내의 title 태그들을 수집하거나, 
    정적 페이지 버전이 없으므로 야후 파이낸스 속보로 일부 대체하거나 제한적 파싱 시도.
    """
    results = []
    today_str = datetime.now(KST).strftime("%Y-%m-%d %H:%M")
    url = "https://www.financialjuice.com/home"
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # Financial Juice는 기본적으로 SPA(Single Page App)이라 초기 HTML에 속보가 없음
        # 따라서 안내 문구 및 헤드라인 몇개만 잡힐 수 있음.
        headlines = soup.find_all('h3') or soup.find_all('div', class_='headline')
        
        for i, h in enumerate(headlines[:20]):
            text = h.get_text(strip=True)
            if len(text) > 10:
                results.append({
                    'date': today_str,
                    'category': 'FinancialJuice (News)',
                    'title': text,
                    'importance': 'RAW',
                    'details': "FinancialJuice는 실시간 단문 터미널로 본문이 별도 존재하지 않음."
                })
        
        # 만약 동적 렌더링이라 비어있다면, 사용자 안내용 한 건 전송
        if not results:
             results.append({
                'date': today_str,
                'category': 'FinancialJuice (News)',
                'title': 'API/동적 렌더링 제한 알림',
                'importance': 'Info',
                'details': 'FinancialJuice 본문은 Javascript 렌더링에 의존하여 현재 텍스트 환경에서 차단됨.'
            })
    except Exception as e:
        print(f"FinancialJuice 에러: {e}")
    
    return results

def get_naver_news(max_items=20):
    url = "https://finance.naver.com/news/mainnews.naver"
    results = []
    today_str = datetime.now(KST).strftime("%Y-%m-%d %H:%M")
    
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.encoding = 'euc-kr' 
        soup = BeautifulSoup(res.text, 'html.parser')
        
        news_list = soup.select('.newsList li')
        for item in news_list[:max_items]:
            title_tag = item.select_one('dd.articleSubject a') or item.select_one('dt.articleSubject a')
            if title_tag:
                title = title_tag.text.strip()
                link = "https://finance.naver.com" + title_tag['href']
                
                print(f"[네이버 경제뉴스] 본문 추출 중: {title[:20]}...")
                body = extract_general_body(link)
                
                results.append({
                    'date': today_str,
                    'category': '네이버 경제뉴스',
                    'title': title,
                    'importance': 'RAW',
                    'details': body
                })
    except Exception as e:
        print(f"[네이버] 뉴스 파싱 에러: {e}")
    return results

def get_economic_news():
    """
    5개 소스에서 각각 최대 20건씩(총 100건) 뉴스 본문을 수집합니다.
    1. CNN (RSS 기반)
    2. Reuters (구글 뉴스 RSS 우회)
    3. FinancialJuice (구조 한계로 헤드라인만 시도)
    4. Naver 경제뉴스 (웹 스크래핑)
    5. MK 매일경제 증권 (RSS 기반)
    """
    total_news = []
    
    # 1. CNN
    cnn_rss = "http://rss.cnn.com/rss/edition_business.rss"
    total_news.extend(parse_rss_to_dicts(cnn_rss, "CNN Business", 20))
    
    # 2. Reuters (구글 뉴스 RSS 우회 검색)
    reuters_rss = "https://news.google.com/rss/search?q=when:24h+site:reuters.com&hl=en-US&gl=US&ceid=US:en"
    total_news.extend(parse_rss_to_dicts(reuters_rss, "Reuters (Global)", 20))
    
    # 3. Financial Juice
    total_news.extend(get_financial_juice()[:20])
    
    # 4. Naver 경제뉴스
    total_news.extend(get_naver_news(20))
    
    # 5. 매일경제 마켓 (MK)
    mk_rss = "https://www.mk.co.kr/rss/40300001/" # 증권 RSS
    total_news.extend(parse_rss_to_dicts(mk_rss, "매일경제 마켓(MK)", 20))
    
    return total_news

if __name__ == "__main__":
    news = get_economic_news()
    print(f"Total collected: {len(news)}")
