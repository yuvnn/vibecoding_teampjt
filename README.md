# LocalHub — 대전/충청권 지역 정보 공유 커뮤니티

공공데이터(한국관광공사 TourAPI 4.0) 기반 익명 지역 정보 커뮤니티. 별도 회원가입·로그인 없이
게시글 단위 비밀번호로만 수정·삭제 권한을 확인하며, 제공 JSON 데이터를 활용한 챗봇 질의응답을
제공한다.

- **대상 권역**: 대전/충청권
- **기술 스택**: Vue.js 3(SPA) · FastAPI · SQLite(SQLAlchemy ORM)
- **배포**: 프론트엔드 Netlify / 백엔드 Render

## 폴더 구조

모노레포로 구성했다. 프론트엔드·백엔드가 저장소 하나에 있지만 배포 설정(`netlify.toml`,
`render.yaml`)의 `base` / `rootDir` 지정으로 각각 독립적으로 빌드·배포된다.

```
vibecoding_teampjt/
├── README.md                    # 이 문서
├── netlify.toml                 # Netlify 배포 설정 (base: frontend)
├── render.yaml                  # Render 배포 설정 (rootDir: backend)
├── .gitignore
│
├── data/                        # 제공 공공데이터 (읽기 전용, 공공누리 3유형 — 변경금지)
│   ├── raw/                     # 대전_충청권_*.json 원본 파일 배치 위치
│   ├── SCHEMA.md                # TourAPI 4.0 원본 JSON 필드 정의
│   └── SOURCE.md                # 데이터 출처·라이선스·파일 목록
│
├── docs/                        # 산출물 문서
│   ├── 기능명세서.md            # 데이터 출처·라이선스 목록 포함
│   └── WBS.md
│
├── frontend/                    # Vue.js 3 SPA (Netlify 배포 대상)
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── .env.example             # VITE_API_BASE_URL
│   ├── public/
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── api/                 # axios 클라이언트 + 엔드포인트별 모듈 (posts.js, chat.js)
│       ├── router/              # vue-router 라우트 정의
│       ├── stores/              # pinia 스토어 (board.js, chat.js)
│       ├── views/               # 페이지 컴포넌트 (Home/BoardList/BoardDetail/BoardWrite)
│       ├── components/
│       │   ├── common/          # 헤더 등 공통 UI
│       │   ├── board/           # 게시판 관련 세부 컴포넌트 (모달 등, 필요 시 추가)
│       │   └── chatbot/         # 챗봇 플로팅 위젯
│       └── assets/
│
├── backend/                     # FastAPI REST API (Render 배포 대상)
│   ├── requirements.txt
│   ├── .env.example             # OPENAI_API_KEY, DATABASE_URL, FRONTEND_ORIGIN, REGION
│   ├── scripts/
│   │   └── seed_db.py           # data/raw JSON → locations 테이블 적재 스크립트
│   └── app/
│       ├── main.py              # FastAPI 앱, CORS, 라우터 등록
│       ├── core/
│       │   ├── config.py        # pydantic-settings 기반 환경변수 로딩
│       │   └── database.py      # SQLAlchemy engine/session
│       ├── models/              # SQLAlchemy ORM 모델 (post, comment, location)
│       ├── schemas/             # Pydantic 요청/응답 스키마 (post, chat)
│       ├── api/
│       │   └── routes/          # posts.py(게시글 CRUD), chat.py(POST /api/chat)
│       ├── services/
│       │   ├── chatbot_service.py  # OpenAI 연동 챗봇 응답 생성
│       │   └── data_loader.py      # JSON → Location 모델 변환
│       └── db/                  # SQLite 파일 저장 위치 (gitignore, 제출 시 별도 첨부)
```

## 폴더 설계 원칙

- **`frontend/` ↔ `backend/` 완전 분리**: 두 앱은 서로의 코드를 import하지 않고 REST API
  (`/api/...`)로만 통신한다. 산출물 목록에 프론트/백엔드 Git Repository URL이 각각
  요구되므로, 이 모노레포 URL 하나를 두 항목에 동일하게 제출하면 된다.
- **`data/`는 읽기 전용 소스**: 제공 JSON은 공공누리 3유형(변경금지) 조건이라 원본을
  건드리지 않는다. 백엔드는 `services/data_loader.py` → `scripts/seed_db.py` 로 이 JSON을
  읽어 `locations` 테이블에 적재만 하고, 커뮤니티 데이터(`posts`, `comments`)와는 완전히
  분리된 테이블로 관리한다.
