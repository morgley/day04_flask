# Flask + SQLite 게시판 U/D 확장 및 디자인 정합성 보정 설계서

## 1) 목표와 범위
- 목표: 기존 C/R/R 게시판에 수정(Update), 삭제(Delete) 기능을 추가한다.
- 추가 요구: 현재 구현 디자인을 `design/stitch_beige_tech_blog_ui`의 원본 의도에 더 가깝게 보정한다.
- 포함 범위:
  - 상세 페이지 [수정] [삭제] 버튼 배치
  - 수정 화면에서 기존 `post_form.html` 재사용
  - 삭제 전 브라우저 기본 확인창 `confirm('정말 삭제할까요?')`
  - 목록/작성 화면의 디자인 정합성 보정
- 제외 범위:
  - 인증/권한
  - soft delete, 복구 기능
  - API 분리, SPA 전환

## 2) 라우트 설계
- `GET /posts/<int:post_id>/edit`
  - 대상 글 조회 후 `post_form.html` 렌더
  - 없으면 404
- `POST /posts/<int:post_id>/edit`
  - `title`, `content`를 `strip()` 처리 후 빈값 검증
  - 유효하면 UPDATE 수행 후 상세 페이지로 리다이렉트
  - 무효하면 400 + 플래시 메시지(`제목과 본문을 입력해주세요.`) + 폼 재렌더
- `POST /posts/<int:post_id>/delete`
  - 대상 글 삭제 후 목록으로 리다이렉트
  - 없으면 404

## 3) 템플릿/화면 설계
### 3-1) 상세 페이지 (`post_detail.html`)
- 본문 하단 액션 영역에 버튼 2개 배치:
  - [수정] → `GET /posts/<id>/edit`
  - [삭제] → `POST /posts/<id>/delete` 폼 제출
- 삭제 폼에는 `onsubmit="return confirm('정말 삭제할까요?')"` 적용

### 3-2) 공용 폼 (`post_form.html`)
- 생성/수정 공용 템플릿 유지
- 모드 분기 값(예: `mode`, `post`)으로 다음만 조건 분기:
  - 페이지 타이틀
  - 폼 action URL
  - 버튼 텍스트
- 입력 필드는 기존 `title`, `content` 그대로 유지

### 3-3) 디자인 정합성 보정
- 목록 페이지(`post_list.html`):
  - `post_list_minimalist_text/code.html`의 핵심 톤(헤더 계층, 리스트 텍스트 리듬, CTA 강약)을 반영
- 작성/수정 공용 페이지(`post_form.html`):
  - `write_post_sidebar_editor/code.html`의 핵심 톤(에디터 중심 구성, 라벨/입력 밀도, 액션 버튼 대비)을 반영
- 제한:
  - “핵심 구조/타이포/여백/액션 계층” 정합성 위주
  - 현재 기능 범위를 벗어나는 위젯(자산 업로드, 분석 패널 등)은 구현하지 않음

## 4) 변경 파일(최소 변경 원칙)
- 수정:
  - `my_board/app.py`
  - `my_board/templates/post_detail.html`
  - `my_board/templates/post_form.html`
  - `my_board/templates/post_list.html`
  - `my_board/static/style.css`
  - `my_board/tests/test_board.py`
- 신규 파일 추가는 하지 않는다.

## 5) 테스트 설계
- 라우트/기능 테스트:
  - `GET /posts/<id>/edit` 200
  - `POST /posts/<id>/edit` 정상 수정 후 상세 반영
  - `POST /posts/<id>/edit` 빈값 제출 시 400 + 메시지
  - `POST /posts/<id>/delete` 정상 삭제 후 목록 이동
  - 없는 글 edit/delete 접근 시 404
- 기존 회귀 테스트 유지:
  - 목록/상세/작성(create)/404 시나리오가 계속 통과해야 함

## 6) 완료 기준
- U/D 기능이 정상 동작한다.
- 상세 페이지에 [수정] [삭제]가 노출되고 삭제 확인창이 동작한다.
- 수정 화면에서 `post_form.html` 재사용이 확인된다.
- 목록/작성 화면이 원본 디자인(`post_list_minimalist_text`, `write_post_sidebar_editor`) 대비 시각적 정합성이 개선된다.
- 테스트 전체 통과.
