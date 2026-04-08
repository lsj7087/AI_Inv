# 🤖 AI-Inv — 글로벌 매크로 AI 투자 비서

> GitHub Actions로 자동 수집 → Google Sheets 저장 → Gemini AI 분석까지  
> **완전 자동화된 개인 투자 의사결정 시스템**

---

## 📌 프로젝트 소개

AI-Inv는 매일 KST 오전 7시부터 밤 11시까지 2시간마다 스스로 깨어나, 전 세계 금융 데이터를 긁어모으고 구글 시트에 정리한 뒤, Gemini Gems AI 비서가 당신만을 위한 투자 브리핑을 제공하는 자동화 파이프라인입니다.

---

## 🏗️ 시스템 구성

```
GitHub Actions (2시간 자동 실행)
    │
    ├─── 🕷️ [크롤러 3종]
    │       ├── blog_scraper.py      → 전문가 블로그 본문 20건 (RSS)
    │       ├── market_indicator.py  → 글로벌 지표 51개 + 8단계 변동폭
    │       └── finance_scraper.py   → 5개 매체 뉴스 최대 100건 (Full Text)
    │
    └─── 📊 [Google Sheets - 데이터 웨어하우스]
            ├── Dashboard           → 수집 상태 모니터링
            ├── Expert_Analytic     → 전문가 블로그 20건 스냅샷
            ├── Market_Indicators   → 글로벌 51개 지표 스냅샷
            └── News_Calendar       → 글로벌 뉴스 100건 스냅샷
                    │
                    └─── 💎 [Gemini Gems AI 비서]
                            → 3인 위원회 토론 + 매수/매도 조언 출력
```

---

## 📦 수집 데이터 상세

### 🏦 Market Indicators — 51개 글로벌 지표
각 종목의 **현재가**와 **1h / 2h / 6h / 12h / 24h / 7d / 30d / 60d 전 대비 변동폭(%)** 동시 수집

| 카테고리 | 수집 종목 |
|---|---|
| 증시·변동성 | KOSPI, KOSDAQ, S&P500, NASDAQ, Dow Jones, Russell2000, VIX, Nikkei225, HSI, 상해종합, Euro Stoxx50 |
| 금리·채권 | 미국 10년/30년물 국채금리 |
| 환율 | DXY, 원/달러, 유로/달러, 엔/달러, 위안/달러, 파운드/달러 |
| 원자재 | WTI, 브렌트유, 천연가스, 금, 은, 구리, 옥수수 |
| 암호화폐 | 비트코인, 이더리움, 솔라나 |
| 메가테크·ETF | AAPL, MSFT, GOOGL, AMZN, NVDA, META, TSLA, TSM, ASML, AVGO, SPY, SOXX |
| 국내 우량주 | 삼성전자, SK하이닉스, 현대차, 기아, 삼성바이오, 셀트리온, 네이버, 카카오 |
| 심리 지표 | CNN Fear & Greed Index |

### 📰 News Calendar — 5개 채널, 최대 100건 Full Text 수집

| 채널 | 종류 | 방식 |
|---|---|---|
| CNN Business | 해외 | 공식 RSS |
| Reuters | 해외 | Google News RSS 우회 |
| Financial Juice | 해외 | 실시간 속보 헤드라인 |
| 네이버 금융 | 국내 | 웹 스크래핑 |
| 매일경제(MK) | 국내 | 공식 RSS |

### 📝 Expert Analytic — 블로그 본문 20건
- 대상: 네이버 파워 투자 블로거 **ranto28**
- RSS 기반 최신 20건 본문 전문(Full Text) 수집

---

## 🚀 시작하기

### 1. 리포지토리 Fork 또는 Clone

### 2. Google Cloud 서비스 계정 설정
1. [Google Cloud Console](https://console.cloud.google.com) → 서비스 계정 생성
2. Google Sheets API & Google Drive API 활성화
3. 서비스 계정에 스프레드시트 편집 권한 부여

### 3. GitHub Secrets 설정
리포지토리 → **Settings → Secrets and variables → Actions → New repository secret**

| Secret 이름 | 값 |
|---|---|
| `GOOGLE_SERVICE_ACCOUNT_JSON` | 서비스 계정 JSON 파일 전체 내용 |
| `SPREADSHEET_ID` | 본인의 구글 스프레드시트 ID |

### 4. 파일 업로드
아래 파일들을 GitHub에 업로드하세요. (`.github` 폴더는 웹 에디터에서 직접 생성)

```
✅ 올려야 할 파일
├── crawler/blog_scraper.py
├── crawler/market_indicator.py
├── crawler/finance_scraper.py
├── uploader/sheets_api.py
├── main.py
├── requirements.txt
└── .github/workflows/daily_collect.yml    ← 웹 에디터에서 직접 생성

❌ 절대 올리면 안 되는 파일
└── [서비스 계정].json                      ← 해킹 위험!
```

### 5. 수동 실행 테스트
GitHub → **Actions 탭** → **Daily Data Collect for AI-Inv** → **Run workflow** 클릭

---

## 💎 Gemini Gems 연동

1. [Google Gemini](https://gemini.google.com) 접속 → **Gems** 메뉴
2. **새 Gem 만들기** → 이름: `AI 투자 비서`
3. `Gems_시스템_프롬프트.txt` 파일의 내용을 **지침(Instructions)** 칸에 붙여넣기
4. 저장 후 대화창에 `"오늘 장 어때?"` 입력

Gems가 스프레드시트를 직접 읽어와 **3인 위원회 토론 + 매수/매도 조언**을 브리핑합니다.

---

## ⏱️ 자동화 스케줄 (KST 기준)

| 시각 | 의미 |
|---|---|
| 07:00 | 국내 개장 전 데이터 준비 |
| 09:00 | 국내 장 초반 |
| 11:00 ~ 15:00 | 국내 장중 추적 |
| 17:00 | 미국 프리마켓 시작 |
| 21:00 ~ 23:00 | 미국 본장 추적 |
| 00:00 ~ 06:00 | 🌙 휴식 (IP 차단 방어) |

---

## 🛠️ 기술 스택

| 종류 | 기술 |
|---|---|
| 언어 | Python 3.10 |
| 스케줄러 | GitHub Actions (ubuntu-latest) |
| 데이터 저장 | Google Sheets API (gspread) |
| 시장 데이터 | yfinance |
| 웹 스크래핑 | requests, BeautifulSoup4, lxml |
| 타임존 처리 | pytz (Asia/Seoul — 서버 위치 무관) |
| AI 분석 | Gemini Gems (Google) |

---

## ⚠️ 주의사항

- **서비스 계정 JSON 파일을 절대 GitHub에 올리지 마세요.** (해킹 시 구글 계정 전체 위험)
- Reuters, Financial Juice는 봇 차단이 강력하여 일부 기사는 헤드라인/요약으로 대체될 수 있습니다.
- GitHub 무료 계정은 월 2,000분의 Actions 실행 시간 제공. 리포지토리를 **Public**으로 설정하면 무제한 무료입니다.
- yfinance의 `1h interval`은 최대 730일 데이터까지 지원합니다.

---

## 📜 License

MIT License — 자유롭게 사용, 수정, 배포 가능합니다.
