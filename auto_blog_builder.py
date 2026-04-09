import os
import sys
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
try:
    import openai
except ImportError:
    print("openai 모듈이 없습니다. 'pip install openai'를 실행해주세요.")
    sys.exit(1)

from dotenv import load_dotenv

BASE_URL = "https://aiaijungle.github.io/vibe-ebook-blog"
BLOG_DIR = os.path.join(os.path.dirname(__file__), "blog")
SITEMAP_PATH = os.path.join(os.path.dirname(__file__), "sitemap.xml")
INDEX_PATH = os.path.join(os.path.dirname(__file__), "index.html")

# .env 에서 인증키 가져오기
ENV_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "03_마케팅_자동화", ".env")
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if line.strip() and "=" in line:
                k, v = line.strip().split("=", 1)
                os.environ[k.strip()] = v.strip()

API_KEY = os.environ.get("OPENAI_API_KEY")
if not API_KEY:
    print("\n⚠️ OPENAI_API_KEY가 없습니다!")
    sys.exit(1)

client = openai.OpenAI(api_key=API_KEY)


def get_ebook_context():
    """바이브코딩 전자책 핵심 내용 반환"""
    print("[1/4] 바이브코딩 컨텍스트 불러오는 중...")
    return "바이브코딩 마스터리는 비개발자, 창업가, 프롬프트 엔지니어 지망생을 위한 완벽한 AI 코딩 가이드북입니다. Claude 3, ChatGPT를 활용해 복잡한 프로그래밍 언어를 배우지 않아도 인간의 언어(Vibe)만으로 소프트웨어와 웹서비스를 개발하고 배포할 수 있는 1억 원 가치의 실전 비법을 담았습니다."


def crawl_naver_blog(query="바이브코딩"):
    """네이버 블로그 검색을 통해 최근 동향 크롤링"""
    print("[2/4] 네이버 블로그 최신 동향 크롤링 중...")
    url = f"https://search.naver.com/search.naver?where=view&sm=tab_jum&query={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")
        titles = soup.find_all("a", class_="api_txt_lines total_tit")
        snippets = soup.find_all("div", class_="api_txt_lines dsc_txt")
        
        context = ""
        for t, s in zip(titles[:5], snippets[:5]):
            context += f"- 검색된 주제: {query}\n- 제목: {t.text}\n  내용 요약: {s.text}\n\n"
        return context
    except Exception as e:
        print(f"네이버 크롤링 실패: {e}")
        return "네이버 블로그 데이터를 가져오지 못했습니다. 일반적인 비즈니스 트렌드를 활용하세요."


def generate_blog_html(ebook_context, naver_context, chosen_topic):
    """Claude AI를 통해 HTML 형식의 블로그 포스트 생성"""
    print("[3/4] AI 블로그 작성 중 (AEO/SEO 최적화)...")
    
    prompt = f"""
    당신은 B2B SaaS 및 마케팅 전문가이자 천재적인 카피라이터입니다.
    아래 1.바이브코딩 전자책 공식 소개와 2.네이버 블로그 최신 동향을 바탕으로, 
    "바이브코딩(AI 창업)을 활용한 {chosen_topic} 극대화 성과 및 후기"를 주제로 하여
    새로운 SEO/AEO 최적화 블로그 페이지를 작성해주세요. (단순 홍보가 아닌, 실제 고객의 문제를 해결한 팩트 기반의 후기 칼럼 형태로 상세히 작성)
    
    [정보 1: 바이브코딩 공식 내용]
    {ebook_context}
    
    [정보 2: 네이버 블로그 동향]
    {naver_context}
    
    [요구사항]
    1. 디자인은 화려한 글래스모피즘(Glassmorphism) 다크 테마 HTML 코드로 작성 (css포함).
    2. 시맨틱 태그(article, h1, h2, h3, ul, li) 적극 활용 및 **Q&A 형식 포맷팅**.
    3. **전자책 내용과 블로그 동향을 융합하여 작성하고, 본문 중간에 반드시 [가슴 뛰는 리얼 독자 후기 ★★★★★] 섹션을 만들어 2~3명의 리얼하고 감동적인 가상 후기(예: '3천만원 견적받고 포기하려다 어젯밤 직접 서버 올렸습니다' 등)를 인용구(blockquote) 형태로 시각적으로 매우 돋보이게 추가하세요.**
    4. 📌 **매우 중요**: 글 하단(또는 중간중간 적절한 곳)에 반드시 **"바이브코딩 1권 즉시 열람하기"** 버튼을 크고 화려한 CTA 버튼 디자인으로 넣어주세요. (링크 주소: https://aiaijungle.github.io/vibe-ebook/)
    5. 📌 **매우 중요**: 생성되는 HTML의 `<head>` 안에는 SEO/AEO 최적화를 위해 완벽한 title, meta description 태그를 넣고, 구글 태그(GDN) 코드도 포함해주세요: `<script async src="https://www.googletagmanager.com/gtag/js?id=AW-987654321"></script><script>window.dataLayer = window.dataLayer || []; function gtag(){{dataLayer.push(arguments);}} gtag('js', new Date()); gtag('config', 'AW-987654321');</script>`
    6. 📌 **매우 중요**: 본문 곳곳에(최상단, 본문 중간, 하단 등) **"현재 작성 중인 내용({chosen_topic}, AI, 프로그래밍 등)과 완벽히 일치하는"** 이미지를 **총 4장** 삽입해주세요. `<img src="https://image.pollinations.ai/prompt/핵심을_나타내는_영어단어?width=800&height=400&nologo=true" alt="이미지 설명" style="width:100%; max-height:400px; object-fit:cover; border-radius:16px; margin: 2rem 0; box-shadow: 0 10px 30px rgba(0,0,0,0.5);" />` 형식을 써서 실시간 생성되게 하세요. (예: `https://image.pollinations.ai/prompt/Hacker%20Coding%20AI%20Screen?width=800&height=400&nologo=true`)
    7. 반드시 ```html 코드블럭으로만 출력.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=4000
        )
        content = response.choices[0].message.content
    except Exception as e:
        print(f"  [실패] gpt-4o-mini 생성 에러 - {e}")
        sys.exit(1)
        
    match = re.search(r"```html\n(.*?)\n```", content, re.DOTALL)
    if match:
        return match.group(1)
    return content


def update_sitemap(filename):
    """sitemap.xml에 새로운 블로그 파일 주소 추가"""
    print("[4/4] 사이트맵(sitemap.xml) 자동 업데이트 중...")
    if not os.path.exists(SITEMAP_PATH):
        return
        
    date_str = datetime.now().strftime("%Y-%m-%d")
    new_url_tag = f"""  <url>
    <loc>{BASE_URL}/blog/{filename}</loc>
    <lastmod>{date_str}</lastmod>
    <changefreq>monthly</changefreq>
  </url>