- **백엔드 계층 분리**: `models`(DB 테이블) / `schemas`(API 입출력 검증) / `api/routes`(엔드포인트)
  / `services`(비즈니스 로직·외부 API 연동)로 나눠 챗봇 로직이나 데이터 적재 로직이
  라우터에 섞이지 않도록 했다.
- **프론트 계층 분리**: `api/`(HTTP 통신) / `stores/`(상태) / `views/`(페이지) /
  `components/`(재사용 UI)로 나눠 화면과 서버 통신 로직을 분리했다.

## 시작하기

### 백엔드 (FastAPI)

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # OPENAI_API_KEY 등 채워 넣기
uvicorn app.main:app --reload
```

- 실행 후 `http://localhost:8000/` 에서 헬스체크 확인.
- 제공 JSON을 `data/raw/`에 배치한 뒤 초기 데이터 적재:
  ```bash
  python -m scripts.seed_db
  ```

### 프론트엔드 (Vue.js 3)

```bash
cd frontend
npm install
cp .env.example .env        # VITE_API_BASE_URL 확인 (로컬은 기본값 사용 가능)
npm run dev
```

## 환경변수 (.env, 절대 커밋 금지)

| 파일 | 변수 | 설명 |
|------|------|------|
| `backend/.env` | `OPENAI_API_KEY` | 챗봇용 OpenAI API 키 (당사 발급) |
| `backend/.env` | `DATABASE_URL` | SQLite 파일 경로 (기본: `sqlite:///./app/db/localhub.db`) |
| `backend/.env` | `FRONTEND_ORIGIN` | CORS 허용 출처 (Netlify 배포 URL) |
| `backend/.env` | `REGION` | 서비스 대상 권역 (기본: 대전/충청권) |
| `frontend/.env` | `VITE_API_BASE_URL` | Render 백엔드 API Base URL |

`.env`는 각 앱의 `.gitignore`에 등록되어 있다. `.env.example`만 커밋하고, 실제 값은
GitLab 저장소에 절대 올리지 않는다.

## 배포

### 프론트엔드 → Netlify

- 저장소를 Netlify에 연결하면 루트의 `netlify.toml`(`base = "frontend"`, `publish = "dist"`)에
  따라 자동으로 `frontend/` 만 빌드된다.
- Netlify 사이트 설정 > Environment variables에 `VITE_API_BASE_URL`(Render 백엔드 URL)을 등록.
- SPA 라우팅을 위해 `netlify.toml`에 `/* → /index.html` 리다이렉트를 이미 포함.

### 백엔드 → Render

- Render 대시보드 > New > Blueprint에서 저장소를 연결하면 루트의 `render.yaml`(`rootDir: backend`)에
  따라 서비스가 생성된다.
- `OPENAI_API_KEY`, `FRONTEND_ORIGIN`은 Render 대시보드에서 직접 입력(`sync: false`).
- **주의**: Render의 기본 웹 서비스는 파일시스템이 재배포/재시작 시 초기화된다. SQLite 파일을
  유지하려면 Render의 Persistent Disk를 `backend/app/db`에 마운트하거나, 배포마다
  `scripts/seed_db.py`로 초기 데이터를 재적재해야 한다.
- 배포 완료 후 프론트엔드·백엔드 URL이 실제로 동작하는지 확인하고 산출물에 기록한다.

## 데이터 & 라이선스

- 원본 JSON 배치 위치와 파일 목록: [`data/raw/README.md`](data/raw/README.md)
- 출처·라이선스(공공누리 3유형) 상세: [`data/SOURCE.md`](data/SOURCE.md)
- 필드 스키마: [`data/SCHEMA.md`](data/SCHEMA.md)
- 제공 JSON 외 추가 데이터를 쓸 경우, 반드시 `data/SOURCE.md`에 출처·라이선스를 추가 기재한다.

## 산출물 체크리스트 (납기 2026-07-16 15:00)

- [ ] 프론트엔드 Git Repository URL (`.env` 미포함 확인)
- [ ] 백엔드 Git Repository URL (`.env` 미포함 확인)
- [ ] SQLite DB 파일(.db, 초기 데이터 포함) — `backend/app/db/localhub.db`를 별도 제출
- [ ] Netlify 배포 URL
- [ ] Render 배포 URL
- [ ] 기능 명세서 (`docs/기능명세서.md` → PDF/docx 변환)
- [ ] WBS (`docs/WBS.md` 또는 스프레드시트)
- [ ] 발표 PPT
