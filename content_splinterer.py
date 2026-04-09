"""
바이브코딩 콘텐츠 스플린터링 엔진
- 알렉스 홀모지 프레임워크 적용
- 블로그 1개 -> SNS 콘텐츠 10개+ 자동 생성
- Hook-Retain-Reward 구조 강제 적용
"""
import os
import sys
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup

try:
    import openai
except ImportError:
    print("openai 모듈 필요: pip install openai")
    sys.exit(1)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BLOG_DIR = os.path.join(BASE_DIR, "blog")
SPLINTERED_DIR = os.path.join(BASE_DIR, "splintered_content")

# .env 로드
ENV_PATH = os.path.join(BASE_DIR, "..", "..", "03_마케팅_자동화", ".env")
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.strip() and "=" in line:
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip()

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("OPENAI_API_KEY 필요!")
    sys.exit(1)

client = openai.OpenAI(api_key=API_KEY)

PURCHASE_URL = "https://vibecodingbible.jbooking.kr/"


def extract_blog_text(html_path):
    """블로그 HTML에서 본문 텍스트 추출"""
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    
    title_tag = soup.find("title")
    title = title_tag.text.strip() if title_tag else "바이브코딩 인사이트"
    
    # 본문 텍스트 추출
    for tag in soup.find_all(["script", "style", "nav"]):
        tag.decompose()
    text = soup.get_text(separator="\n", strip=True)
    
    return title, text[:3000]  # 토큰 절약


def generate_instagram_carousel(title, text):
    """인스타그램 캐러셀 카드 5장용 텍스트 생성"""
    prompt = f"""
    아래 블로그 글을 인스타그램 캐러셀 카드 5장 분량으로 변환해주세요.
    
    [블로그 제목]: {title}
    [블로그 본문 요약]: {text[:1500]}
    
    [규칙]
    1. 카드 1: Hook - 강렬한 한 줄 (예: "3천만원 견적서를 받고 울었던 그날...")
    2. 카드 2~4: 핵심 인사이트 3가지 (짧고 임팩트 있게)
    3. 카드 5: CTA - "바이브코딩 바이블 즉시 구매: {PURCHASE_URL}"
    4. 각 카드는 3줄 이내로 작성
    5. 이모지 적극 활용
    6. JSON 배열로 출력: [{{"card": 1, "text": "..."}}, ...]
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=1000
    )
    content = response.choices[0].message.content
    match = re.search(r'\[.*\]', content, re.DOTALL)
    if match:
        return json.loads(match.group())
    return [{"card": 1, "text": content}]


def generate_x_thread(title, text):
    """X(트위터) 스레드 생성 (5개 트윗)"""
    prompt = f"""
    아래 블로그 글을 X(트위터) 스레드 5개로 변환해주세요.
    
    [블로그 제목]: {title}
    [블로그 본문 요약]: {text[:1500]}
    
    [규칙 - 알렉스 홀모지 Hook-Retain-Reward 공식]
    1. 트윗 1 (Hook): 도발적인 첫 줄로 스크롤을 멈추게 함
    2. 트윗 2~3 (Retain): "내가 어떻게 했는지" 스토리 형태
    3. 트윗 4 (Reward): 구체적이고 즉시 실행 가능한 팁 1개
    4. 트윗 5 (CTA): "전체 가이드가 필요하다면: {PURCHASE_URL}"
    5. 각 트윗은 280자 이내
    6. JSON 배열로 출력: [{{"tweet": 1, "text": "..."}}, ...]
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=1000
    )
    content = response.choices[0].message.content
    match = re.search(r'\[.*\]', content, re.DOTALL)
    if match:
        return json.loads(match.group())
    return [{"tweet": 1, "text": content}]


def generate_short_form_script(title, text):
    """30초 숏폼(릴스/쇼츠/틱톡) 대본 생성"""
    prompt = f"""
    아래 블로그 글을 30초 숏폼 영상 대본으로 변환해주세요.
    
    [블로그 제목]: {title}
    [블로그 본문 요약]: {text[:1500]}
    
    [규칙 - Hook-Retain-Reward 구조 필수]
    - Hook (0~3초): 시청자의 스크롤을 멈추는 충격적인 첫 문장
    - Retain (3~25초): 문제 → 해결 스토리 ("나도 똑같았다. 그런데...")
    - Reward (25~30초): 핵심 한 줄 요약 + "링크는 프로필에"
    
    [출력 형식]
    HOOK: (첫 3초 대사)
    RETAIN: (본문 대사)
    REWARD: (마무리 대사 + CTA)
    CAPTION: (영상 설명 + 해시태그 5개)
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8,
        max_tokens=800
    )
    return response.choices[0].message.content


def generate_naver_blog(title, text):
    """네이버 블로그용 포스트 생성 (HTML X, 순수 텍스트)"""
    prompt = f"""
    아래 블로그 글을 네이버 블로그 포스트 형식으로 변환해주세요.
    
    [블로그 제목]: {title}
    [블로그 본문 요약]: {text[:1500]}
    
    [규칙]
    1. 제목은 검색 최적화 (키워드: 바이브코딩, AI 코딩, 비개발자)
    2. 본문은 2000자 내외
    3. 자연스러운 한국어 블로그 톤 (존댓말)
    4. 중간에 구매 유도 자연스럽게 삽입: {PURCHASE_URL}
    5. 하단에 태그 10개 추천
    6. 순수 텍스트로 출력 (HTML 태그 없이)
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=2000
    )
    return response.choices[0].message.content


