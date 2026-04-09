"""
바이브코딩 7일 자동 이메일 너처링 시퀀스
- Day 1: 환영 + 무료 프롬프트 발송
- Day 3: 사회적 증거 (비개발자 87% 성공)
- Day 5: 무료 가치 제공 (n8n 워크플로우)
- Day 7: FOMO + 최종 CTA (한정가 마감)
"""
import os
import sys
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LEADS_FILE = os.path.join(BASE_DIR, "leads.json")
SEQUENCE_LOG = os.path.join(BASE_DIR, "email_sequence_log.json")
PURCHASE_URL = "https://vibecodingbible.jbooking.kr/"

# .env 로드
ENV_PATH = os.path.join(BASE_DIR, "..", "..", "03_마케팅_자동화", ".env")
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.strip() and "=" in line:
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip()


# =========================================================
# 이메일 시퀀스 템플릿 (7일)
# =========================================================

SEQUENCES = {
    1: {
        "subject": "[바이브코딩] AI 프롬프트 5종이 도착했습니다!",
        "body": """
안녕하세요 {name}님!

바이브코딩 바이블에 관심을 가져주셔서 감사합니다.

약속드린 대로, 실전 검증된 AI 프롬프트 5종을 보내드립니다:

1. 텔레그램 자동화 봇 생성 프롬프트
2. 랜딩 페이지 즉시 생성 프롬프트
3. 데이터 분석 대시보드 생성 프롬프트
4. SEO 블로그 자동 생성 프롬프트
5. API 서버 구축 프롬프트

[프롬프트 활용 가이드]
- Claude 또는 ChatGPT에 그대로 복사+붙여넣기 하세요
- 에러가 나면 빨간 화면을 그대로 복사해서 AI에게 던지세요
- 카톡 채팅할 줄 아시면 100% 가능합니다

---

P.S. 이 프롬프트들은 바이브코딩 바이블에 수록된 30종 중 일부입니다.
전체 템플릿 15종 + n8n 워크플로우 + 바이블 본권이 궁금하시다면:

-> {purchase_url}

좋은 하루 되세요!
바이브코딩 바이블 팀 드림
"""
    },
    3: {
        "subject": "[바이브코딩] 비개발자 87%가 성공한 비결",
        "body": """
{name}님, 안녕하세요!

혹시 "나 같은 비개발자가 정말 할 수 있을까?" 고민하고 계신가요?

솔직한 데이터를 공유드립니다:

바이브코딩 바이블 구매자 현황
- 비개발자 비율: 87%
- 평균 평점: 5.0 / 5.0
- 첫 프로젝트 완성 평균 시간: 48시간

[실제 독자 후기]

"3,200만원 견적서를 받고 포기하려다, 이 책을 읽은 다음 날 밤에
혼자서 텔레그램 자동화 봇을 완성했습니다.
지금은 오히려 타 기업에 시스템을 납품하고 있습니다."
— K 대표 (전직 마케터, 코딩 경험 0)

"코딩 부트캠프 6개월 할 돈으로 이 책을 사서
1주일 만에 실제 서비스를 런칭했습니다."
— L님 (직장인, 부업으로 시작)

---

핵심은 '코딩을 배우는 것'이 아니라
'AI에게 지휘하는 법'을 익히는 것입니다.

지금 바로 시작하기: {purchase_url}

바이브코딩 바이블 팀 드림
"""
    },
    5: {
        "subject": "[선물] n8n 자동화 워크플로우를 보내드립니다",
        "body": """
{name}님!

오늘은 특별한 선물을 준비했습니다.

n8n 자동화 워크플로우 1종을 무료로 드립니다:

[이메일 자동 발송 워크플로우]
- Google Sheets에 데이터가 추가되면
- 자동으로 이메일을 발송하는 시스템
- 코딩 없이 드래그 앤 드롭으로 설정 가능

이 워크플로우 하나만으로도 월 50시간의 반복 작업을 자동화할 수 있습니다.

---

그런데 {name}님, 한 가지 질문을 드릴게요.

지금 이 순간에도 경쟁사 대표들은 AI 직원을 고용해서
인건비 0원으로 24시간 시스템을 돌리고 있습니다.

이 격차는 시간이 갈수록 벌어집니다.

바이브코딩 바이블에는 이런 워크플로우가 5종 + 
파이썬 템플릿 15종 + GPT 프롬프트 30종이 들어있습니다.

전체 자동화 키트 확인하기: {purchase_url}

바이브코딩 바이블 팀 드림
"""
    },
    7: {
        "subject": "[긴급] 베타 한정가 마감 안내 (290,000원 → 790,000원)",
        "body": """
{name}님, 중요한 안내입니다.

바이브코딩 바이블 베타 한정가가 곧 종료됩니다.

현재: 290,000원 (63% 할인)
정가: 790,000원

포함 내역:
- 실전 바이블 PDF 200p
- 마스터 파이썬 템플릿 15종 (5,000만원 가치)
- n8n 워크플로우 5종
- GPT 프롬프트 30종
- 100% 무조건 환불 보장

[비용 비교]
- 외주 개발 1회: 1,500만원~
- 코딩 부트캠프: 300~500만원
- AI 인력 채용 (월): 300만원
- 바이브코딩 바이블: 29만원 (평생 소장)

커피 3잔 값으로 월 300만원 인건비를 영구 절약하는 것입니다.

---

7일간 보내드린 무료 콘텐츠로 가능성을 확인하셨을 겁니다.
이제 전체 시스템을 구축할 차례입니다.

지금 바로 구매하기: {purchase_url}

P.S. 100% 환불 보장이니 리스크는 0입니다.
읽고 실행해도 결과가 없으면 전액 환불해 드립니다.

바이브코딩 바이블 팀 드림
"""
    }
}


