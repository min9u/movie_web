# MovieFlix Frontend — Vue 3 SPA

TMDB·YouTube·Open-Meteo API를 조합해 영화 탐색, 예고편/리뷰 영상 감상, 날씨 기반 추천을 제공하는 싱글 페이지 애플리케이션입니다.

## 기술 스택

| 기술 | 선택 이유 |
| :--- | :--- |
| Vue 3 (Composition API) | `<script setup>`으로 상태·비동기 로직을 간결하게 작성, 로딩/에러 상태가 많은 화면에 적합 |
| Vite | 빠른 개발 서버·HMR, `import.meta.env`로 API 키를 코드와 분리 |
| Pinia | 로그인 토큰을 네비게이션 바·라우터 가드·API 인터셉터가 함께 쓰도록 전역 상태로 관리 |
| Vue Router | 새로고침 없는 페이지 전환, 동적 라우트(`/:movieId`)로 상세 페이지 구성 |
| Axios | API별 인스턴스(`axios.create`)에 baseURL·인증·공통 파라미터를 묶고, 인터셉터로 토큰 첨부·401 처리 |
| Bootstrap 5 | 그리드·카드·네비게이션을 빠르게 구성하고 커스텀 CSS로 다듬음 |

## 실행

```bash
npm install
cp .env.example .env   # API 키 입력
npm run dev            # http://localhost:5173
```

| 환경 변수 | 설명 |
| :--- | :--- |
| `VITE_TMDB_API_KEY` | TMDB v3 API Key 또는 v4 Read Access Token(`eyJ...`) — 둘 다 지원 |
| `VITE_YOUTUBE_API_KEY` | YouTube Data API v3 Key |
| `VITE_MOVIE_API_SOURCE` | 영화 데이터 출처: `tmdb`(기본) / `django`(자체 API 서버, 로그인 필요) |
| `VITE_DJANGO_API_URL` | 자체 API 서버 주소 (기본 `http://127.0.0.1:8000/api/v1`) |

## 페이지 구성

| Path | View | 기능 |
| :--- | :--- | :--- |
| `/` | `HomeView` | 서비스 소개와 주요 메뉴 |
| `/movies` | `MovieListView` | TMDB 최고 평점 영화 카드 목록 |
| `/:movieId` | `MovieDetailView` | 영화 상세 정보 + 공식 예고편 모달 |
| `/review-search` | `ReviewSearchView` | YouTube 리뷰 영상 검색 및 모달 재생 |
| `/recommended` | `RecommendedView` | 서울 현재 날씨 기반 랜덤 영화 추천 |
| `/login` | `LoginView` | 자체 API 서버 로그인 (토큰 발급) |
| `/signup` | `SignupView` | 자체 API 서버 회원가입 (가입 즉시 로그인) |

`django` 모드에서는 영화 데이터를 쓰는 페이지(`/movies`, `/:movieId`, `/recommended`)에 로그인이 필요하며, 네비게이션 바에 로그인/로그아웃 버튼이 표시됩니다.

## 구조

```
src/
├─ api/
│  ├─ movies.js    데이터 출처 추상화 레이어 — 뷰는 이 파일만 사용
│  ├─ tmdb.js      TMDB axios 인스턴스 (v3/v4 인증 자동 판별, ko-KR)
│  ├─ django.js    자체 REST API 클라이언트 (토큰 첨부·401 처리 인터셉터)
│  ├─ accounts.js  회원가입/로그인 (dj-rest-auth)
│  ├─ youtube.js   YouTube 검색 / embed URL
│  └─ weather.js   Open-Meteo 조회 + WMO 코드 → 장르 매핑
├─ components/
│  ├─ MovieCard.vue            포스터·제목·평점·줄거리 카드
│  ├─ MovieDetailInfo.vue      상세 정보 표시
│  ├─ VideoModalFrame.vue      모달 공통 틀 (Teleport, ESC/배경 클릭 닫기)
│  ├─ YoutubeTrailerModal.vue  "제목 trailer" 검색 첫 결과 재생
│  ├─ YoutubeCard.vue          검색 결과 카드
│  └─ YoutubeReviewModal.vue   선택한 리뷰 영상 재생
├─ stores/auth.js              로그인 토큰·사용자명 (Pinia, localStorage 유지)
├─ utils/decodeHtml.js         HTML 엔티티 안전 디코딩
├─ views/                      페이지 컴포넌트 7개
└─ router/index.js
```

## 날씨 → 장르 매핑

| WMO 코드 | 날씨 | 추천 장르 |
| :--- | :--- | :--- |
| 0 | 맑음 | 모험 |
| 1–3 | 구름/흐림 | 코미디 |
| 45, 48 | 안개 | 미스터리 |
| 51–57 | 이슬비 | 드라마 |
| 61–67, 80–82 | 비 | 공포 |
| 71–77, 85–86 | 눈 | 로맨스 |
| 95–99 | 뇌우 | 스릴러 |
| 그 외 | — | 애니메이션 |

TMDB 모드에서는 매칭된 장르에서 투표 수 1,000 이상인 영화를 평점순으로 조회한 뒤 랜덤으로 1편을 고르고, Django 모드에서는 서버의 추천 API가 직접 1편을 골라 줍니다. "다른 영화 추천" 버튼으로 다시 뽑을 수 있습니다.

## 구현 포인트

- **API 레이어 분리** — 컴포넌트는 `api/movies.js`의 함수만 호출하고, 실제 데이터 출처(TMDB / 자체 서버)는 환경 변수로 전환합니다.
- **토큰 인증 흐름** — 토큰은 Pinia 스토어와 localStorage에 보관하고, axios 요청 인터셉터가 `Authorization: Token <key>` 헤더를 붙입니다. 라우터 가드가 비로그인 사용자를 로그인 페이지로 보내며 원래 경로를 `redirect` 쿼리로 넘겨, 로그인 후 그 페이지로 돌아옵니다. 401 응답을 받으면 토큰을 지우고 다시 로그인하게 합니다.
- **라우트 충돌 방지** — `/:movieId(\\d+)`로 숫자 ID만 상세 페이지에 매칭합니다.
- **같은 라우트 내 이동 처리** — `watch(route.params.movieId, { immediate: true })`로 상세 페이지 간 이동 시에도 데이터를 다시 불러옵니다.
- **모달 재사용** — `VideoModalFrame`에 Teleport·ESC 닫기·스크롤 잠금을 모아 예고편/리뷰 모달이 공유합니다. `v-if`로 렌더링해 닫으면 iframe이 제거되어 재생도 멈춥니다.
- **XSS 없는 텍스트 디코딩** — YouTube 제목의 HTML 엔티티를 `v-html` 대신 `DOMParser`로 디코딩합니다.
- **로딩·에러 상태** — 모든 API 호출 화면에 로딩 스피너와 에러 메시지(키 오류, 할당량 초과 등)를 표시합니다.