</urlset>"""

    with open(SITEMAP_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    
    new_content = content.replace("</urlset>", new_url_tag)
    with open(SITEMAP_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

import json

def update_blog_data_js():
    print("[-] 블로그 데이터(blog_data.js) 업데이트 중...")
    blogs = []
    if os.path.exists(BLOG_DIR):
        files = [f for f in os.listdir(BLOG_DIR) if f.endswith(".html")]
        files.sort(reverse=True)
        
        for file in files:
            filepath = os.path.join(BLOG_DIR, file)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                soup = BeautifulSoup(content, "html.parser")
                title_tag = soup.find("title")
                desc_tag = soup.find("meta", attrs={"name": "description"})
                
                title = title_tag.text.strip() if title_tag else "바이브코딩 마스터리 인사이트"
                desc = desc_tag["content"].strip() if desc_tag and desc_tag.has_attr("content") else "비개발자도 AI로 코딩하는 바이브코딩 전자책 후기와 성과"
                
                blogs.append({
                    "title": title,
                    "desc": desc,
                    "url": f"blog/{file}"
                })
                
    js_path = os.path.join(os.path.dirname(__file__), "blog_data.js")
    with open(js_path, "w", encoding="utf-8") as f:
        f.write("const BLOG_POSTS = " + json.dumps(blogs, ensure_ascii=False, indent=4) + ";\n")


import random

def main():
    os.makedirs(BLOG_DIR, exist_ok=True)
    today_str = datetime.now().strftime("%Y%m%d_%H%M")
    
    # 바이브코딩 전용 키워드
    target_topics = [
        "AI 코딩", "바이브코딩", "비개발자 코딩", "챗GPT 코딩", 
        "코딩 부트캠프", "전자책 부업", "AI 자동화 시스템 구축"
    ]
    chosen_topic = random.choice(target_topics)
    print(f"[*] 오늘의 타겟팅 크롤링 주제: {chosen_topic}")
    
    e_ctx = get_ebook_context()
    n_ctx = crawl_naver_blog(chosen_topic)
    
    n_ctx += f"\n\n[최신 팩트 업데이트: {chosen_topic} 분야에서 '바이브코딩 마스터리' 전자책이 비개발자들의 혁신을 이끌고 있습니다. 복잡한 문법 공부 없이 텔레그램 지시만으로 수익형 웹서비스를 런칭하는 사례가 폭발적으로 증가했습니다.]"
    
    html_result = generate_blog_html(e_ctx, n_ctx, chosen_topic)
    
    filename = f"vibe-post-{today_str}.html"
    filepath = os.path.join(BLOG_DIR, filename)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_result)
        
    update_sitemap(filename)
    update_blog_data_js()
    
    print("\n==============================================")
    print(f"바이브코딩 무인 자동화 블로그 발행 완료!")
    print(f"   파일: blog/{filename}")
    print("==============================================\n")

if __name__ == "__main__":
    main()
