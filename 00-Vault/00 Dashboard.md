---
tags: [dashboard, moc]
---

# vibe-ebook-blog — 볼트 대시보드

이 저장소를 그대로 Obsidian 볼트로 연 것입니다.

## 이 저장소는 무엇인가

`aiaijungle/vibe-ebook`(전자책 시리즈)을 위한 **AEO 블로그·콘텐츠 재활용 자동화 파이프라인**. 블로그 8편 + 자동 발행/재활용 스크립트로 구성. 콘텐츠를 한 번 만들고 여러 채널로 쪼개 배포하는 구조.

## 파이프라인 구성 (파일 기준)

| 스크립트 | 역할 |
|---|---|
| `master_pipeline.py` | 전체 파이프라인 오케스트레이션 |
| `auto_blog_builder.py` | 블로그 포스트 자동 생성 |
| `blog_scheduler.py` | 발행 스케줄링 |
| `content_splinterer.py` | 블로그 글 → 짧은 콘텐츠로 쪼개기(`splintered_content/`) |
| `sns_auto_poster.py` | SNS 자동 포스팅 |
| `email_nurture.py` | 이메일 너처 시퀀스 (`email_sequence_log.json`) |
| `전자책_마케팅_스케줄러_시작.bat` | Windows용 실행 배치 |

## 산출물 폴더

- `blog/` — 발행된 블로그 포스트 8편
- `splintered_content/` — 쪼개진 콘텐츠
- `instagram_ready/`, `threads_ready/` — 채널별 재가공 콘텐츠
- `leads.json` — 수집된 리드

## 섹션

- [[PARA 연동 노트]] — 로컬 PARA 볼트 `1-Projects/`용 요약 (수동 반영)

## 관련 저장소

- `aiaijungle/vibe-ebook` — 이 블로그가 트래픽을 보내는 본 전자책 사이트
- `aiaijungle/jungle-booking-aeo-landing` — 동일한 파이프라인 패턴(`auto_blog_builder.py`, `blog_scheduler.py`)을 쓰는 자매 프로젝트, 공통 모듈화 여지 있음
