# MovieFlix Backend — Django REST API

영화·장르·출연진·리뷰 데이터와 날씨 기반 추천을 제공하고, 토큰 인증 기반의 리뷰 CRUD를 지원하는 REST API 서버입니다. Vue 프론트엔드의 영화 데이터 출처로 사용됩니다.

## 기술 스택

| 기술 | 버전 | 선택 이유 |
| :--- | :--- | :--- |
| Django | 5.2 | ORM으로 M:N·1:N 관계와 집계 쿼리를 간결하게 표현, admin으로 데이터 확인 용이 |
| Django REST Framework | 3.18 | Serializer로 중첩 응답·입력 검증을 선언적으로 작성, `@api_view`로 HTTP 메서드별 분기 |
| dj-rest-auth + django-allauth | 7.2 / 65.x | 회원가입·로그인·토큰 발급을 검증된 라이브러리로 구성 |
| DRF TokenAuthentication | — | SPA에서 헤더 한 줄로 인증 가능한 단순한 방식 |
| django-cors-headers | 4.9 | Vite 개발 서버(5173)에서의 교차 출처 요청 허용 |
| SQLite | — | 설치 없이 실행 가능, fixture로 초기 데이터 재현 |

## 실행

```bash
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt

python problem/problem_a.py   # CSV(problem/data) → fixture(JSON) 생성
python manage.py migrate
python manage.py loaddata users.json genres.json movies.json casts.json reviews.json
python manage.py runserver
```

테스트: `python manage.py test movies`

## 데이터 모델

```
User ──1:N──┐
            ▼
Movie ──1:N──▶ Review
  │
  ├──1:N──▶ Cast
  └──M:N──▶ Genre
```

| 모델 | 필드 | 관계 |
| :--- | :--- | :--- |
| Movie | id(TMDB id, PK), title, release_date, popularity, budget, revenue, runtime, overview, poster_path, vote_average | Genre와 M:N (`genres`) |
| Genre | id(TMDB 장르 id, PK), name | |
| Cast | movie, name, character, order | Movie 1:N |
| Review | movie, author, content, rating | Movie 1:N, User 1:N |

- TMDB의 영화·장르 ID를 그대로 PK로 사용해 외부 데이터와의 매핑을 단순하게 유지했습니다.
- 리뷰 작성자는 문자열이 아닌 `User` FK로 설계해 권한 검사를 가능하게 했습니다.

### TMDB 데이터 수집 (`problem/fetch_tmdb.py`)

제공 CSV에는 프론트엔드 화면에 필요한 줄거리·포스터 경로·평점이 없어, TMDB 상세 API(`ko-KR`, 한국어 줄거리가 없으면 영어)로 수집해 `problem/data/movie_tmdb.csv`에 저장합니다. 결과 CSV를 저장소에 포함했기 때문에 데이터를 새로 받을 때만 실행하면 됩니다.

```bash
TMDB_API_KEY=<v3 키 또는 v4 토큰> python problem/fetch_tmdb.py
```

### CSV → fixture 변환 (`problem/problem_a.py`)

원본 CSV는 바로 적재할 수 없는 형태여서 변환 스크립트를 작성했습니다.

- `movie_cast.csv`의 `cast_id`는 영화마다 겹치고, `movie_reviews.csv`의 `review_id`는 16진 문자열 → CSV 순서대로 PK를 재부여
- 장르가 `"Animation, Family"` 같은 문자열 → TMDB 장르 ID로 매핑해 M:N 관계로 연결
- 리뷰 작성자 이름마다 로그인 불가 계정(비밀번호 `!`)을 생성해 User FK로 연결
- `movie_tmdb.csv`의 줄거리·포스터·평점을 영화 데이터에 병합

## API

`/accounts/signup/`, `/accounts/login/`을 제외한 모든 요청은 `Authorization: Token <key>` 헤더가 필요합니다.

| Method | URL | 설명 |
| :--- | :--- | :--- |
| POST | `/accounts/signup/` | 회원가입 (username, password1, password2) → 토큰 발급 |
| POST | `/accounts/login/` | 로그인 (username, password) → `{"key": "<token>"}` |
| GET | `/api/v1/genres/` | 장르 목록 `[{id, name}]` |
| GET | `/api/v1/movies/` | 영화 목록, 평점 높은 순 (genres는 장르 id 목록) |
| GET | `/api/v1/movies/<movie_pk>/` | 영화 상세 + 장르명, 출연진, 리뷰, 평균 평점, 리뷰 수 |
| GET | `/api/v1/movies/recommend/?genre=<id>` | 해당 장르 영화 중 랜덤 1편 (장르 누락·형식 오류 400, 영화 없음 404) |
| POST | `/api/v1/movies/<movie_pk>/reviews/` | 리뷰 생성 (201) |
| GET | `/api/v1/reviews/` | 리뷰 목록 (movie는 `{id, title}`) |
| GET | `/api/v1/reviews/<review_pk>/` | 리뷰 조회 |
| PUT | `/api/v1/reviews/<review_pk>/` | 리뷰 전체 수정 (content, rating 모두 필요, 누락 시 400) |
| PATCH | `/api/v1/reviews/<review_pk>/` | 리뷰 부분 수정 |
| DELETE | `/api/v1/reviews/<review_pk>/` | 리뷰 삭제 (204) |

## 구현 포인트

- **작성자 권한 검사** — 리뷰 수정·삭제는 작성자 본인만 가능하며, 다른 사용자는 403을 받습니다. 작성자는 요청 토큰의 사용자로 저장되므로 요청 본문에서 받지 않습니다(`ReadOnlyField`).
- **집계 쿼리** — 영화 상세의 `average_rating`은 `Avg('review__rating')`, `vote_count`는 `Count('review__rating')`로 annotate해 DB에서 계산합니다. 리뷰가 없으면 평균은 `null`입니다.
- **N+1 방지** — 상세 조회는 `prefetch_related('genres', 'cast_set', 'review_set__author')`, 리뷰 목록은 `select_related('movie', 'author')`로 쿼리 수를 줄였습니다.
- **랜덤 추천** — `order_by('?')`는 후보 전체를 랜덤 정렬하므로, `aggregate(Count('id'))`로 후보 수를 구한 뒤 `random.randrange`로 고른 offset의 1건만 조회합니다.
- **프론트엔드와 필드명 통일** — `overview`, `poster_path`, `vote_average`를 TMDB 응답과 같은 이름으로 내려줘, 프론트엔드가 데이터 출처와 관계없이 같은 컴포넌트로 렌더링합니다.
- **용도별 Serializer 분리** — 목록·상세·리뷰 응답 형태가 달라, 중첩 Serializer로 필요한 필드만 노출했습니다 (예: 리뷰 응답의 movie는 `{id, title}`만).
- **PUT/PATCH 구분** — 같은 Serializer에 `partial=request.method == 'PATCH'`를 넘겨 전체/부분 수정을 하나의 뷰에서 처리합니다.

## 테스트

`movies/tests.py`에 16개 테스트를 작성했습니다.

- 장르·영화·리뷰 조회, 목록 평점순 정렬, 상세의 줄거리·포스터 필드, 존재하지 않는 영화 404
- 장르 추천 성공, 장르 누락·형식 오류 400, 영화 없는 장르 404
- 리뷰 생성 201, PUT 전체 수정 / 필드 누락 시 400, PATCH 부분 수정, DELETE 204
- 토큰 없이 요청 시 401, 작성자가 아닌 사용자의 수정 시도 403
- 회원가입 → 로그인 → 토큰 발급 흐름
