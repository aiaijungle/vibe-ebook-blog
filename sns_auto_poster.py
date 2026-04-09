"""
바이브코딩 인스타그램 + 쓰레드 자동화 엔진
- 인스타 캐러셀 이미지 자동 생성 (Pillow)
- 쓰레드(Threads) API 자동 포스팅
- 블로그 -> 스플린터링 -> SNS 포스팅 완전 자동화
"""
import os
import sys
import json
import textwrap
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SPLINTERED_DIR = os.path.join(BASE_DIR, "splintered_content")
INSTA_OUTPUT_DIR = os.path.join(BASE_DIR, "instagram_ready")
PURCHASE_URL = "https://vibecodingbible.jbooking.kr/"

# =========================================================
# 1. 인스타그램 캐러셀 이미지 자동 생성
# =========================================================

# 카드별 그라디언트 색상 세트
CARD_THEMES = [
    {"bg_top": (25, 10, 55), "bg_bottom": (10, 10, 30), "accent": (200, 120, 255), "label": "HOOK"},
    {"bg_top": (10, 30, 60), "bg_bottom": (5, 15, 35), "accent": (76, 201, 240), "label": "INSIGHT"},
    {"bg_top": (40, 10, 50), "bg_bottom": (15, 5, 25), "accent": (255, 120, 200), "label": "INSIGHT"},
    {"bg_top": (10, 40, 40), "bg_bottom": (5, 20, 20), "accent": (80, 240, 180), "label": "INSIGHT"},
    {"bg_top": (50, 20, 10), "bg_bottom": (25, 10, 5), "accent": (255, 180, 80), "label": "CTA"},
]


def create_gradient(draw, width, height, top_color, bottom_color):
    """세로 그라디언트 배경 생성"""
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def get_font(size):
    """시스템 폰트 로드 (한글 지원)"""
    font_paths = [
        "C:/Windows/Fonts/malgun.ttf",      # 맑은 고딕
        "C:/Windows/Fonts/malgunbd.ttf",     # 맑은 고딕 Bold
        "C:/Windows/Fonts/NanumGothicBold.ttf",
        "C:/Windows/Fonts/gulim.ttc",
    ]
    for fp in font_paths:
        if os.path.exists(fp):
            return ImageFont.truetype(fp, size)
    return ImageFont.load_default()


def draw_rounded_rect(draw, xy, radius, fill, outline=None):
    """둥근 모서리 사각형"""
    x1, y1, x2, y2 = xy
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline)


def generate_card_image(card_num, text, theme, output_path):
    """인스타그램 캐러셀 카드 1장 생성 (1080x1080)"""
    W, H = 1080, 1080
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    
    # 그라디언트 배경
    create_gradient(draw, W, H, theme["bg_top"], theme["bg_bottom"])
    
    # 상단 악센트 라인
    draw.rectangle([(0, 0), (W, 6)], fill=theme["accent"])
    
    # 카드 번호 뱃지
    badge_font = get_font(24)
    badge_text = f"{card_num}/5"
    draw.rounded_rectangle([(40, 40), (130, 80)], radius=20, 
                           fill=(*theme["accent"], 60), outline=theme["accent"])
    draw.text((60, 48), badge_text, fill=(255, 255, 255), font=badge_font)
    
    # 라벨 (HOOK / INSIGHT / CTA)
    label_font = get_font(20)
    label = theme["label"]
    draw.text((W - 140, 50), label, fill=theme["accent"], font=label_font)
    
    # 메인 텍스트
    main_font = get_font(42)
    margin = 80
    max_width = W - margin * 2
    
    # 텍스트 줄바꿈
    lines = []
    for paragraph in text.split("\n"):
        wrapped = textwrap.wrap(paragraph, width=18)  # 한글 기준 약 18자
        lines.extend(wrapped if wrapped else [""])
    
    # 텍스트 세로 중앙 정렬
    line_height = 60
    total_text_height = len(lines) * line_height
    y_start = (H - total_text_height) // 2
    
    for i, line in enumerate(lines):
        y = y_start + i * line_height
        draw.text((margin, y), line, fill=(255, 255, 255), font=main_font)
    
    # 하단 브랜딩
    brand_font = get_font(22)
    draw.text((margin, H - 80), "VIBECODING BIBLE", fill=(*theme["accent"],), font=brand_font)
    draw.text((margin, H - 50), "vibecodingbible.jbooking.kr", fill=(180, 180, 180), font=get_font(18))
    
    # 하단 장식 라인
    draw.rectangle([(0, H - 6), (W, H)], fill=theme["accent"])
    
    img.save(output_path, "PNG", quality=95)
    return output_path