def generate_newsletter(title, text):
    """이메일 뉴스레터 본문 생성"""
    prompt = f"""
    아래 블로그 글을 이메일 뉴스레터 형식으로 변환해주세요.
    
    [블로그 제목]: {title}
    [블로그 본문 요약]: {text[:1500]}
    
    [규칙]
    1. 제목: 열어보고 싶은 이메일 제목 (호기심 유발)
    2. 본문: 500자 내외 (짧고 임팩트 있게)
    3. PS: "지금 바로 확인하기: {PURCHASE_URL}"
    4. 톤: 친근하지만 전문적인 1인칭
    5. 순수 텍스트로 출력
    """
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=800
    )
    return response.choices[0].message.content


def splinter_latest_blog():
    """가장 최근 블로그를 모든 SNS 포맷으로 스플린터링"""
    if not os.path.exists(BLOG_DIR):
        print("blog 폴더가 없습니다.")
        return
    
    files = sorted([f for f in os.listdir(BLOG_DIR) if f.endswith(".html")], reverse=True)
    if not files:
        print("블로그 파일이 없습니다.")
        return
    
    latest = files[0]
    filepath = os.path.join(BLOG_DIR, latest)
    print(f"\n[Hormozi Engine] 스플린터링 대상: {latest}")
    
    title, text = extract_blog_text(filepath)
    print(f"  제목: {title}")
    
    # 출력 디렉토리
    today = datetime.now().strftime("%Y%m%d_%H%M")
    output_dir = os.path.join(SPLINTERED_DIR, today)
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. 인스타그램 캐러셀
    print("\n[1/5] 인스타그램 캐러셀 카드 생성 중...")
    try:
        insta = generate_instagram_carousel(title, text)
        with open(os.path.join(output_dir, "instagram_carousel.json"), "w", encoding="utf-8") as f:
            json.dump(insta, f, ensure_ascii=False, indent=2)
        print(f"  -> {len(insta)}장 카드 생성 완료")
    except Exception as e:
        print(f"  [실패] {e}")
    
    # 2. X 스레드
    print("[2/5] X(트위터) 스레드 생성 중...")
    try:
        thread = generate_x_thread(title, text)
        with open(os.path.join(output_dir, "x_thread.json"), "w", encoding="utf-8") as f:
            json.dump(thread, f, ensure_ascii=False, indent=2)
        print(f"  -> {len(thread)}개 트윗 생성 완료")
    except Exception as e:
        print(f"  [실패] {e}")
    
    # 3. 숏폼 대본
    print("[3/5] 숏폼(릴스/쇼츠) 대본 생성 중...")
    try:
        script = generate_short_form_script(title, text)
        with open(os.path.join(output_dir, "shortform_script.txt"), "w", encoding="utf-8") as f:
            f.write(script)
        print("  -> 30초 대본 생성 완료")
    except Exception as e:
        print(f"  [실패] {e}")
    
    # 4. 네이버 블로그
    print("[4/5] 네이버 블로그 포스트 생성 중...")
    try:
        naver = generate_naver_blog(title, text)
        with open(os.path.join(output_dir, "naver_blog.txt"), "w", encoding="utf-8") as f:
            f.write(naver)
        print("  -> 네이버 블로그 텍스트 생성 완료")
    except Exception as e:
        print(f"  [실패] {e}")
    
    # 5. 뉴스레터
    print("[5/5] 이메일 뉴스레터 생성 중...")
    try:
        newsletter = generate_newsletter(title, text)
        with open(os.path.join(output_dir, "newsletter.txt"), "w", encoding="utf-8") as f:
            f.write(newsletter)
        print("  -> 뉴스레터 본문 생성 완료")
    except Exception as e:
        print(f"  [실패] {e}")
    
    print(f"\n{'='*55}")
    print(f"[Hormozi Engine] 콘텐츠 스플린터링 완료!")
    print(f"  원본: blog/{latest}")
    print(f"  출력: splintered_content/{today}/")
    print(f"  생성물: 인스타 캐러셀 + X 스레드 + 숏폼 대본")
    print(f"          + 네이버 블로그 + 이메일 뉴스레터")
    print(f"{'='*55}\n")


if __name__ == "__main__":
    splinter_latest_blog()