# =========================================================
# 이메일 발송 함수
# =========================================================

def send_email(to_email, subject, body):
    """SMTP를 통한 이메일 발송"""
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER", "")
    smtp_pass = os.environ.get("SMTP_PASSWORD", "")
    from_name = os.environ.get("SMTP_FROM_NAME", "바이브코딩 바이블")
    
    if not smtp_user or not smtp_pass:
        print(f"  [SKIP] SMTP 미설정 → 이메일 저장만 완료: {to_email}")
        return False
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{smtp_user}>"
    msg["To"] = to_email
    
    # 텍스트 버전
    msg.attach(MIMEText(body, "plain", "utf-8"))
    
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())
        print(f"  [OK] 이메일 발송 성공: {to_email}")
        return True
    except Exception as e:
        print(f"  [FAIL] 이메일 발송 실패: {e}")
        return False


# =========================================================
# 리드 관리
# =========================================================

def load_leads():
    """리드 목록 로드"""
    if not os.path.exists(LEADS_FILE):
        return []
    with open(LEADS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_leads(leads):
    with open(LEADS_FILE, "w", encoding="utf-8") as f:
        json.dump(leads, f, ensure_ascii=False, indent=2)

def add_lead(name, email):
    """새 리드 추가"""
    leads = load_leads()
    # 중복 체크
    if any(l.get("email") == email for l in leads):
        print(f"  [SKIP] 이미 등록된 이메일: {email}")
        return
    leads.append({
        "name": name,
        "email": email,
        "registered": datetime.now().isoformat(),
        "last_sequence": 0,
        "converted": False
    })
    save_leads(leads)
    print(f"  [NEW] 리드 등록: {name} ({email})")


def load_sequence_log():
    if not os.path.exists(SEQUENCE_LOG):
        return {}
    with open(SEQUENCE_LOG, "r", encoding="utf-8") as f:
        return json.load(f)

def save_sequence_log(log):
    with open(SEQUENCE_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


# =========================================================
# 시퀀스 실행 엔진
# =========================================================

def run_email_sequence():
    """모든 리드에 대해 7일 이메일 시퀀스 실행"""
    leads = load_leads()
    log = load_sequence_log()
    now = datetime.now()
    
    print(f"\n{'='*55}")
    print(f"  이메일 너처링 시퀀스 실행")
    print(f"  현재 리드: {len(leads)}명")
    print(f"{'='*55}\n")
    
    sent_count = 0
    
    for lead in leads:
        email = lead.get("email")
        name = lead.get("name", "고객")
        registered = datetime.fromisoformat(lead.get("registered", now.isoformat()))
        days_since = (now - registered).days
        
        if lead.get("converted"):
            continue
        
        email_log = log.get(email, {})
        
        for day, template in sorted(SEQUENCES.items()):
            day_key = f"day_{day}"
            
            # 이미 발송했으면 스킵
            if email_log.get(day_key):
                continue
            
            # 해당 일수가 지났는지 확인
            if days_since >= day - 1:  # Day 1은 즉시, Day 3은 2일 후...
                subject = template["subject"]
                body = template["body"].format(
                    name=name,
                    purchase_url=PURCHASE_URL
                )
                
                print(f"[Day {day}] {name} ({email})")
                success = send_email(email, subject, body)
                
                # 발송 로그 기록
                if email not in log:
                    log[email] = {}
                log[email][day_key] = {
                    "sent": now.isoformat(),
                    "success": success
                }
                
                lead["last_sequence"] = day
                sent_count += 1
                break  # 하루에 한 통만 발송
    
    save_leads(leads)
    save_sequence_log(log)
    
    print(f"\n[결과] {sent_count}통 이메일 처리 완료")
    print(f"[TIP] SMTP를 설정하려면 .env에 추가하세요:")
    print(f"  SMTP_USER=your@gmail.com")
    print(f"  SMTP_PASSWORD=your_app_password")
    print(f"  SMTP_SERVER=smtp.gmail.com")
    print(f"  SMTP_PORT=587")


# =========================================================
# 리드 대시보드
# =========================================================

def show_dashboard():
    """리드 현황 대시보드"""
    leads = load_leads()
    log = load_sequence_log()
    
    print(f"\n{'='*55}")
    print(f"  바이브코딩 리드 대시보드")
    print(f"{'='*55}")
    print(f"\n  총 리드: {len(leads)}명")
    
    converted = sum(1 for l in leads if l.get("converted"))
    print(f"  전환(구매): {converted}명")
    print(f"  전환율: {(converted/len(leads)*100) if leads else 0:.1f}%")
    
    print(f"\n  시퀀스 진행 현황:")
    for day in [1, 3, 5, 7]:
        count = sum(1 for l in leads if l.get("last_sequence", 0) >= day)
        bar = "#" * (count * 2)
        print(f"    Day {day}: [{bar:<20}] {count}명")
    
    print(f"\n  최근 등록 리드:")
    for lead in leads[-5:]:
        print(f"    - {lead.get('name')} ({lead.get('email')}) | Day {lead.get('last_sequence', 0)}")
    print()


# =========================================================
# CLI
# =========================================================

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "add" and len(sys.argv) >= 4:
            add_lead(sys.argv[2], sys.argv[3])
        elif cmd == "run":
            run_email_sequence()
        elif cmd == "dashboard":
            show_dashboard()
        else:
            print("사용법:")
            print("  python email_nurture.py add <이름> <이메일>")
            print("  python email_nurture.py run")
            print("  python email_nurture.py dashboard")
    else:
        # 기본: 시퀀스 실행
        run_email_sequence()
