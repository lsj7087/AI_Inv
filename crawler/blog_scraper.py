import requests
from bs4 import BeautifulSoup
from datetime import datetime
import xml.etree.ElementTree as ET
import pytz

KST = pytz.timezone('Asia/Seoul')

def parse_naver_blog_post(url):
    """
    개별 네이버 블로그 포스트의 모바일 URL을 파싱하여 본문(전체)을 가져옵니다.
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'
    }
    
    # 모바일 URL로 강제 변환하여 iframe 우회
    if "m.blog.naver.com" not in url:
        url = url.replace("blog.naver.com", "m.blog.naver.com")
        
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        # 본문 내용 추출
        content_tags = soup.find_all('div', class_='se-module-text')
        content_text = ""
        for tag in content_tags:
            content_text += tag.get_text(separator=' ', strip=True) + "\n"
            
        # 만약 se-module-text 가 없으면 다른 클래스명 체크 (구버전 에디터 등)
        if not content_text.strip():
            post_body = soup.find('div', id='viewTypeSelector')
            if post_body:
                content_text = post_body.get_text(separator=' ', strip=True)
                
        # 최대 글자수 다소 넉넉하게 40000자로 컷 (구글 시트 한 셀 글자수 제한: 50,000자)
        return content_text.strip()[:40000]
    except Exception as e:
        print(f"개별 포스트 수집 오류 ({url}): {e}")
        return "본문 파싱 실패"

def get_latest_post_ranto28():
    """
    Naver Blog (ranto28)의 RSS 피드에서 최신 20개 포스트를 가져옵니다.
    본문은 해당 URL을 방문하여 긁어옵니다.
    """
    rss_url = "https://rss.blog.naver.com/ranto28.xml"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    results = []
    
    try:
        res = requests.get(rss_url, headers=headers, timeout=10)
        res.raise_for_status()
        
        # XML 파싱
        root = ET.fromstring(res.text)
        items = root.findall('.//item')
        
        # 최대 20개 (보통 RSS 기본 출력이 20개 내외)
        for i, item in enumerate(items[:20]):
            title_el = item.find('title')
            link_el = item.find('link')
            pubDate_el = item.find('pubDate')
            
            title = title_el.text if title_el is not None else "제목 없음"
            link = link_el.text if link_el is not None else ""
            pub_date_raw = pubDate_el.text if pubDate_el is not None else ""
            
            # pubDate 포맷 추출
            # 예: "Wed, 08 Apr 2026 08:20:40 +0900"
            try:
                dt = datetime.strptime(pub_date_raw, "%a, %d %b %Y %H:%M:%S %z")
                date_str = dt.strftime("%Y-%m-%d %H:%M")
            except Exception:
                date_str = datetime.now(KST).strftime("%Y-%m-%d %H:%M")  # 파싱 실패시 현재 시간
                
            print(f"[{i+1}/20] 블로그 본문 수집 중: {title}")
            full_content = parse_naver_blog_post(link)
            
            results.append({
                'date': date_str,
                'source': 'Naver(ranto28)',
                'title': title,
                'content': full_content,
                'url': link
            })
            
    except Exception as e:
        print(f"[RSS 파싱] 수집 오류: {e}")
        results.append({
            'date': datetime.now(KST).strftime("%Y-%m-%d %H:%M"),
            'source': 'Naver(ranto28)',
            'title': '수집 실패',
            'content': str(e),
            'url': rss_url
        })
        
    return results

if __name__ == "__main__":
    posts = get_latest_post_ranto28()
    print(f"수집된 포스트 수: {len(posts)}")
    if posts:
        print(f"최상단 포스트: {posts[0]['title']}")
        print(f"본문 길이: {len(posts[0]['content'])}")
