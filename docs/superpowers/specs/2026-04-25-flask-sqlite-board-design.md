# Flask + SQLite 게시판 설계서 (C/R/R)

## 1) 목표와 범위
- 목표: `my-board/my_board` 경로에 Flask + SQLite 기반 게시판을 구축한다.
- 1차 기능 범위: 글쓰기(Create), 목록보기(Read), 상세보기(Read).
- 제외 범위: 수정/삭제(Update/Delete), 인증/권한, 검색/페이징.

## 2) 구현 접근
- 선택안: Flask + Jinja 서버 렌더링(SSR).
- 선택 이유:
  - 현재 요구사항(C/R/R)과 범위에 가장 단순하고 안정적이다.
  - 제공된 디자인 HTML(`post_list_minimalist_text`, `post_detail`, `write_post_sidebar_editor`)을 템플릿으로 이식하기 쉽다.
  - `linen_logic`를 공통 레이아웃으로 반영하기 좋다.

## 3) 디렉토리 구조
- 루트: `my-board/my_board`
- 가상환경: `my-board/my_board/.venv`
- 예상 파일 구조:
  - `my_board/app.py` (앱 엔트리, 라우트, DB 접근)
  - `my_board/templates/base.html` (linen_logic 공통 헤더/톤)
  - `my_board/templates/post_list.html` (목록)
  - `my_board/templates/post_detail.html` (상세)
  - `my_board/templates/post_form.html` (글쓰기)
  - `my_board/static/style.css` (공통 스타일)
  - `my_board/instance/board.db` (SQLite DB)

## 4) 데이터 설계
- 테이블: `posts`
- 스키마:
  - `id INTEGER PRIMARY KEY AUTOINCREMENT`
  - `title TEXT NOT NULL`
  - `content TEXT NOT NULL`
  - `created_at TEXT NOT NULL`
- 시간 저장 형식: 로컬 시간 문자열 `YYYY-MM-DD HH:MM:SS`.

## 5) 라우팅/동작 설계
- `GET /`
  - 게시글 목록을 최신순으로 조회하여 렌더링.
- `GET /posts/new`
  - 글쓰기 폼 페이지 렌더링.
- `POST /posts`
  - 제목/본문 공백 여부만 최소 검증.
  - 유효하면 DB insert 후 생성된 게시글 상세로 리다이렉트.
- `GET /posts/<int:post_id>`
  - 해당 게시글 상세 렌더링.
- 수정/삭제 라우트는 생성하지 않는다.

## 6) UI/디자인 반영 원칙
- 공통 레이아웃:
  - `linen_logic`의 warm minimal 톤(베이지 배경, 차콜 텍스트, serif body 느낌)을 `base.html`과 공통 CSS에 반영.
- 목록 페이지:
  - `post_list_minimalist_text`의 에디토리얼 리스트 구조를 적용.
- 상세 페이지:
  - `post_detail`의 본문 중심 타이포/메타 구조 적용.
- 글쓰기 페이지:
  - `write_post_sidebar_editor`의 미니멀 에디터 레이아웃에서 핵심 입력 UX만 반영.
- 범위 통제:
  - 지금 단계는 기능 우선으로, 데코레이션/부가 위젯은 축소 적용.

## 7) 에러 처리/검증
- 현재 단계 최소 처리만 수행:
  - 제목 또는 본문이 비어 있으면 작성 폼으로 되돌리고 안내 메시지 표시.
  - 존재하지 않는 글 ID 접근 시 404 처리.

## 8) 검증 계획
- 환경 준비:
  - Ubuntu 24.04에서 `python3 -m venv .venv` 생성 후 Flask 설치.
- 기능 검증 시나리오:
  1. 서버 실행 후 목록 페이지(`GET /`) 접속 확인.
  2. 글쓰기 페이지에서 제목/본문 작성 후 저장.
  3. 저장 직후 상세 페이지로 이동 확인.
  4. 목록으로 돌아가 새 글 노출 확인.
  5. DB에서 `posts` 테이블/행 생성 확인.

## 9) 완료 기준
- C/R/R 기능이 정상 동작한다.
- `posts(id, title, content, created_at)` 테이블이 생성되고 데이터가 적재된다.
- 3개 디자인 페이지 + `linen_logic` 공통 레이아웃이 일관성 있게 반영된다.

## 10) 제약/메모
- 현재 작업 디렉토리(`my-board`)는 git 저장소가 아니므로 본 문서 커밋은 수행하지 않는다.
