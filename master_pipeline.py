"""
바이브코딩 마케팅 마스터 파이프라인
- 모든 자동화 모듈을 하나로 통합 실행
- 블로그 생성 -> 스플린터링 -> SNS 이미지 -> 이메일 시퀀스
"""
import subprocess
import sys
import os
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_step(name, script, args=[]):
    """서브 스크립트 실행"""
    print(f"\n{'='*55}")
    print(f"  STEP: {name}")
    print(f"{'='*55}")
    try:
        result = subprocess.run(
            [sys.executable, script] + args,
            cwd=BASE_DIR,
            check=True,
            capture_output=False
        )
        print(f"  -> {name} 완료!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  -> {name} 실패: {e}")
        return False

def main():
    start = datetime.datetime.now()
    
    print(f"""
    ╔══════════════════════════════════════════════════╗
    ║   바이브코딩 마케팅 마스터 파이프라인            ║
    ║   [Hormozi Framework: 1 -> 30 자동화]           ║
    ║   {start.strftime('%Y-%m-%d %H:%M:%S')}                           ║
    ╚══════════════════════════════════════════════════╝
    """)
    
    results = {}
    
    # STEP 1: AI 블로그 생성
    results["blog"] = run_step(
        "AI 블로그 자동 생성 (SEO/AEO)",
        "auto_blog_builder.py"
    )
    
    # STEP 2: 콘텐츠 스플린터링 (1 -> 5 포맷)
    results["splinter"] = run_step(
        "콘텐츠 스플린터링 (블로그 -> 5 SNS 포맷)",
        "content_splinterer.py"
    )
    
    # STEP 3: 인스타 + 쓰레드 콘텐츠 생성
    results["sns"] = run_step(
        "인스타 이미지 + 쓰레드 텍스트 생성",
        "sns_auto_poster.py"
    )
    
    # STEP 4: 이메일 시퀀스 실행
    results["email"] = run_step(
        "이메일 너처링 시퀀스 실행",
        "email_nurture.py",
        ["run"]
    )
    
    # STEP 5: Git 배포
    print(f"\n{'='*55}")
    print(f"  STEP: GitHub Pages 자동 배포")
    print(f"{'='*55}")
    try:
        subprocess.run(["git", "add", "."], cwd=BASE_DIR, check=True)
        subprocess.run(
            ["git", "commit", "-m", f"Auto Pipeline: {start.strftime('%Y-%m-%d %H:%M')}"],
            cwd=BASE_DIR, check=False
        )
        subprocess.run(["git", "push"], cwd=BASE_DIR, check=True)
        results["deploy"] = True
        print("  -> 배포 완료!")
    except Exception as e:
        results["deploy"] = False
        print(f"  -> 배포 실패: {e}")
    
    # 최종 리포트
    elapsed = (datetime.datetime.now() - start).seconds
    
    print(f"""
    ╔══════════════════════════════════════════════════╗
    ║   마스터 파이프라인 실행 완료!                   ║
    ╠══════════════════════════════════════════════════╣
    ║   블로그 생성:    {'OK' if results.get('blog') else 'FAIL':>5}                         ║
    ║   스플린터링:     {'OK' if results.get('splinter') else 'FAIL':>5}                         ║
    ║   SNS 콘텐츠:     {'OK' if results.get('sns') else 'FAIL':>5}                         ║
    ║   이메일 시퀀스:  {'OK' if results.get('email') else 'FAIL':>5}                         ║
    ║   GitHub 배포:    {'OK' if results.get('deploy') else 'FAIL':>5}                         ║
    ╠══════════════════════════════════════════════════╣
    ║   소요 시간: {elapsed}초                                ║
    ╚══════════════════════════════════════════════════╝
    """)

if __name__ == "__main__":
    main()