def generate_carousel_images(splintered_dir):
    """스플린터링된 인스타 캐러셀 JSON → 이미지 5장 자동 생성"""
    json_path = os.path.join(splintered_dir, "instagram_carousel.json")
    if not os.path.exists(json_path):
        print("instagram_carousel.json 파일을 찾을 수 없습니다.")
        return []
    
    with open(json_path, "r", encoding="utf-8") as f:
        cards = json.load(f)
    
    # 출력 디렉토리
    timestamp = os.path.basename(splintered_dir)
    output_dir = os.path.join(INSTA_OUTPUT_DIR, timestamp)
    os.makedirs(output_dir, exist_ok=True)
    
    generated = []
    for i, card in enumerate(cards):
        card_text = card.get("text", "")
        theme = CARD_THEMES[i % len(CARD_THEMES)]
        output_path = os.path.join(output_dir, f"card_{i+1}.png")
        
        generate_card_image(i + 1, card_text, theme, output_path)
        generated.append(output_path)
        print(f"  [카드 {i+1}/5] 생성 완료 -> {os.path.basename(output_path)}")
    
    # 캡션 파일도 함께 저장
    caption = "🔥 바이브코딩으로 AI 시대를 선점하세요!\n\n"
    for card in cards:
        caption += f"➡️ {card.get('text', '')[:50]}...\n"
    caption += f"\n📘 지금 바로 시작하기: {PURCHASE_URL}\n"
    caption += "\n#바이브코딩 #AI창업 #프롬프트엔지니어링 #비개발자코딩 #클로드코드 #AI자동화 #1인창업 #전자책 #사이드프로젝트 #코딩없이개발"
    
    with open(os.path.join(output_dir, "caption.txt"), "w", encoding="utf-8") as f:
        f.write(caption)
    
    return generated


# =========================================================
# 2. 쓰레드(Threads) 자동 포스팅
# =========================================================

def post_to_threads_manual(splintered_dir):
    """쓰레드 포스팅용 텍스트 준비 (복붙 자동화)
    
    Threads API가 아직 제한적이므로, 
    '복사 → 붙여넣기' 할 수 있는 최적화된 텍스트를 생성합니다.
    향후 Threads API 정식 지원 시 자동 포스팅으로 전환.
    """
    json_path = os.path.join(splintered_dir, "x_thread.json")
    if not os.path.exists(json_path):
        print("x_thread.json 파일을 찾을 수 없습니다.")
        return
    
    with open(json_path, "r", encoding="utf-8") as f:
        tweets = json.load(f)
    
    timestamp = os.path.basename(splintered_dir)
    output_dir = os.path.join(BASE_DIR, "threads_ready", timestamp)
    os.makedirs(output_dir, exist_ok=True)
    
    # 개별 쓰레드 포스트 파일 생성
    for i, tweet in enumerate(tweets):
        text = tweet.get("text", "")
        filepath = os.path.join(output_dir, f"thread_{i+1}.txt")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"  [쓰레드 {i+1}/5] 준비 완료")
    
    # 전체 스레드를 하나로 합친 파일 (한번에 복붙용)
    combined = ""
    for i, tweet in enumerate(tweets):
        combined += f"--- 포스트 {i+1} ---\n"
        combined += tweet.get("text", "") + "\n\n"
    
    with open(os.path.join(output_dir, "full_thread.txt"), "w", encoding="utf-8") as f:
        f.write(combined)
    
    return output_dir


def post_to_threads_api(splintered_dir):
    """Threads API 자동 포스팅 (Meta Graph API v21.0+)
    
    사전 준비:
    1. Meta Developer 앱 생성 (developers.facebook.com)
    2. threads_basic, threads_content_publish 권한 취득
    3. .env 파일에 THREADS_ACCESS_TOKEN, THREADS_USER_ID 추가
    """
    access_token = os.environ.get("THREADS_ACCESS_TOKEN")
    user_id = os.environ.get("THREADS_USER_ID")
    
    if not access_token or not user_id:
        print("  [INFO] THREADS_ACCESS_TOKEN / THREADS_USER_ID가 .env에 없습니다.")
        print("  [INFO] 수동 포스팅 모드로 전환합니다.")
        return post_to_threads_manual(splintered_dir)
    
    import requests
    
    json_path = os.path.join(splintered_dir, "x_thread.json")
    with open(json_path, "r", encoding="utf-8") as f:
        tweets = json.load(f)
    
    base_url = f"https://graph.threads.net/v1.0/{user_id}/threads"
    
    posted_ids = []
    for i, tweet in enumerate(tweets):
        text = tweet.get("text", "")
        
        # Step 1: 미디어 컨테이너 생성
        create_resp = requests.post(base_url, params={
            "media_type": "TEXT",
            "text": text,
            "access_token": access_token
        })
        
        if create_resp.status_code != 200:
            print(f"  [쓰레드 {i+1}] 컨테이너 생성 실패: {create_resp.text}")
            continue
        
        container_id = create_resp.json().get("id")
        
        # Step 2: 퍼블리시
        publish_url = f"https://graph.threads.net/v1.0/{user_id}/threads_publish"
        pub_resp = requests.post(publish_url, params={
            "creation_id": container_id,
            "access_token": access_token
        })
        
        if pub_resp.status_code == 200:
            posted_ids.append(pub_resp.json().get("id"))
            print(f"  [쓰레드 {i+1}/5] 자동 포스팅 성공!")
        else:
            print(f"  [쓰레드 {i+1}] 퍼블리시 실패: {pub_resp.text}")
    
    return posted_ids


# =========================================================
# 3. 통합 실행
# =========================================================

def get_latest_splintered():
    """가장 최근 스플린터링 결과 디렉토리 반환"""
    if not os.path.exists(SPLINTERED_DIR):
        return None
    dirs = sorted(os.listdir(SPLINTERED_DIR), reverse=True)
    if not dirs:
        return None
    return os.path.join(SPLINTERED_DIR, dirs[0])


def main():
    print("\n" + "=" * 60)
    print("  바이브코딩 인스타 + 쓰레드 자동화 엔진")
    print("  [Hormozi Framework: Hook -> Retain -> Reward]")
    print("=" * 60)
    
    latest = get_latest_splintered()
    if not latest:
        print("\n스플린터링 결과가 없습니다. 먼저 content_splinterer.py를 실행하세요.")
        return
    
    print(f"\n대상: {os.path.basename(latest)}/")
    
    # 1. 인스타 캐러셀 이미지 생성
    print("\n[PHASE 1] 인스타그램 캐러셀 이미지 생성")
    print("-" * 40)
    images = generate_carousel_images(latest)
    if images:
        print(f"\n  총 {len(images)}장 이미지 + 캡션 생성 완료!")
        print(f"  경로: instagram_ready/{os.path.basename(latest)}/")
    
    # 2. 쓰레드 포스팅
    print("\n[PHASE 2] 쓰레드(Threads) 포스팅 준비")
    print("-" * 40)
    result = post_to_threads_api(latest)
    if isinstance(result, str):
        print(f"\n  수동 포스팅 파일 준비 완료!")
        print(f"  경로: threads_ready/{os.path.basename(latest)}/")
    elif isinstance(result, list):
        print(f"\n  {len(result)}개 자동 포스팅 성공!")
    
    print("\n" + "=" * 60)
    print("  모든 SNS 콘텐츠 준비 완료!")
    print("=" * 60)
    print(f"""
  [인스타그램]
    1. instagram_ready/ 폴더의 card_1~5.png 이미지를 다운로드
    2. 인스타그램 앱에서 캐러셀 포스트로 업로드
    3. caption.txt 내용을 캡션에 붙여넣기
    
  [쓰레드]
    1. threads_ready/ 폴더의 thread_1~5.txt를 순서대로
    2. 쓰레드 앱에서 스레드로 연결 포스팅
    (또는 full_thread.txt 참조)
    
  [자동화 팁]
    .env에 아래 값을 추가하면 쓰레드 완전 자동화 가능:
    THREADS_ACCESS_TOKEN=your_token
    THREADS_USER_ID=your_user_id
""")


if __name__ == "__main__":
    main()
