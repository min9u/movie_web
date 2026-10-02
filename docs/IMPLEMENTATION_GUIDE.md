# 📘 MovieFlix 구현 가이드

> 이 문서는 "무엇을 만들었는가"보다 **"어떤 순서로, 왜 그렇게 만들었는가"** 를 따라가며 다시 이해할 수 있도록 정리한 문서입니다.
> 각 단계는 **목표 → 코드 → 핵심 개념 → 왜 이렇게 했나 → 직접 해보기** 순서로 구성되어 있습니다.
> 코드는 실제 프로젝트 파일에서 발췌했으니, 파일을 옆에 열어두고 함께 읽으면 좋습니다.
>
> - **Part 1 백엔드**: 데이터를 저장하고 API로 내려주는 Django 서버
> - **Part 2 프론트엔드**: 외부 API와 자체 서버의 데이터를 보여주는 Vue SPA
> - **Part 3 통합**: 두 서버를 함께 실행하고 연동을 확인하는 방법

---

## 목차

- [0. 전체 그림 먼저 보기](#0-전체-그림-먼저-보기)
- **Part 1. 백엔드 (Django REST API)**
  - [B1. 프로젝트 세팅](#b1-프로젝트-세팅)
  - [B2. 모델 설계와 마이그레이션](#b2-모델-설계와-마이그레이션)
  - [B3. 초기 데이터 준비](#b3-초기-데이터-준비)
  - [B4. 조회 API — Serializer, View, URL](#b4-조회-api--serializer-view-url)
  - [B5. 리뷰 CRUD API](#b5-리뷰-crud-api)
  - [B6. 회원가입·로그인과 권한](#b6-회원가입로그인과-권한)
  - [B7. 평점 통계 — annotate](#b7-평점-통계--annotate)
  - [B8. 날씨 추천 API — Count와 랜덤 offset](#b8-날씨-추천-api--count와-랜덤-offset)
  - [B9. CORS 설정](#b9-cors-설정)
  - [B10. 테스트](#b10-테스트)
- **Part 2. 프론트엔드 (Vue SPA)**
  - [F1. Vue 프로젝트 생성과 진입점](#f1-vue-프로젝트-생성과-진입점)
  - [F2. 라우터와 네비게이션 바](#f2-라우터와-네비게이션-바)
  - [F3. API 레이어 분리 — axios 인스턴스](#f3-api-레이어-분리--axios-인스턴스)
  - [F4. 최고 평점 영화 목록](#f4-최고-평점-영화-목록)
  - [F5. 영화 상세 정보](#f5-영화-상세-정보)
  - [F6. 공통 모달 만들기](#f6-공통-모달-만들기)
  - [F7. 공식 예고편 모달](#f7-공식-예고편-모달)
  - [F8. 리뷰 영상 검색](#f8-리뷰-영상-검색)
  - [F9. 로그인과 토큰 관리](#f9-로그인과-토큰-관리)
  - [F10. 데이터 출처 전환하기](#f10-데이터-출처-전환하기)
  - [F11. 날씨 기반 영화 추천](#f11-날씨-기반-영화-추천)
  - [F12. 스타일링과 마무리 점검](#f12-스타일링과-마무리-점검)
- **Part 3. 통합**
  - [I1. 전체 실행 순서](#i1-전체-실행-순서)
  - [I2. 연동 확인 시나리오](#i2-연동-확인-시나리오)
  - [I3. 자주 만나는 문제와 해결](#i3-자주-만나는-문제와-해결)
- [복습 체크리스트와 셀프 퀴즈](#복습-체크리스트와-셀프-퀴즈)

---

## 0. 전체 그림 먼저 보기

### 0-1. 구조 한 장 요약

```
┌──────────────────────── 브라우저 (Vue SPA, :5173) ────────────────────────┐
│                                                                           │
│  URL 변경 ─▶ router/index.js ─▶ views/*View.vue ─(props)─▶ components/*   │
│                  │ (가드: 로그인 확인)     │                                │
│                  ▼                        ▼ (뷰는 api/ 폴더의 함수만 호출)   │
│            stores/auth.js          api/movies.js  (데이터 출처 전환 레이어) │
│            (Pinia, 토큰)             ├─ api/tmdb.js   ─▶ TMDB API           │
│                  │                   └─ api/django.js ─┐                   │
│                  └── 토큰을 헤더에 첨부 ─────────────────┤                   │
│                                    api/youtube.js ─▶ YouTube Data API      │
│                                    api/weather.js ─▶ Open-Meteo API        │
└────────────────────────────────────────────────────────┼──────────────────┘
                                  Authorization: Token … │
                                                         ▼
┌──────────────────────── Django REST API (:8000) ──────────────────────────┐
│  /accounts/  (dj-rest-auth) 회원가입·로그인 → 토큰 발급                     │
│  /api/v1/    (movies 앱)    영화·장르·추천·리뷰 API                         │
│                  │                                                        │
│                  ▼                                                        │
│               SQLite  ◀── loaddata ◀── fixtures ◀── problem_a.py ◀── CSV   │
└───────────────────────────────────────────────────────────────────────────┘
```

### 0-2. 프론트엔드 폴더별 책임 (설계 원칙)

| 폴더 | 책임 | 하지 않는 일 |
| :--- | :--- | :--- |
| `router/` | URL ↔ 화면(View) 연결, 로그인 필요 여부 검사 | 데이터 요청 |
| `views/` | **페이지 단위**. 데이터를 요청하고 로딩/에러 상태 관리 | HTTP 세부사항(URL, 인증) 알기 |
| `components/` | **재사용 UI 조각**. props로 받은 데이터를 그리기만 함 | 직접 API 호출 (예고편 모달은 예외 — F7 참고) |
| `api/` | 외부 서버와 통신. 인증, baseURL, 응답 가공 | 화면 그리기 |
| `stores/` | 여러 화면이 공유하는 상태 (로그인 토큰) | 화면 그리기 |
| `utils/` | 순수 함수 (입력 → 출력) | 상태 보관 |

### 0-3. 백엔드 폴더별 책임

| 경로 | 책임 |
| :--- | :--- |
| `my_api/settings.py` | 앱 등록, 인증 방식, CORS 등 서버 전역 설정 |
| `my_api/urls.py` | URL 최상위 분배 (`/api/v1/` → movies, `/accounts/` → dj-rest-auth) |
| `accounts/` | 커스텀 User 모델 |
| `movies/models.py` | 테이블 구조와 관계 |
| `movies/serializers.py` | 모델 ↔ JSON 변환, 입력 검증 |
| `movies/views.py` | 요청을 받아 ORM으로 조회/저장하고 응답 |
| `movies/tests.py` | API 동작을 자동으로 검증 |
| `problem/` | 원본 CSV, TMDB 데이터 수집, fixture 생성 스크립트 |

> 💡 **핵심 아이디어**: "누가 무엇을 아는가"를 나누면, 나중에 TMDB → Django로 바꿀 때 프론트는 `api/` 폴더만 고치면 됩니다. (F10에서 실제로 증명합니다.)

---

# Part 1. 백엔드 (Django REST API)

## B1. 프로젝트 세팅

### 🎯 목표
가상환경을 만들고 Django·DRF·인증 라이브러리를 설치한 뒤, `movies`와 `accounts` 두 앱을 가진 프로젝트를 구성한다.

### 따라하기
```bash
cd django-pjt
python -m venv venv
source venv/Scripts/activate        # Windows Git Bash (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt     # Django, djangorestframework, dj-rest-auth, django-allauth, django-cors-headers, requests

# 처음부터 만든다면:
# django-admin startproject my_api .
# python manage.py startapp movies
# python manage.py startapp accounts
```

### 코드 — `my_api/settings.py` (앱 등록)
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',          # allauth 가 필요로 함 (SITE_ID = 1 과 함께)
    'rest_framework',
    'rest_framework.authtoken',      # 토큰 테이블
    'corsheaders',
    'dj_rest_auth',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'dj_rest_auth.registration',     # 회원가입 엔드포인트
    'movies',
    'accounts',
]

SITE_ID = 1
AUTH_USER_MODEL = 'accounts.User'
```

### 코드 — `accounts/models.py`
```python
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass
```

### 🤔 왜 이렇게 했나
- **커스텀 User 모델은 첫 `migrate` 전에** 만들어야 합니다. 기본 `auth.User`로 한 번 마이그레이션한 뒤에 `AUTH_USER_MODEL`을 바꾸면, 이미 생성된 테이블과 외래 키가 꼬여서 DB를 지우고 다시 시작해야 합니다. 지금 당장 필드를 추가하지 않더라도 `pass`만 있는 `User`를 미리 만들어 두는 것이 Django 공식 권장 사항입니다.
- 다른 모델에서 User를 참조할 때는 `settings.AUTH_USER_MODEL`을 씁니다 (B2의 Review 참고). `accounts.User`를 직접 import하면 앱 간 결합이 강해집니다.
- 앱을 `movies`(영화 도메인)와 `accounts`(사용자)로 나눠, 각 앱이 자기 모델과 로직만 갖도록 했습니다.

### ✍️ 직접 해보기
- `python manage.py check`로 설정 오류가 없는지 확인해 보세요.
- `pip freeze`의 결과와 `requirements.txt`를 비교해 보세요. 새 패키지를 설치했다면 `pip freeze > requirements.txt`로 갱신해야 다른 사람도 같은 환경을 만들 수 있습니다.

---

## B2. 모델 설계와 마이그레이션

### 🎯 목표
영화(Movie), 장르(Genre), 출연진(Cast), 리뷰(Review)의 테이블과 관계를 정의한다.

### 관계도
```
User ──1:N──┐
            ▼
Movie ──1:N──▶ Review     (리뷰 하나는 영화 하나에, 작성자 한 명에 속함)
  │
  ├──1:N──▶ Cast          (출연진 한 명은 영화 하나에 속함)
  └──M:N──▶ Genre         (영화는 여러 장르, 장르는 여러 영화)
```

### 코드 — `movies/models.py`
```python
class Genre(models.Model):
    # TMDB 장르 ID를 그대로 PK로 사용
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)


class Movie(models.Model):
    # TMDB 영화 ID를 그대로 PK로 사용
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    release_date = models.DateField()
    popularity = models.FloatField()
    budget = models.IntegerField()
    revenue = models.IntegerField()
    runtime = models.IntegerField()
    # 프론트엔드 화면(카드, 상세)용 TMDB 데이터 - problem/fetch_tmdb.py 로 수집
    overview = models.TextField(blank=True)
    poster_path = models.CharField(max_length=255, blank=True)
    vote_average = models.FloatField(default=0)
    # M:N - movies_movie_genres 중개 테이블
    genres = models.ManyToManyField(Genre, related_name='movies')


class Cast(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    character = models.CharField(max_length=255)
    order = models.IntegerField()


class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.FloatField()
```

### 핵심 개념
| 개념 | 설명 |
| :--- | :--- |
| `ForeignKey` (1:N) | "N 쪽"(Cast, Review)이 "1 쪽"(Movie)의 PK를 컬럼으로 가집니다. DB에는 `movie_id` 컬럼이 생깁니다. |
| `on_delete=models.CASCADE` | 영화가 삭제되면 그 영화의 출연진·리뷰도 함께 삭제됩니다. |
| `ManyToManyField` (M:N) | 어느 한쪽에 컬럼을 둘 수 없으므로 **중개 테이블**(`movies_movie_genres`: `movie_id`, `genre_id`)이 자동 생성됩니다. |
| 역참조 이름 | `related_name`이 없으면 `movie.cast_set`, `movie.review_set`처럼 `모델명소문자_set`으로 접근합니다. Genre에는 `related_name='movies'`를 줘서 `genre.movies.all()`로 씁니다. |
| `blank=True` | 폼/Serializer 검증에서 빈 값을 허용합니다. (DB의 NULL 허용은 `null=True`로 별개) |

### 🤔 왜 PK를 TMDB ID로 했나?
자동 증가 PK(1, 2, 3...)를 쓰면 DB의 `id=1`과 TMDB의 `id=1022789`가 달라집니다. 그러면 프론트의 `/:movieId` URL이 데이터 출처에 따라 다른 영화를 가리키게 됩니다. TMDB ID를 PK로 쓰면 **`/1022789`는 TMDB 모드든 Django 모드든 항상 인사이드 아웃 2**입니다. 장르도 같은 이유로 TMDB 장르 ID(공포 = 27)를 PK로 써서, 프론트의 날씨→장르 매핑표를 두 모드에서 그대로 쓸 수 있습니다.

### 🤔 왜 author가 문자열이 아니라 User FK인가?
처음엔 CSV처럼 `author = CharField`로 둘 수도 있습니다. 하지만 그러면 "이 리뷰를 쓴 사람이 지금 요청한 사람인가?"를 확인할 수 없습니다. User를 참조해야 B6의 **작성자만 수정/삭제** 권한 검사가 가능합니다.

### 따라하기 — 마이그레이션
```bash
python manage.py makemigrations accounts movies   # 모델 → 마이그레이션 파일(설계도) 생성
python manage.py migrate                          # 설계도 → 실제 DB 테이블 생성
```
- `makemigrations`가 만든 `accounts/migrations/0001_initial.py`, `movies/migrations/0001_initial.py`는 **반드시 git에 커밋**합니다. 이 파일이 없으면 저장소를 clone한 사람이 `migrate`를 해도 테이블이 생기지 않고, 테스트도 `Dependency on app with no migrations` 오류로 실행되지 않습니다. (실제로 이 프로젝트에서 겪은 문제입니다.)
- `db.sqlite3`는 커밋하지 않습니다(`.gitignore`). DB는 마이그레이션 + fixture로 언제든 다시 만들 수 있기 때문입니다.

### ✍️ 직접 해보기
- `python manage.py sqlmigrate movies 0001`로 실제 실행될 SQL을 보고, 중개 테이블 `movies_movie_genres`가 어떻게 생겼는지 확인해 보세요.
- `python manage.py shell`에서 `Movie.objects.get(pk=1022789).review_set.all()`과 `Genre.objects.get(pk=27).movies.all()`을 실행해 보세요.

---

## B3. 초기 데이터 준비

### 🎯 목표
제공된 CSV를 정리해서 Django가 읽을 수 있는 **fixture(JSON)** 로 바꾸고 DB에 넣는다. CSV에 없는 화면용 데이터(줄거리·포스터·평점)는 TMDB에서 수집한다.

### 전체 흐름
```
[필요할 때만] fetch_tmdb.py ── TMDB 상세 API ──▶ problem/data/movie_tmdb.csv
                                                        │
problem/data/*.csv (movies, movie_details, movie_cast, movie_reviews) ──┤
                                                        ▼
                         problem_a.py ──▶ accounts/fixtures/users.json
                                          movies/fixtures/genres.json, movies.json, casts.json, reviews.json
                                                        │
                         python manage.py loaddata ... ─▶ SQLite
```

### 3-1. 원본 CSV의 문제점
| 파일 | 문제 | 해결 |
| :--- | :--- | :--- |
| `movies.csv` + `movie_details.csv` | 영화 정보가 두 파일로 나뉨 | `movie_id` 기준으로 합침 |
| `movie_details.csv` | 장르가 `"Animation, Family, Drama"` 같은 문자열 | 장르 이름 → TMDB 장르 ID로 매핑해 M:N 목록으로 |
| `movie_cast.csv` | `cast_id`가 영화마다 0부터 다시 시작해 중복 | CSV 순서대로 1부터 PK 재부여 |
| `movie_reviews.csv` | `review_id`가 `666193da...` 같은 16진 문자열 | CSV 순서대로 1부터 PK 재부여 |
| `movie_reviews.csv` | 작성자가 문자열인데 모델은 User FK | 작성자 이름마다 User 계정 생성 후 PK로 연결 |
| 전체 | 화면에 필요한 줄거리·포스터·평점이 없음 | TMDB API로 수집 (3-2) |

### 3-2. TMDB 데이터 수집 — `problem/fetch_tmdb.py`
```python
def tmdb_session(api_key):
    session = requests.Session()
    # v4 Read Access Token(JWT)은 Bearer 헤더, v3 API Key 는 api_key 쿼리로 인증
    if api_key.startswith('eyJ'):
        session.headers['Authorization'] = f'Bearer {api_key}'
    else:
        session.params = {'api_key': api_key}
    return session


def fetch_movie(session, movie_id):
    response = session.get(TMDB_URL.format(movie_id=movie_id), params={'language': 'ko-KR'}, timeout=10)
    response.raise_for_status()
    movie = response.json()
    overview = movie['overview']
    # 한국어 줄거리가 없는 영화는 영어 줄거리로 대체
    if not overview:
        ...
    return {
        'movie_id': movie_id,
        'overview': overview,
        'poster_path': movie['poster_path'] or '',
        'vote_average': movie['vote_average'],
    }
```
실행:
```bash
TMDB_API_KEY=<v3 키 또는 v4 토큰> python problem/fetch_tmdb.py
# → problem/data/movie_tmdb.csv: 20개
```
- **결과 CSV를 git에 커밋**해 두었습니다. 그래서 다른 사람은 TMDB 키 없이도 같은 데이터로 프로젝트를 실행할 수 있고, 이 스크립트는 데이터를 새로 받고 싶을 때만 실행합니다.
- API 키는 코드에 쓰지 않고 **환경 변수**로 받습니다.
- `requests.Session`에 인증 정보를 한 번 넣어 두면 이후 요청에 자동으로 붙습니다. (프론트의 `axios.create`와 같은 발상 — F3 참고)
- `raise_for_status()`: 401(키 오류), 404(없는 영화) 같은 응답을 조용히 넘기지 않고 예외로 바꿔, 잘못된 데이터가 CSV에 들어가는 것을 막습니다.

### 3-3. CSV → fixture 변환 — `problem/problem_a.py`
```python
# 'Animation, Family' -> [16, 10751]
def to_genre_ids(genres_text):
    genre_ids = []
    for name in genres_text.split(', '):
        if name not in GENRE_IDS:
            raise ValueError(f'매핑에 없는 장르 이름입니다: {name}')
        genre_ids.append(GENRE_IDS[name])
    return genre_ids


# movies.csv, movie_details.csv, movie_tmdb.csv 를 movie_id 기준으로 통합
def make_movies(movies, details, tmdb_rows):
    details_by_movie = {row['movie_id']: row for row in details}
    tmdb_by_movie = {row['movie_id']: row for row in tmdb_rows}
    fixtures = []
    for row in movies:
        detail = details_by_movie[row['id']]
        tmdb = tmdb_by_movie[row['id']]
        fixtures.append({
            'model': 'movies.movie',
            'pk': int(row['id']),
            'fields': {
                'title': row['title'],
                ...
                'overview': tmdb['overview'],
                'poster_path': tmdb['poster_path'],
                'vote_average': float(tmdb['vote_average']),
                'genres': to_genre_ids(detail['genres']),
            },
        })
    return fixtures


# Review.author 가 User FK 이므로 CSV 의 작성자 이름마다 로그인 불가 계정을 만든다
def make_users(reviews):
    authors = list(dict.fromkeys(row['author'] for row in reviews))
    return [
        {
            'model': 'accounts.user',
            'pk': pk,
            # '!' 로 시작하는 비밀번호는 Django 에서 사용할 수 없는 비밀번호로 취급된다
            'fields': {'username': author, 'password': '!'},
        }
        for pk, author in enumerate(authors, start=1)
    ]
```

### 핵심 개념
- **fixture 형식**: `{"model": "앱.모델", "pk": 값, "fields": {...}}`의 배열입니다. M:N 필드는 상대 PK 목록(`"genres": [16, 10751]`), FK 필드는 상대 PK(`"movie": 1022789`)로 씁니다.
- **딕셔너리로 조인**: `{row['movie_id']: row for row in details}`처럼 키로 찾을 수 있는 딕셔너리를 먼저 만들면, 영화마다 리스트 전체를 뒤지지 않고 바로 찾을 수 있습니다 (O(n²) → O(n)).
- **`dict.fromkeys(...)`로 순서 유지 중복 제거**: `set`은 순서가 바뀌지만 `dict`는 넣은 순서를 지킵니다. 그래서 실행할 때마다 같은 사용자에게 같은 PK가 붙습니다.
- **모르는 값은 조용히 넘기지 않기**: 매핑에 없는 장르 이름이 나오면 `ValueError`로 멈춥니다. 조용히 건너뛰면 장르가 빠진 영화가 생겨도 알아채기 어렵습니다.
- **로그인 불가 비밀번호 `!`**: CSV 작성자 계정은 리뷰를 연결하기 위한 것일 뿐 실제로 로그인하면 안 됩니다. Django는 `!`로 시작하는 비밀번호 해시를 "사용 불가"로 취급합니다.

### 따라하기 — 데이터 적재
```bash
python problem/problem_a.py
python manage.py loaddata users.json genres.json movies.json casts.json reviews.json
# Installed 198 object(s) from 5 fixture(s)
```
- **순서가 중요합니다.** Review는 User와 Movie를, Movie는 Genre를 참조하므로 참조당하는 쪽을 먼저 넣습니다. (한 번의 `loaddata` 명령에 모두 넘기면 Django가 한 트랜잭션으로 처리합니다.)
- `loaddata`는 각 앱의 `fixtures/` 폴더에서 파일 이름으로 찾습니다.

### ✍️ 직접 해보기
- `movie_details.csv`에 없는 장르 이름(`"Western"`)을 하나 넣고 `problem_a.py`를 실행해 오류 메시지를 확인해 보세요.
- `python manage.py createsuperuser`로 관리자를 만들고 `/admin/`에서 적재된 데이터를 둘러보세요.

---

## B4. 조회 API — Serializer, View, URL

### 🎯 목표
장르 목록, 영화 목록, 영화 상세를 JSON으로 내려준다.

### 요청이 처리되는 흐름
```
GET /api/v1/movies/1022789/
  → my_api/urls.py   : 'api/v1/' 로 시작 → movies.urls 로 넘김
  → movies/urls.py   : 'movies/<int:movie_pk>/' → views.movie_detail(request, movie_pk=1022789)
  → views.py         : ORM 으로 조회 → Serializer 로 dict 변환 → Response(JSON)
```

### 코드 — URL
```python
# my_api/urls.py
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('movies.urls')),
    path('accounts/', include('dj_rest_auth.urls')),
    path('accounts/signup/', include('dj_rest_auth.registration.urls')),
]

# movies/urls.py
urlpatterns = [
    path('genres/', views.genre_list),
    path('movies/', views.movie_list),
    path('movies/recommend/', views.movie_recommend),
    path('movies/<int:movie_pk>/', views.movie_detail),
    path('movies/<int:movie_pk>/reviews/', views.review_create),
    path('reviews/', views.review_list),
    path('reviews/<int:review_pk>/', views.review_detail),
]
```
- API 버전을 URL에 넣으면(`/api/v1/`) 나중에 응답 형식을 크게 바꿀 때 `/api/v2/`를 따로 열어 기존 클라이언트를 깨뜨리지 않을 수 있습니다.
- `<int:movie_pk>`는 **숫자만** 매칭합니다. 그래서 `movies/recommend/`와 충돌하지 않지만, 정적 경로를 동적 경로보다 위에 두는 습관이 안전합니다. (프론트 F2의 Vue 라우터와 같은 원리)

### 코드 — `movies/serializers.py`
```python
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('id', 'name')


# 영화 목록 - genres 는 장르 id 목록으로
class MovieListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'


# 영화 상세 - 영화를 참조하는 Cast, Review 와 M:N 관계의 Genre 이름을 함께
class MovieSerializer(serializers.ModelSerializer):
    class GenreNameSerializer(serializers.ModelSerializer):
        class Meta:
            model = Genre
            fields = ('name',)

    class CastSerializer(serializers.ModelSerializer):
        class Meta:
            model = Cast
            fields = ('name', 'character', 'order')

    class MovieReviewSerializer(serializers.ModelSerializer):
        author = serializers.ReadOnlyField(source='author.username')

        class Meta:
            model = Review
            fields = ('author', 'content', 'rating')

    genres = GenreNameSerializer(many=True, read_only=True)
    cast_set = CastSerializer(many=True, read_only=True)
    review_set = MovieReviewSerializer(many=True, read_only=True)
    # B7: view 에서 Avg / Count 로 annotate 한 값
    average_rating = serializers.FloatField(read_only=True)
    vote_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Movie
        fields = (
            'id', 'title', 'release_date', 'popularity', 'budget', 'revenue', 'runtime',
            'overview', 'poster_path', 'vote_average',
            'genres', 'cast_set', 'review_set', 'average_rating', 'vote_count',
        )
```

### 핵심 개념 — Serializer
- **Serializer = 번역기**. 모델 객체 ↔ JSON(dict)을 양방향으로 바꾸고, 들어오는 데이터는 검증까지 합니다.
- `ModelSerializer`는 모델 필드를 보고 Serializer 필드를 자동으로 만들어 줍니다. M:N 필드는 기본적으로 **PK 목록**(`"genres": [16, 10751]`)으로 나갑니다 → 목록 API는 이 기본 동작을 그대로 씁니다.
- **중첩 Serializer**: 필드 자리에 다른 Serializer를 넣으면 그 객체를 펼쳐서 보여줍니다. `many=True`는 "여러 개(목록)"라는 뜻입니다.
  - `genres = GenreNameSerializer(many=True)` → `"genres": [{"name": "Animation"}, ...]`
  - `cast_set = CastSerializer(many=True)` → 역참조 이름(`cast_set`)을 그대로 필드 이름으로 씁니다.
- **Serializer 안의 Serializer 클래스**: 상세 응답에서만 쓰는 작은 Serializer는 `MovieSerializer` 안에 정의해서, 다른 곳에서 실수로 재사용하지 않도록 범위를 좁혔습니다.
- `ReadOnlyField(source='author.username')`: User 객체 전체 대신 `username` 문자열만 보여줍니다. `source`로 점(.) 경로를 따라갈 수 있습니다.

### 코드 — `movies/views.py` (조회)
```python
@api_view(['GET'])
def genre_list(request):
    genres = Genre.objects.all()
    serializer = GenreSerializer(genres, many=True)
    return Response(serializer.data)


# 프론트엔드의 최고 평점 목록용으로 평점 높은 순
@api_view(['GET'])
def movie_list(request):
    movies = Movie.objects.prefetch_related('genres').order_by('-vote_average')
    serializer = MovieListSerializer(movies, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def movie_detail(request, movie_pk):
    movies = Movie.objects.annotate(
        average_rating=Avg('review__rating'),
        vote_count=Count('review__rating'),
    ).prefetch_related('genres', 'cast_set', 'review_set__author')
    movie = get_object_or_404(movies, pk=movie_pk)
    serializer = MovieSerializer(movie)
    return Response(serializer.data)
```

### 핵심 개념 — View
| 코드 | 의미 |
| :--- | :--- |
| `@api_view(['GET'])` | DRF 함수형 뷰. 허용하지 않은 메서드(POST 등)는 자동으로 **405** 응답. 인증·권한 설정도 이 데코레이터를 통해 적용됩니다. |
| `get_object_or_404` | 없는 PK면 500 에러 대신 **404** 응답 |
| `order_by('-vote_average')` | `-`는 내림차순. 프론트의 "최고 평점" 화면과 순서를 맞췄습니다. |
| `Response(serializer.data)` | dict를 JSON으로 바꿔 응답. 브라우저로 열면 DRF가 보기 좋은 HTML 화면으로 보여줍니다. |

### 🐛 N+1 쿼리 문제와 `prefetch_related`
영화 20편의 장르를 보여준다고 해봅시다.
- 아무 처리 없이: 영화 목록 1번 + **영화마다 장르 조회 20번** = 21번 쿼리 (N+1)
- `prefetch_related('genres')`: 영화 목록 1번 + 장르 전체 1번 = **2번 쿼리**. Django가 파이썬에서 짝을 맞춰 줍니다.
- `select_related`는 FK(1:1, N:1)를 **SQL JOIN**으로 한 번에 가져옵니다. 리뷰 목록에서 `select_related('movie', 'author')`를 쓴 이유입니다.
- `review_set__author`처럼 `__`로 이어 쓰면 "리뷰들, 그리고 그 리뷰들의 작성자"까지 미리 가져옵니다.

| | 대상 | 방식 |
| :--- | :--- | :--- |
| `select_related` | FK, 1:1 (정방향, 하나) | SQL JOIN 한 번 |
| `prefetch_related` | M:N, 역참조(`_set`, 여러 개) | 쿼리를 따로 한 번 더 보내고 파이썬에서 연결 |

### ✍️ 직접 해보기
- 서버를 켜고 브라우저에서 `http://127.0.0.1:8000/api/v1/genres/`를 열어 보세요. 토큰이 없어서 401이 뜹니다(B6). `settings.py`의 `DEFAULT_PERMISSION_CLASSES`를 잠깐 주석 처리하면 DRF 화면을 볼 수 있습니다.
- `prefetch_related`를 지운 뒤 `django.db.connection.queries`로 쿼리 수가 어떻게 달라지는지 비교해 보세요.

---

## B5. 리뷰 CRUD API

### 🎯 목표
리뷰를 조회(GET)·전체 수정(PUT)·부분 수정(PATCH)·삭제(DELETE)하고, 특정 영화에 리뷰를 생성(POST)한다.

### 코드 — `ReviewSerializer`
```python
class ReviewSerializer(serializers.ModelSerializer):
    class MovieTitleSerializer(serializers.ModelSerializer):
        class Meta:
            model = Movie
            fields = ('id', 'title')

    movie = MovieTitleSerializer(read_only=True)
    # 작성자는 요청한 유저로 저장되므로 입력받지 않고 username 만 보여준다
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Review
        fields = ('id', 'movie', 'author', 'content', 'rating')
```
- 리뷰 응답의 `movie`는 영화 전체가 아니라 `{id, title}`만 보여줍니다. 리뷰 목록에서 영화 정보 전체를 반복하면 응답이 불필요하게 커지기 때문입니다.
- `movie`와 `author`는 **읽기 전용**입니다. 클라이언트가 보낸 값으로 바꿀 수 없고, 서버가 URL(`movie_pk`)과 토큰(`request.user`)으로 정합니다. → 다른 사람 이름으로 리뷰를 쓰는 것이 원천적으로 불가능합니다.

### 코드 — `movies/views.py` (리뷰)
```python
@api_view(['GET'])
def review_list(request):
    reviews = Review.objects.select_related('movie', 'author')
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def review_detail(request, review_pk):
    review = get_object_or_404(Review.objects.select_related('movie', 'author'), pk=review_pk)

    if request.method == 'GET':
        serializer = ReviewSerializer(review)
        return Response(serializer.data)

    # 수정/삭제는 작성자 본인만 (B6)
    if review.author != request.user:
        return Response({'detail': '리뷰 작성자만 수정/삭제할 수 있습니다.'}, status=status.HTTP_403_FORBIDDEN)

    if request.method in ('PUT', 'PATCH'):
        # PUT 은 모든 필드가 필요하고, PATCH 는 일부 필드만 보내도 된다
        serializer = ReviewSerializer(review, data=request.data, partial=request.method == 'PATCH')
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

    elif request.method == 'DELETE':
        review.delete()
        return Response(
            {'delete': f'{review_pk}번 째 리뷰가 정상적으로 삭제되었습니다.'},
            status=status.HTTP_204_NO_CONTENT,
        )


@api_view(['POST'])
def review_create(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(movie=movie, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
```

### 핵심 개념
| 메서드 | 의미 | 성공 코드 | 이 프로젝트의 구현 |
| :--- | :--- | :--- | :--- |
| GET | 조회 | 200 | `ReviewSerializer(review)` |
| POST | 생성 | **201** Created | `serializer.save(movie=..., author=...)` |
| PUT | **전체** 교체 | 200 | `ReviewSerializer(review, data=...)` — content, rating 중 하나라도 빠지면 400 |
| PATCH | **일부** 수정 | 200 | `partial=True` — 보낸 필드만 바꿈 |
| DELETE | 삭제 | **204** No Content | `review.delete()` |

- **`Serializer(instance, data=...)`**: 첫 인자로 기존 객체를 주면 `save()`가 **수정**(update), 안 주면 **생성**(create)이 됩니다.
- **`partial=request.method == 'PATCH'`**: 비교식의 결과(True/False)를 그대로 넘겨서 PUT과 PATCH를 같은 코드로 처리합니다.
- **`is_valid(raise_exception=True)`**: 검증 실패 시 직접 `return Response(errors, 400)`을 쓰지 않아도 DRF가 **400 응답**과 오류 내용을 만들어 줍니다.
- **`save(movie=movie, author=request.user)`**: 검증을 통과한 데이터에 **서버가 정한 값**을 추가로 넣어 저장합니다.
- 204는 원래 "본문 없음"을 뜻합니다. 이 프로젝트는 삭제 확인 메시지를 함께 보냈지만, HTTP 클라이언트에 따라 본문을 무시할 수 있다는 점을 알아 두세요.

### ✍️ 직접 해보기 (토큰 발급은 B6 참고)
```bash
TOKEN=<로그인으로 받은 토큰>
curl -X POST http://127.0.0.1:8000/api/v1/movies/1022789/reviews/ \
  -H "Authorization: Token $TOKEN" -H "Content-Type: application/json" \
  -d '{"content": "재밌어요", "rating": 4.5}'

# rating 없이 PUT → 400 과 {"rating": ["이 필드는 필수 항목입니다."]}
curl -X PUT http://127.0.0.1:8000/api/v1/reviews/<방금 만든 id>/ \
  -H "Authorization: Token $TOKEN" -H "Content-Type: application/json" -d '{"content": "수정"}'
```

---

## B6. 회원가입·로그인과 권한

### 🎯 목표
dj-rest-auth로 회원가입·로그인을 만들고, 로그인 시 토큰을 발급한다. 회원가입·로그인을 제외한 모든 API는 토큰이 있어야 쓸 수 있고, 리뷰 수정·삭제는 작성자만 할 수 있다.

### 코드 — `my_api/settings.py`
```python
REST_FRAMEWORK = {
    # 토큰 인증
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    # 회원가입/로그인(dj-rest-auth 가 AllowAny 로 지정)을 제외한 모든 API 는 인증 필요
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# dj-rest-auth 회원가입: username + password 로 가입 (이메일 인증 없음)
ACCOUNT_LOGIN_METHODS = {'username'}
# email 은 선택 항목 (목록에서 빼면 dj-rest-auth 가 필수로 취급한다)
ACCOUNT_SIGNUP_FIELDS = ['username*', 'email', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'none'
```
URL은 B4의 `my_api/urls.py`에서 `/accounts/`(로그인·로그아웃 등)와 `/accounts/signup/`(회원가입)으로 연결했습니다.

### 토큰 인증의 흐름
```
① POST /accounts/signup/  {username, password1, password2}  → 201 {"key": "45e9b7..."}
② POST /accounts/login/   {username, password}              → 200 {"key": "45e9b7..."}
③ GET  /api/v1/movies/    헤더 Authorization: Token 45e9b7... → 200 영화 목록
④ GET  /api/v1/movies/    (헤더 없음)                        → 401
```
- 서버는 `authtoken_token` 테이블에 `토큰 ↔ 사용자`를 저장합니다. 요청이 오면 `TokenAuthentication`이 헤더의 토큰으로 사용자를 찾아 `request.user`에 넣어 줍니다.
- 세션 쿠키 방식과 달리, 클라이언트가 헤더 한 줄만 붙이면 되므로 **다른 출처의 SPA**에서 쓰기 간단합니다.

### 핵심 개념 — 인증(Authentication) vs 권한(Authorization)
| | 질문 | 실패 시 | 이 프로젝트에서 |
| :--- | :--- | :--- | :--- |
| 인증 | **누구**인가? | 401 Unauthorized | `TokenAuthentication` + `IsAuthenticated` (전역 설정) |
| 권한 | 이 일을 **해도 되는가**? | 403 Forbidden | 리뷰 수정·삭제 시 `review.author != request.user` 검사 (B5) |

- **전역 기본값을 "인증 필요"로** 두었습니다. 새 API를 만들 때 깜빡해도 기본이 잠겨 있으므로 안전합니다. 회원가입·로그인 뷰는 dj-rest-auth가 `AllowAny`로 따로 열어 둡니다.
- 조회(GET)는 다른 사용자의 리뷰도 볼 수 있어야 하므로 권한 검사를 GET 분기 **뒤에** 두었습니다.

### 🤔 왜 dj-rest-auth를 썼나
회원가입(비밀번호 확인, 중복 아이디, 비밀번호 규칙 검증), 로그인, 토큰 발급, 로그아웃을 직접 만들면 코드가 많고 보안 실수가 생기기 쉽습니다. dj-rest-auth는 이 엔드포인트들을 검증된 구현으로 제공하고, 내부적으로 allauth를 써서 가입 규칙을 설정만으로 바꿀 수 있습니다. 비밀번호 규칙은 Django의 `AUTH_PASSWORD_VALIDATORS`(너무 짧은 비밀번호, 흔한 비밀번호, 숫자만 있는 비밀번호 거부)가 그대로 적용됩니다.

### ✍️ 직접 해보기
```bash
curl -X POST http://127.0.0.1:8000/accounts/signup/ -H "Content-Type: application/json" \
  -d '{"username": "tester", "password1": "Movie-flix-2026!", "password2": "Movie-flix-2026!"}'
```
- 비밀번호를 `1234`로 바꿔 보내고 어떤 검증 메시지가 오는지 확인해 보세요.
- 다른 사용자로 로그인해서 남의 리뷰를 PATCH 하면 403이 오는지 확인해 보세요.

---

## B7. 평점 통계 — annotate

### 🎯 목표
영화 상세 응답에 그 영화 리뷰들의 **평균 평점**(`average_rating`)과 **리뷰 수**(`vote_count`)를 함께 내려준다.

### 코드 (B4의 `movie_detail` 다시 보기)
```python
movies = Movie.objects.annotate(
    average_rating=Avg('review__rating'),
    # rating 값이 있는 리뷰만 센다
    vote_count=Count('review__rating'),
).prefetch_related('genres', 'cast_set', 'review_set__author')
movie = get_object_or_404(movies, pk=movie_pk)
```
그리고 Serializer에는 모델에 없는 필드를 선언해 둡니다.
```python
average_rating = serializers.FloatField(read_only=True)
vote_count = serializers.IntegerField(read_only=True)
```

### 핵심 개념
- **`annotate`**: QuerySet의 **각 행에** 계산한 값을 붙입니다. SQL로는 `LEFT JOIN review ... GROUP BY movie.id`와 `AVG()`, `COUNT()`가 됩니다. 결과 객체에 `movie.average_rating`처럼 속성으로 생깁니다.
- **`review__rating`**: 더블 언더스코어로 관계를 따라갑니다. "이 영화를 참조하는 Review들의 rating".
- **`Count('review__rating')` vs `Count('review')`**: 전자는 rating이 NULL이 아닌 리뷰만 셉니다. "평점이 있는 리뷰 수"라는 의미를 정확히 표현했습니다.
- 리뷰가 없으면 `Avg`는 `None` → JSON에서 `null`, `Count`는 `0`입니다.
- **DB에서 계산하는 이유**: 파이썬에서 `sum(r.rating for r in movie.review_set.all()) / len(...)`로 계산하면 리뷰를 전부 메모리로 가져와야 합니다. DB 집계는 숫자 하나만 돌려줍니다.
- `SerializerMethodField`로도 구현할 수 있지만, 그 안에서 쿼리를 보내면 목록에서 쓸 때 다시 N+1 문제가 생깁니다. `annotate`는 쿼리 한 번에 끝납니다.

### `aggregate` vs `annotate` (B8에서도 씁니다)
| | 결과 | 예 |
| :--- | :--- | :--- |
| `aggregate` | QuerySet **전체를 값 하나**로 요약한 dict | `Movie.objects.aggregate(total=Count('id'))` → `{'total': 20}` |
| `annotate` | **각 행마다** 계산 값을 붙인 QuerySet | 영화마다 `average_rating` |

### ✍️ 직접 해보기
- `python manage.py shell`에서 `print(Movie.objects.annotate(a=Avg('review__rating')).query)`로 생성되는 SQL을 확인해 보세요.

---

## B8. 날씨 추천 API — Count와 랜덤 offset

### 🎯 목표
프론트에서 날씨에 맞는 장르 id를 보내면, 그 장르의 영화 중 **1편을 랜덤으로** 골라 준다.
`GET /api/v1/movies/recommend/?genre=27`

### 코드 — `movies/views.py`
```python
@api_view(['GET'])
def movie_recommend(request):
    genre_id = request.query_params.get('genre')
    if not genre_id or not genre_id.isdigit():
        return Response({'detail': 'genre 쿼리 파라미터(장르 id)가 필요합니다.'}, status=status.HTTP_400_BAD_REQUEST)

    movies = Movie.objects.filter(genres=genre_id)
    # order_by('?') 는 전체를 랜덤 정렬하므로, Count 로 개수를 구한 뒤 랜덤 offset 1건만 조회
    total = movies.aggregate(total=Count('id'))['total']
    if not total:
        return Response({'detail': '해당 장르의 영화가 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

    movie = movies.order_by('id').prefetch_related('genres')[random.randrange(total)]
    serializer = MovieListSerializer(movie)
    return Response(serializer.data)
```

### 핵심 개념
- **입력 검증**: 쿼리 파라미터는 항상 문자열이고, 사용자가 아무 값이나 보낼 수 있습니다. 없거나 숫자가 아니면 **400 Bad Request**로 거절합니다.
- **`filter(genres=genre_id)`**: M:N 필드에 값을 주면 중개 테이블을 JOIN해서 "이 장르를 가진 영화"를 찾습니다.
- **왜 `order_by('?')`를 안 썼나?** `?`는 SQL의 `ORDER BY RANDOM()` → 후보 모든 행에 난수를 매기고 **전체를 정렬**합니다. 데이터가 많아지면 느려집니다. 대신:
  1. `aggregate(Count('id'))`로 후보 **개수만** 셉니다 (`SELECT COUNT(...)`)
  2. `random.randrange(total)`로 `0 ~ total-1` 중 위치 하나를 고릅니다
  3. `[n]` 인덱싱 → SQL `LIMIT 1 OFFSET n`으로 **딱 1건만** 가져옵니다
- **`order_by('id')`를 붙인 이유**: 정렬 없는 OFFSET은 DB가 순서를 보장하지 않아, 같은 n이라도 다른 행이 나올 수 있습니다.
- **응답 형태를 목록 API와 같게** (`MovieListSerializer`): 프론트는 추천 결과를 목록과 같은 `MovieCard`로 그리므로 필드 구성이 같아야 합니다.
- 해당 장르 영화가 없으면 404를 주고, 프론트는 이를 "추천할 영화가 없습니다"로 보여줍니다 (F11).

### ✍️ 직접 해보기
- 같은 요청을 여러 번 보내 결과가 바뀌는지 확인해 보세요.
- `?genre=10770`(TV 영화, 데이터에 없음), `?genre=abc`, 파라미터 없이 보냈을 때 각각 404, 400, 400이 오는지 확인해 보세요.

---

## B9. CORS 설정

### 🎯 목표
Vite 개발 서버(`localhost:5173`)에서 Django(`127.0.0.1:8000`)로 보내는 요청을 브라우저가 막지 않게 한다.

### 코드 — `my_api/settings.py`
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',          # ← CommonMiddleware 보다 위
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]
```

### 핵심 개념
- **출처(Origin) = 프로토콜 + 도메인 + 포트**. `localhost:5173`과 `127.0.0.1:8000`은 포트가 달라 **다른 출처**입니다. (`localhost`와 `127.0.0.1`도 서로 다른 출처라 둘 다 등록했습니다.)
- 브라우저는 다른 출처의 응답을 기본적으로 막습니다 (Same-Origin Policy). 서버가 `Access-Control-Allow-Origin` 헤더로 "이 출처는 허용"이라고 알려줘야 합니다.
- **사전 요청(preflight)**: `Authorization` 같은 커스텀 헤더를 붙인 요청은 브라우저가 먼저 `OPTIONS` 요청을 보내 허용 여부를 묻습니다. `django-cors-headers`가 이 응답을 대신 처리해 줍니다.
- `CorsMiddleware`가 위에 있어야 하는 이유: `CommonMiddleware`가 먼저 리다이렉트 응답(예: 끝 슬래시 추가) 등을 만들어버리면 CORS 헤더가 안 붙습니다.
- ⚠️ CORS는 **브라우저**의 보안 정책입니다. Postman이나 `curl`로는 CORS 설정 없이도 잘 되기 때문에 "Postman에선 되는데 Vue에선 안 돼요"의 단골 원인입니다.

### ✍️ 직접 해보기
```bash
curl -i -X OPTIONS http://127.0.0.1:8000/api/v1/movies/ \
  -H "Origin: http://localhost:5173" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: authorization"
```
응답 헤더에 `access-control-allow-origin: http://localhost:5173`이 있는지 확인해 보세요. `Origin`을 `http://localhost:3000`으로 바꾸면 이 헤더가 사라집니다.

---

## B10. 테스트

### 🎯 목표
모든 API의 정상 동작과 예외 상황(400, 401, 403, 404)을 자동으로 검증해서, 코드를 고친 뒤에도 기존 기능이 깨지지 않았는지 바로 확인할 수 있게 한다.

### 코드 — `movies/tests.py` (발췌)
```python
class MovieApiTests(APITestCase):
    fixtures = ['users.json', 'genres.json', 'movies.json', 'casts.json', 'reviews.json']

    def setUp(self):
        # 리뷰 1번(Inside Out 2)의 작성자 Hotplix 로 인증
        self.author = Review.objects.get(pk=1).author
        self.login(self.author)

    def login(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    def test_movie_list(self):
        response = self.client.get('/api/v1/movies/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 20)
        # 평점 높은 순
        averages = [movie['vote_average'] for movie in response.data]
        self.assertEqual(averages, sorted(averages, reverse=True))

    def test_movie_recommend_invalid_genre(self):
        self.assertEqual(self.client.get('/api/v1/movies/recommend/').status_code, 400)
        self.assertEqual(self.client.get('/api/v1/movies/recommend/', {'genre': 'abc'}).status_code, 400)
        # 영화가 없는 장르(TV 영화)
        self.assertEqual(self.client.get('/api/v1/movies/recommend/', {'genre': 10770}).status_code, 404)

    def test_requires_token(self):
        self.client.credentials()          # 헤더 제거
        self.assertEqual(self.client.get('/api/v1/movies/').status_code, 401)

    def test_only_author_can_modify(self):
        self.login(User.objects.create_user(username='other', password='pw-for-test-123'))
        self.assertEqual(self.client.get('/api/v1/reviews/1/').status_code, 200)
        self.assertEqual(self.client.patch('/api/v1/reviews/1/', {'rating': 1}).status_code, 403)
        self.assertEqual(self.client.delete('/api/v1/reviews/1/').status_code, 403)
```

### 테스트 목록 (16개)
| 분류 | 테스트 |
| :--- | :--- |
| 조회 | 장르 목록, 영화 목록(필드·평점순), 영화 상세(중첩 필드·줄거리·포스터·통계), 없는 영화 404, 리뷰 목록, 리뷰 조회 |
| 리뷰 CUD | PUT 전체 수정, PUT 필드 누락 400, PATCH 부분 수정, DELETE 204, 리뷰 생성 201 |
| 추천 | 장르 추천 성공, 잘못된 장르 400·404 |
| 인증·권한 | 토큰 없음 401, 작성자 아닌 사용자 403, 회원가입 → 로그인 → 토큰으로 요청 |

### 핵심 개념
- **`APITestCase`**: 테스트마다 **빈 테스트 DB**를 만들고 끝나면 지웁니다. 실제 `db.sqlite3`는 건드리지 않습니다. 각 테스트는 트랜잭션으로 감싸져서, 한 테스트에서 리뷰를 삭제해도 다음 테스트에는 영향이 없습니다.
- **`fixtures = [...]`**: 실제 서비스와 같은 데이터를 테스트 DB에 넣고 시작합니다.
- **`self.client.credentials(...)`**: 이후 모든 요청에 헤더를 붙입니다. 인자 없이 부르면 헤더를 제거합니다.
- **예외 케이스를 꼭 테스트**: "잘 되는 경우"만 확인하면 권한 검사를 실수로 지워도 모릅니다. 401·403 테스트가 보안 회귀를 잡아 줍니다.
- 테스트는 마이그레이션 파일로 테스트 DB를 만들기 때문에, 마이그레이션 파일이 없으면 실행조차 되지 않습니다 (B2 참고).

### 따라하기
```bash
python manage.py test movies
# Found 16 test(s). ... OK
```

### ✍️ 직접 해보기
- `review_detail`의 작성자 검사 `if review.author != request.user:` 블록을 주석 처리하고 테스트를 돌려, 어떤 테스트가 실패하는지 확인해 보세요.

---

# Part 2. 프론트엔드 (Vue SPA)

## F1. Vue 프로젝트 생성과 진입점

### 🎯 목표
Vite 기반 Vue 3 프로젝트를 만들고, 라이브러리(Bootstrap, Router, Pinia)를 앱에 연결한다.

### 따라하기
```bash
npm create vue@latest my-vue-pjt   # Router, Pinia 선택
cd my-vue-pjt
npm install
npm install axios bootstrap
```

### 코드 — `my-vue-pjt/src/main.js`
```js
import 'bootstrap/dist/css/bootstrap.min.css'   // ① CSS는 가장 먼저 (뒤에 오는 main.css가 덮어쓸 수 있도록)
import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

const app = createApp(App)   // ② 루트 컴포넌트로 앱 인스턴스 생성
app.use(createPinia())       // ③ 플러그인 등록 (Pinia를 라우터보다 먼저: 라우터 가드가 store를 씀)
app.use(router)
app.mount('#app')            // ④ index.html 의 <div id="app"> 에 마운트
```

### 🤔 왜 이렇게 했나
- **CSS import 순서가 중요합니다.** 나중에 import한 CSS가 우선순위가 같을 때 이깁니다. Bootstrap을 먼저, 커스텀 `main.css`를 나중에 둬야 커스텀 스타일이 적용됩니다.
- Bootstrap은 **CSS만** 가져왔습니다. 모달을 Bootstrap JS 대신 Vue로 직접 제어하기 때문입니다 (F6).
- `@/` 경로 별칭은 `vite.config.js`의 `resolve.alias`에 `@ → ./src`로 설정되어 있어 `../../` 지옥을 피할 수 있습니다.

### 🔐 환경 변수 (`.env`)
```env
VITE_TMDB_API_KEY=...
VITE_YOUTUBE_API_KEY=...
VITE_MOVIE_API_SOURCE=tmdb          # 또는 django
VITE_DJANGO_API_URL=http://127.0.0.1:8000/api/v1
```
- Vite는 **`VITE_` 접두사가 붙은 변수만** `import.meta.env.XXX`로 노출합니다.
- `.env`는 `.gitignore`에 넣고, 대신 값이 비어있는 `.env.example`을 커밋해서 다른 사람이 어떤 키가 필요한지 알게 합니다.
- `.env`를 바꾼 뒤에는 **`npm run dev`를 재시작**해야 반영됩니다.
- ⚠️ 주의: `VITE_` 변수는 **빌드 결과물 JS에 그대로 박힙니다.** 즉 브라우저에서 누구나 볼 수 있습니다. 실서비스에서는 키를 백엔드에 숨겨야 합니다.

### ✍️ 직접 해보기
- `console.log(import.meta.env)`를 찍어보고, `VITE_` 없는 변수를 `.env`에 추가하면 보이는지 확인해 보세요.

---

## F2. 라우터와 네비게이션 바

### 🎯 목표
URL에 따라 다른 페이지(View)가 보이도록 하고, 상단 메뉴로 이동할 수 있게 한다.

### 코드 — `src/router/index.js` (라우트 부분)
```js
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    // usesMovieApi: 영화 데이터를 불러오는 페이지 (Django 출처일 때 로그인 필요 — F9)
    { path: '/movies', name: 'movies', component: MovieListView, meta: { usesMovieApi: true } },
    { path: '/review-search', name: 'reviewSearch', component: ReviewSearchView },
    { path: '/recommended', name: 'recommended', component: RecommendedView, meta: { usesMovieApi: true } },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/signup', name: 'signup', component: SignupView },
    // 숫자 ID만 상세 페이지로 매칭되도록 제한 (정적 경로와의 충돌 방지)
    { path: '/:movieId(\\d+)', name: 'movieDetail', component: MovieDetailView, meta: { usesMovieApi: true } },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})
```

### 핵심 개념
| 개념 | 설명 |
| :--- | :--- |
| `createWebHistory` | `/#/movies` 같은 해시 없이 깔끔한 URL 사용 (HTML5 History API) |
| `name` | 경로 문자열 대신 이름으로 이동 → 경로가 바뀌어도 링크 코드 수정 불필요 |
| `:movieId` | **동적 세그먼트**. `/278` 에서 `278`이 `route.params.movieId`로 들어옴 |
| `(\\d+)` | 동적 세그먼트에 **정규식 제약**. 숫자만 매칭 |
| `meta` | 라우트에 붙이는 자유 형식 정보. 가드에서 `to.meta.usesMovieApi`로 읽음 (F9) |
| `scrollBehavior` | 페이지 이동 시 스크롤을 맨 위로 |

### 🐛 트러블슈팅: 동적 라우트 충돌
`/:movieId`만 쓰면 `/movies`도 "movieId = 'movies'"로 해석될 *수* 있습니다. Vue Router 4는 정적 경로에 우선순위를 주긴 하지만, `/abc`처럼 오타 URL도 상세 페이지로 가서 API 404를 부릅니다. `(\\d+)`로 **"숫자일 때만 상세 페이지"** 라고 명확히 해두면 의도가 코드에 드러납니다.
(JS 문자열 안이라 `\d`를 `\\d`로 이스케이프한 것에 주의!)

### 코드 — `src/App.vue` (요약)
```vue
<RouterLink class="nav-link" :to="{ name: 'home' }" exact-active-class="active">Home</RouterLink>
<RouterLink class="nav-link" :to="{ name: 'movies' }" active-class="active">Movies</RouterLink>
...
<!-- Django 모드일 때만 로그인/로그아웃 (F9) -->
<div v-if="MOVIE_API_SOURCE === 'django'" class="d-flex align-items-center gap-2 ms-auto">...</div>
...
<main class="container py-4">
  <RouterView />   <!-- 현재 URL에 매칭된 View가 여기에 그려짐 -->
</main>
```
- `RouterLink`는 `<a>` 태그를 만들지만 **페이지 새로고침 없이** 이동합니다 (SPA의 핵심).
- `active-class` vs `exact-active-class`: `/`는 모든 경로의 접두사라서 `active-class`를 쓰면 Home이 항상 활성화돼 보입니다. 그래서 Home에만 `exact-active-class`를 사용했습니다.

### ✍️ 직접 해보기
- `(\\d+)`를 지우고 `/hello`로 접속해 보세요. 무슨 일이 일어나나요?
- 존재하지 않는 경로를 위한 404 페이지 라우트(`/:pathMatch(.*)*`)를 추가해 보세요.

---

## F3. API 레이어 분리 — axios 인스턴스

### 🎯 목표
컴포넌트 안에 `axios.get('https://api.themoviedb.org/3/...?api_key=...')`를 매번 쓰지 않도록, **외부 API마다 파일 하나**를 만든다.

### 코드 — `src/api/tmdb.js`
```js
const TMDB_API_KEY = import.meta.env.VITE_TMDB_API_KEY
export const TMDB_IMAGE_URL = 'https://image.tmdb.org/t/p'

// v4 Read Access Token(JWT, "eyJ"로 시작)이면 Bearer 헤더, v3 API Key면 api_key 쿼리로 인증
const isBearerToken = TMDB_API_KEY?.startsWith('eyJ')

const tmdb = axios.create({
  baseURL: 'https://api.themoviedb.org/3',
  headers: isBearerToken ? { Authorization: `Bearer ${TMDB_API_KEY}` } : {},
  params: {
    language: 'ko-KR',
    ...(isBearerToken ? {} : { api_key: TMDB_API_KEY }),
  },
})

export async function fetchTopRated(page = 1) {
  const { data } = await tmdb.get('/movie/top_rated', { params: { page } })
  return data.results          // ← 뷰가 쓰기 좋은 형태(배열)로 가공해서 반환
}
```

### 핵심 개념
- **`axios.create()`**: 공통 설정(baseURL, 헤더, 기본 쿼리)을 가진 "전용 axios"를 만듭니다. 이후 `tmdb.get('/movie/top_rated')`처럼 경로만 쓰면 됩니다.
- 인스턴스의 `params`와 요청별 `params`는 **합쳐집니다**. 그래서 `language`, `api_key`는 매번 자동으로 붙습니다.
- **스프레드 + 삼항 연산자 패턴** `...(조건 ? {} : { key: value })` 은 "조건에 따라 속성을 넣거나 빼는" JS 관용구입니다.
- 함수가 `data.results`만 반환하므로 뷰는 TMDB 응답 구조(`{ page, results, total_pages }`)를 몰라도 됩니다.

### 🤔 왜 TMDB 인증을 두 방식 다 지원했나
TMDB는 v3 API Key(짧은 문자열)와 v4 Read Access Token(긴 JWT, `eyJ`로 시작) 두 가지를 발급합니다. JWT는 항상 base64 인코딩된 `{"` 로 시작하므로 `eyJ`가 됩니다. 이걸 이용해 어떤 키를 넣어도 동작하게 했습니다. (백엔드 `fetch_tmdb.py`도 같은 방식 — B3)

### `src/api/youtube.js`도 같은 패턴
```js
const youtube = axios.create({
  baseURL: 'https://www.googleapis.com/youtube/v3',
  params: { key: import.meta.env.VITE_YOUTUBE_API_KEY, part: 'snippet', type: 'video' },
})

export async function searchVideos(query, maxResults = 12) {
  const { data } = await youtube.get('/search', { params: { q: query, maxResults } })
  return data.items
}

export function getEmbedUrl(videoId) {
  return `https://www.youtube.com/embed/${videoId}?autoplay=1`
}
```
- `type: 'video'`를 넣어야 채널/재생목록이 검색 결과에 섞이지 않습니다 (재생목록은 `videoId`가 없어서 에러 원인이 됨).
- URL을 만드는 로직(`getEmbedUrl`)도 API 파일에 둬서 컴포넌트에는 문자열 조립이 없게 했습니다.

### ✍️ 직접 해보기
- 브라우저 개발자도구 **Network 탭**에서 실제 요청 URL을 열어 `language=ko-KR&api_key=...`가 자동으로 붙었는지 확인해 보세요.

---

## F4. 최고 평점 영화 목록

### 🎯 목표
`/movies` 진입 시 최고 평점 영화 목록을 받아와 카드 그리드로 보여준다.

### 데이터 흐름
```
MovieListView 마운트
  → onMounted 에서 getTopRatedMovies() 호출  (TMDB 또는 Django — F10)
  → movies.value = [...20편]
  → v-for 로 MovieCard 에 :movie="movie" (props) 전달
  → MovieCard 가 포스터/제목/평점/줄거리 렌더링
```

### 코드 — `src/views/MovieListView.vue`
```vue
<template>
  <div class="d-flex align-items-center justify-content-between mb-4">
    <h2 class="fw-bold mb-0">🏆 최고 평점 영화</h2>
    <span class="badge text-bg-secondary">source: {{ MOVIE_API_SOURCE }}</span>
  </div>

  <div v-if="isLoading" class="text-center py-5">
    <div class="spinner-border" role="status"></div>
  </div>
  <div v-else-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
  <div v-else class="row row-cols-2 row-cols-md-3 row-cols-lg-4 row-cols-xl-5 g-4">
    <div v-for="movie in movies" :key="movie.id" class="col">
      <MovieCard :movie="movie" />
    </div>
  </div>
</template>

<script setup>
const movies = ref([])
const isLoading = ref(true)
const errorMessage = ref('')

onMounted(async () => {
  try {
    movies.value = await getTopRatedMovies()
  } catch (error) {
    console.error(error)
    errorMessage.value = '영화 목록을 불러오지 못했습니다. API Key 또는 서버 상태를 확인해주세요.'
  } finally {
    isLoading.value = false
  }
})
</script>
```

### 핵심 개념 ① — 비동기 요청의 "3가지 상태" 패턴
이 프로젝트의 **모든 뷰**가 이 패턴을 씁니다. 한 번 익혀두면 계속 재사용할 수 있어요.

| 상태 | 변수 | 화면 |
| :--- | :--- | :--- |
| 로딩 중 | `isLoading = true` | 스피너 |
| 실패 | `errorMessage = '...'` | 빨간 알림 |
| 성공 | `movies = [...]` | 실제 콘텐츠 |

- `try / catch / finally`: `finally`는 성공·실패 **모두** 실행되므로 `isLoading = false`를 여기에 두면 빠뜨릴 일이 없습니다.
- 템플릿에서는 `v-if → v-else-if → v-else` 체인으로 **딱 하나만** 보이게 합니다.

### 핵심 개념 ② — `:key`
`v-for`에는 항상 고유한 `:key`를 줍니다. Vue가 리스트가 바뀔 때 어떤 DOM을 재사용할지 판단하는 기준입니다. 배열 인덱스 대신 `movie.id`처럼 **데이터 고유값**을 쓰세요.

### 코드 — `src/components/MovieCard.vue`
```vue
<template>
  <RouterLink :to="{ name: 'movieDetail', params: { movieId: movie.id } }" class="text-decoration-none text-reset">
    <div class="card h-100 border-0 shadow-sm hover-lift">
      <img :src="getPosterUrl(movie.poster_path)" class="card-img-top" :alt="movie.title" loading="lazy" />
      <div class="card-body">
        <h6 class="card-title fw-bold mb-0">{{ movie.title }}</h6>
        <span class="badge text-bg-warning">★ {{ movie.vote_average?.toFixed(1) }}</span>
        <p class="card-text small text-secondary text-clamp-3 mb-0">
          {{ movie.overview || '줄거리 정보가 없습니다.' }}
        </p>
      </div>
    </div>
  </RouterLink>
</template>

<script setup>
defineProps({
  movie: { type: Object, required: true },
})
</script>
```
- **props는 부모 → 자식 단방향**입니다. 카드는 받은 데이터를 그리기만 하고 수정하지 않습니다.
- 카드 전체를 `RouterLink`로 감싸서 어디를 클릭해도 상세 페이지로 이동합니다.
- `?.` (옵셔널 체이닝): `vote_average`가 없을 때 `toFixed` 호출로 앱이 터지는 것을 방지.
- `loading="lazy"`: 화면에 보일 때 이미지를 로드 → 첫 로딩 속도 개선.
- `getPosterUrl`은 TMDB가 `poster_path`로 `/abc.jpg`만 주기 때문에 `https://image.tmdb.org/t/p/w500/abc.jpg`로 조립하고, 포스터가 없으면 placeholder를 반환합니다. Django도 같은 `poster_path` 문자열을 저장하므로 두 모드에서 똑같이 동작합니다.

### ✍️ 직접 해보기
- `.env`의 TMDB 키를 일부러 틀리게 바꾸고 에러 메시지가 뜨는지 확인해 보세요.
- "더 보기" 버튼으로 2페이지를 이어 붙여 보세요. (`fetchTopRated(page)`는 이미 page 인자를 받습니다.)

---

## F5. 영화 상세 정보

### 🎯 목표
`/278` 같은 URL로 들어오면 해당 영화의 상세 정보를 보여준다.

### 코드 — `src/views/MovieDetailView.vue` (스크립트)
```js
const route = useRoute()    // 현재 URL 정보 (읽기용)
const router = useRouter()  // 이동 기능 (router.back(), router.push())

const movie = ref(null)
const isLoading = ref(true)
const errorMessage = ref('')
const isTrailerOpen = ref(false)

watch(
  () => route.params.movieId,
  async (movieId) => {
    if (!movieId) return
    isLoading.value = true
    errorMessage.value = ''
    isTrailerOpen.value = false
    try {
      movie.value = await getMovieDetail(movieId)
    } catch (error) {
      console.error(error)
      errorMessage.value = '영화 정보를 불러오지 못했습니다.'
    } finally {
      isLoading.value = false
    }
  },
  { immediate: true },
)
```

### 🐛 트러블슈팅: 왜 `onMounted`가 아니라 `watch`인가?
처음엔 목록처럼 `onMounted`로 요청했다고 해봅시다.

1. `/278` 진입 → `MovieDetailView` 생성 → `onMounted` 실행 ✅
2. 같은 페이지 안에서 `/238`로 이동 (예: 추천 영화 클릭, 브라우저 뒤로가기)
3. **같은 컴포넌트를 재사용**하므로 새로 만들어지지 않음 → `onMounted` 다시 실행 안 됨 ❌
4. URL은 `/238`인데 화면은 여전히 278번 영화

해결: URL 파라미터를 **감시(watch)** 합니다.
- `() => route.params.movieId` — 감시 대상을 **getter 함수**로 넘깁니다. (`route.params.movieId`를 바로 넘기면 그 순간의 문자열 값만 전달되어 반응성이 끊김)
- `{ immediate: true }` — 값이 바뀔 때뿐 아니라 **처음 한 번도 즉시 실행** → `onMounted` 역할까지 겸함.

### 코드 — `src/components/MovieDetailInfo.vue` (요약)
```vue
<span v-for="genre in movie.genres" :key="genre.name" class="badge rounded-pill text-bg-primary me-1">
  {{ genre.name }}
</span>
...
<slot />   <!-- 부모가 넣어준 내용(예고편 버튼)이 여기에 들어감 -->
```
- 장르의 `:key`로 `genre.id`가 아니라 `genre.name`을 씁니다. TMDB는 `[{id, name}]`을 주지만 Django 상세 API는 `[{name}]`만 주기 때문에(B4), **두 출처에 공통으로 있는 값**을 키로 골랐습니다.

그리고 부모(`MovieDetailView`)에서:
```vue
<MovieDetailInfo v-else :movie="movie">
  <button class="btn btn-danger btn-lg mt-2" @click="isTrailerOpen = true">▶ 공식 예고편</button>
</MovieDetailInfo>
```

### 핵심 개념 — `slot`
`MovieDetailInfo`는 "정보 표시"만 책임지고, 예고편 버튼은 **부모가 주입**합니다. 덕분에:
- 정보 컴포넌트는 예고편 모달의 존재를 몰라도 됨
- 버튼 클릭 상태(`isTrailerOpen`)는 부모가 관리 → 모달도 부모가 띄움

props가 "데이터"를 내려준다면, slot은 "마크업(화면 조각)"을 내려준다고 생각하면 됩니다.

### ✍️ 직접 해보기
- `watch`를 `onMounted`로 바꾸고, 주소창에서 숫자만 바꿔 이동했을 때(혹은 추천 카드에서 이동 후 뒤로가기) 버그를 재현해 보세요.

---

## F6. 공통 모달 만들기

### 🎯 목표
예고편과 리뷰 영상 둘 다 "영상 모달"이 필요하다. **겉 틀(`VideoModalFrame`)은 하나만** 만들고 내용만 바꿔 끼운다.

### 코드 — `src/components/VideoModalFrame.vue`
```vue
<template>
  <Teleport to="body">
    <div class="modal d-block" tabindex="-1" @click.self="emit('close')">
      <div class="modal-dialog modal-xl modal-dialog-centered">
        <div class="modal-content bg-dark text-white">
          <div class="modal-header border-secondary">
            <h5 class="modal-title text-truncate">{{ title }}</h5>
            <button type="button" class="btn-close btn-close-white" @click="emit('close')"></button>
          </div>
          <div class="modal-body p-0">
            <slot />
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop show"></div>
  </Teleport>
</template>

<script setup>
defineProps({ title: { type: String, default: '' } })
const emit = defineEmits(['close'])

const onKeydown = (event) => {
  if (event.key === 'Escape') emit('close')
}

onMounted(() => {
  document.body.classList.add('modal-open')        // 배경 스크롤 막기
  window.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  document.body.classList.remove('modal-open')
  window.removeEventListener('keydown', onKeydown) // 꼭 정리!
})
</script>
```

### 핵심 개념 4가지

**① `Teleport to="body"`**
모달을 컴포넌트 트리 위치가 아니라 `<body>` 바로 아래에 렌더링합니다. 부모에 `overflow: hidden`이나 `z-index`, `transform`이 있으면 모달이 잘리거나 뒤로 숨는 문제가 생기는데, 이를 원천 차단합니다.

**② `emit` — 자식 → 부모 통신**
모달은 스스로 사라질 수 없습니다(자신을 보여줄지 말지는 부모의 `v-if`가 결정). 그래서 "닫아줘"라는 **이벤트만 올려보내고**, 부모가 상태를 바꿉니다.
```
props  : 부모 ──데이터──▶ 자식
emit   : 부모 ◀──이벤트── 자식
```

**③ `@click.self`**
이벤트 수식어 `.self`는 "클릭된 요소가 **바로 그 요소 자신**일 때만" 실행합니다. 어두운 배경 클릭 → 닫힘, 영상(자식 요소) 클릭 → 안 닫힘.

**④ 이벤트 리스너는 반드시 정리**
`window`에 붙인 리스너는 컴포넌트가 사라져도 남습니다. `onUnmounted`에서 `removeEventListener`를 안 하면 모달을 열 때마다 리스너가 쌓이는 **메모리 누수**가 생깁니다. 그래서 익명 함수가 아닌 `onKeydown` 변수로 같은 함수 참조를 넘겨야 합니다.

### 🐛 트러블슈팅: 모달을 닫아도 소리가 계속 난다
Bootstrap 모달처럼 CSS(`display: none`)로 숨기면 iframe은 **살아있어서** 유튜브가 계속 재생됩니다.
→ 부모에서 모달을 **`v-if`** 로 렌더링해서, 닫으면 iframe이 DOM에서 아예 제거되도록 했습니다. (`v-show`였다면 같은 문제가 발생합니다.)
→ 부수 효과로, 열 때마다 컴포넌트가 새로 생성되므로 `onMounted`/`onUnmounted`가 정확히 열기/닫기 타이밍에 맞춰 실행됩니다.

### ✍️ 직접 해보기
- 부모의 `v-if`를 `v-show`로 바꿔서 소리 버그를 재현해 보세요.
- `onUnmounted`의 `removeEventListener`를 지우고, 모달을 3번 열고 닫은 뒤 ESC를 눌렀을 때 `close`가 몇 번 emit되는지 Vue DevTools로 확인해 보세요.

---

## F7. 공식 예고편 모달

### 🎯 목표
상세 페이지에서 **[공식 예고편]** 버튼을 누르면 `"영화제목 trailer"`로 유튜브를 검색하고 첫 번째 영상을 모달에서 재생한다.

### 코드 — 부모 (`MovieDetailView.vue`)
```vue
<YoutubeTrailerModal
  v-if="isTrailerOpen"
  :movie-title="movie.original_title || movie.title"
  @close="isTrailerOpen = false"
/>
```

### 코드 — `src/components/YoutubeTrailerModal.vue`
```vue
<template>
  <VideoModalFrame :title="`${movieTitle} 공식 예고편`" @close="emit('close')">
    <div v-if="isLoading" class="text-center py-5"><div class="spinner-border text-light"></div></div>
    <p v-else-if="errorMessage" class="p-4 mb-0 text-warning">{{ errorMessage }}</p>
    <div v-else class="ratio ratio-16x9">
      <iframe :src="getEmbedUrl(videoId)" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>
    </div>
  </VideoModalFrame>
</template>

<script setup>
const props = defineProps({ movieTitle: { type: String, required: true } })
const emit = defineEmits(['close'])

const videoId = ref(null)
const isLoading = ref(true)
const errorMessage = ref('')

onMounted(async () => {
  try {
    const [firstVideo] = await searchVideos(`${props.movieTitle} trailer`, 1)
    if (!firstVideo) {
      errorMessage.value = '예고편을 찾을 수 없습니다.'
      return
    }
    videoId.value = firstVideo.id.videoId
  } catch (error) {
    errorMessage.value = '예고편을 불러오지 못했습니다. Youtube API Key를 확인해주세요.'
  } finally {
    isLoading.value = false
  }
})
</script>
```

### 🤔 왜 이렇게 했나
- **`original_title` 우선 사용**: TMDB 모드는 `language=ko-KR` 때문에 `title`이 한국어("쇼생크 탈출")입니다. 공식 예고편은 원제("The Shawshank Redemption trailer")로 검색해야 훨씬 정확합니다. Django 모드에는 `original_title`이 없지만 `title`이 CSV의 영어 제목이라 그대로 씁니다.
- **`maxResults = 1`**: 첫 번째 결과만 쓰므로 1개만 요청 → Youtube API 할당량 절약 (search는 요청당 100 unit 소모, 하루 10,000 unit 제한).
- **배열 구조 분해** `const [firstVideo] = ...` 로 첫 원소만 꺼냅니다. 결과가 빈 배열이면 `undefined` → "찾을 수 없음" 처리.
- **`onMounted`에서 요청해도 되는 이유**: 부모의 `v-if` 덕분에 모달을 열 때마다 새로 생성되기 때문 (F6의 부수 효과).
- **컴포넌트가 직접 API를 부르는 예외**: 모달은 열릴 때만 데이터가 필요하고 다른 곳에서 결과를 공유하지 않으므로, 부모가 미리 요청하는 것보다 응집도가 높습니다.
- **`ratio ratio-16x9`**: Bootstrap 유틸리티로 iframe을 16:9 비율로 반응형 유지.
- **props 이름 표기법**: 템플릿에서는 `:movie-title`, 스크립트에서는 `movieTitle` — Vue가 자동 변환합니다.

---

## F8. 리뷰 영상 검색

### 🎯 목표
검색어를 입력하면 `"검색어 review"`로 유튜브를 검색해 카드 목록을 보여주고, 카드를 누르면 모달로 재생한다.

### 컴포넌트 관계
```
ReviewSearchView  (상태: keyword, videos, selectedVideo)
 ├─ YoutubeCard × N        ── emit('select', video) ──▶ selectedVideo = video
 └─ YoutubeReviewModal     (v-if="selectedVideo")  ── emit('close') ──▶ selectedVideo = null
      └─ VideoModalFrame   (F6의 공통 틀 재사용)
```

### 코드 — `src/views/ReviewSearchView.vue` (핵심)
```vue
<form class="input-group input-group-lg mb-4 shadow-sm" @submit.prevent="onSearch">
  <input v-model.trim="keyword" type="text" class="form-control" placeholder="영화 제목을 입력하세요" />
  <button class="btn btn-dark" type="submit" :disabled="!keyword || isLoading">검색</button>
</form>
...
<p v-else-if="!searchedKeyword">영화 제목을 검색하면 Youtube 리뷰 영상을 찾아드려요.</p>
<p v-else-if="!videos.length">"{{ searchedKeyword }}" 에 대한 리뷰 영상이 없습니다.</p>
<template v-else>
  <div v-for="video in videos" :key="video.id.videoId" class="col">
    <YoutubeCard :video="video" @select="selectedVideo = $event" />
  </div>
</template>

<YoutubeReviewModal v-if="selectedVideo" :video="selectedVideo" @close="selectedVideo = null" />
```
```js
const keyword = ref('')          // 입력창과 양방향 바인딩 (타이핑할 때마다 변함)
const searchedKeyword = ref('')  // 실제로 검색을 실행한 단어 (검색 버튼 누를 때만 변함)

const onSearch = async () => {
  if (!keyword.value) return
  isLoading.value = true
  errorMessage.value = ''
  try {
    videos.value = await searchVideos(`${keyword.value} review`)
    searchedKeyword.value = keyword.value
  } catch (error) { ... } finally { isLoading.value = false }
}
```

### 핵심 개념
| 문법 | 의미 |
| :--- | :--- |
| `<form @submit.prevent>` | 버튼 클릭과 **Enter 키** 둘 다 처리 + 페이지 새로고침(기본 동작) 방지 |
| `v-model.trim` | 입력값 앞뒤 공백 자동 제거 → `"   "`만 입력하면 빈 문자열 → 버튼 비활성화 |
| `:disabled="!keyword \|\| isLoading"` | 빈 검색, 중복 클릭 방지 |
| `$event` | 템플릿 인라인 핸들러에서 emit이 보낸 값 (여기선 `video`) |

### 🤔 왜 `keyword`와 `searchedKeyword`를 나눴나
하나만 쓰면, "어벤져스" 검색 후 입력창에 "타이타닉"을 **타이핑만 해도** 결과 위 문구가 `"타이타닉 review 검색 결과"`로 바뀝니다. 입력 중인 값과 확정된 값은 **다른 상태**입니다. 또 `searchedKeyword`가 비어있는지로 "아직 검색 전" / "검색했는데 결과 0개"를 구분할 수 있습니다 — 빈 화면도 상황별로 다르게 안내하는 것이 좋은 UX입니다.

### 🐛 트러블슈팅: 제목에 `&#39;`, `&quot;`가 보인다
Youtube API의 `snippet.title`은 `Marvel&#39;s Avengers`처럼 **HTML 엔티티로 인코딩**되어 옵니다.

- ❌ `v-html="title"` — 동작은 하지만, 제목에 `<img onerror=...>` 같은 스크립트가 섞여 있으면 그대로 실행됩니다 (**XSS 취약점**).
- ✅ `utils/decodeHtml.js`:
  ```js
  export function decodeHtml(text = '') {
    return new DOMParser().parseFromString(text, 'text/html').documentElement.textContent
  }
  ```
  `DOMParser`는 문자열을 **실행하지 않고** 파싱만 합니다. 거기서 `textContent`(순수 텍스트)만 꺼내 `{{ }}`로 출력하면 안전합니다.

### `YoutubeCard.vue`의 `computed`
```js
const props = defineProps({ video: { type: Object, required: true } })
const emit = defineEmits(['select'])

const snippet = computed(() => props.video.snippet)
const title = computed(() => decodeHtml(snippet.value.title))
```
- 템플릿에서 `video.snippet.thumbnails...`처럼 길게 쓰지 않도록 `computed`로 별칭을 만들었습니다.
- `computed`는 **캐싱**됩니다. 의존 값이 안 바뀌면 `decodeHtml`을 다시 실행하지 않습니다.
- 썸네일은 `thumbnails.high?.url ?? thumbnails.default.url` — 고화질이 없으면 기본 화질로 대체(`??` 널 병합 연산자).

### ✍️ 직접 해보기
- `decodeHtml`을 빼고 `"I'm"`이 들어간 영화를 검색해 보세요.
- 검색 결과에 "다음 페이지" 기능을 추가해 보세요. (힌트: 응답의 `nextPageToken`을 `pageToken` 파라미터로 전달)

---

## F9. 로그인과 토큰 관리

### 🎯 목표
Django API는 모든 요청에 토큰을 요구합니다(B6). 프론트에서 회원가입·로그인으로 토큰을 받아 보관하고, Django로 가는 요청마다 자동으로 붙인다. 로그인하지 않은 사용자는 영화 페이지 대신 로그인 페이지로 보낸다.

### 전체 흐름
```
LoginView ─ auth.login() ─▶ api/accounts.js ─ POST /accounts/login/ ─▶ {"key": "..."}
                                │
                                ▼
                    stores/auth.js : token, username 저장 (+ localStorage)
                                │
      ┌─────────────────────────┼──────────────────────────┐
      ▼                         ▼                          ▼
 router 가드              api/django.js 요청 인터셉터       App.vue 네비게이션 바
 (로그인 여부 검사)       (Authorization 헤더 첨부)         (사용자명·로그아웃 버튼)
```

### 9-1. 토큰 보관소 — `src/stores/auth.js`
```js
const TOKEN_KEY = 'movieflix-token'
const USERNAME_KEY = 'movieflix-username'

// 사파리 사생활 보호 모드 등에서는 localStorage 접근이 예외를 던질 수 있음
function readStorage(key) {
  try {
    return localStorage.getItem(key)
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(readStorage(TOKEN_KEY))
  const username = ref(readStorage(USERNAME_KEY))
  const isLoggedIn = computed(() => Boolean(token.value))

  const setSession = (newToken, newUsername) => {
    token.value = newToken
    username.value = newUsername
    writeStorage(TOKEN_KEY, newToken)
    writeStorage(USERNAME_KEY, newUsername)
  }

  const login = async (credentials) => {
    const key = await accounts.login(credentials)
    setSession(key, credentials.username)
  }

  const signup = async (payload) => {
    const key = await accounts.signup(payload)
    setSession(key, payload.username)
  }

  const logout = () => setSession(null, null)

  return { token, username, isLoggedIn, login, signup, logout }
})
```
- **왜 Pinia인가?** 토큰은 네비게이션 바, 라우터 가드, API 인터셉터, 로그인 화면이 **모두** 써야 합니다. props로 내려주기엔 거리가 멀고, 컴포넌트가 아닌 곳(라우터, api 모듈)에서도 읽어야 하므로 전역 store가 맞습니다.
- **Setup Store 문법**: `defineStore('auth', () => { ... })` 안에서 `ref`는 state, `computed`는 getter, 함수는 action이 됩니다. 컴포넌트의 `<script setup>`과 같은 방식으로 쓸 수 있습니다.
- **localStorage에 같이 저장**: Pinia 상태는 새로고침하면 사라집니다. 토큰을 localStorage에도 저장하고 store를 만들 때 읽어 와서, 새로고침해도 로그인이 유지됩니다.
- **try/catch로 감싼 이유**: 브라우저 설정에 따라 localStorage 접근 자체가 예외를 던질 수 있습니다. 그래도 앱이 멈추지 않고 메모리의 토큰으로 계속 동작하게 했습니다.
- ⚠️ localStorage는 같은 출처의 JS가 모두 읽을 수 있어서, XSS가 생기면 토큰이 탈취될 수 있습니다. 그래서 F8의 `v-html` 회피 같은 XSS 방어가 더 중요해집니다. 실서비스에서는 HttpOnly 쿠키 방식도 고려합니다.

### 9-2. 인증 API — `src/api/accounts.js`
```js
// dj-rest-auth 엔드포인트는 /api/v1 이 아닌 서버 루트의 /accounts/ 아래에 있음
const accounts = axios.create({
  baseURL: DJANGO_API_URL.replace(/\/api\/v1\/?$/, '') + '/accounts',
})

export async function login({ username, password }) {
  const { data } = await accounts.post('/login/', { username, password })
  return data.key
}

// DRF 검증 오류 응답({ field: ['메시지'] })을 한 줄 메시지로
export function formatAuthError(error) {
  const data = error.response?.data
  if (!data || typeof data !== 'object') return '서버에 연결하지 못했습니다. Django 서버가 실행 중인지 확인해주세요.'
  return Object.values(data).flat().join(' ')
}
```
- 환경 변수는 `VITE_DJANGO_API_URL=http://127.0.0.1:8000/api/v1` 하나만 두고, 정규식으로 끝의 `/api/v1`을 떼어 서버 루트를 구합니다. 설정값을 두 개로 늘리지 않기 위해서입니다.
- **오류 메시지 가공**: DRF는 `{"password1": ["비밀번호가 너무 짧습니다."], "username": ["이미 존재하는 아이디입니다."]}`처럼 필드별 배열로 오류를 줍니다. `Object.values(...).flat()`으로 펼쳐 한 줄로 보여줍니다. 응답 자체가 없으면(서버 꺼짐) 서버 상태를 안내합니다.

### 9-3. 토큰 자동 첨부 — `src/api/django.js`의 인터셉터
```js
// 서버의 모든 API 가 토큰 인증을 요구하므로 로그인 시 발급받은 토큰을 헤더에 싣는다
// (store 를 지연 import 해서 stores/auth.js ↔ api 모듈 간 순환 참조를 피함)
django.interceptors.request.use(async (config) => {
  const { useAuthStore } = await import('@/stores/auth')
  const auth = useAuthStore()
  if (auth.token) config.headers.Authorization = `Token ${auth.token}`
  return config
})

// 토큰이 없거나 만료되면 로그아웃 후 로그인 페이지로
django.interceptors.response.use(undefined, async (error) => {
  if (error.response?.status === 401) {
    const [{ useAuthStore }, { default: router }] = await Promise.all([
      import('@/stores/auth'),
      import('@/router'),
    ])
    useAuthStore().logout()
    router.push({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } })
  }
  return Promise.reject(error)
})
```
- **인터셉터**: 모든 요청이 나가기 직전 / 모든 응답이 도착한 직후에 끼어드는 함수입니다. 각 API 함수(`fetchTopRated` 등)가 토큰을 신경 쓰지 않아도 됩니다.
- **헤더 형식**: DRF `TokenAuthentication`은 `Bearer`가 아니라 **`Token <key>`** 형식을 씁니다. (TMDB v4의 `Bearer`와 헷갈리기 쉬움)
- **응답 인터셉터의 두 인자**: `use(성공 처리, 실패 처리)`. 성공은 그대로 통과시키려고 `undefined`를 넘겼습니다. 실패 처리에서 `Promise.reject(error)`를 다시 던져야 뷰의 `catch`가 에러 메시지를 띄울 수 있습니다.
- **왜 동적 `import()`인가?** `stores/auth.js` → `api/accounts.js` → `api/django.js`로 import가 이어지는데, `django.js`가 다시 store와 router를 정적으로 import하면 **순환 참조**가 됩니다. 모듈 로딩 순서에 따라 값이 `undefined`가 될 수 있어서, 실제로 필요한 시점(요청할 때)에 불러오도록 했습니다. (`npm run build` 시 "dynamic import will not move module into another chunk" 경고가 나오는데, 코드 분할이 목적이 아니라서 무시해도 됩니다.)

### 9-4. 라우터 가드 — `src/router/index.js`
```js
// Django API 는 토큰 인증이 필요하므로, Django 출처일 때 비로그인 사용자는 로그인 페이지로
router.beforeEach((to) => {
  if (MOVIE_API_SOURCE !== 'django' || !to.meta.usesMovieApi) return
  if (!useAuthStore().isLoggedIn) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
})
```
- **`beforeEach`**: 모든 페이지 이동 직전에 실행됩니다. 아무것도 반환하지 않으면 통과, 다른 위치를 반환하면 그곳으로 보냅니다.
- **`meta.usesMovieApi`**: 어떤 페이지가 로그인을 요구하는지를 라우트 정의에 표시해 두고, 가드는 그 표시만 봅니다. 새 페이지를 추가할 때 `meta`만 붙이면 됩니다.
- **TMDB 모드에서는 가드가 아무것도 하지 않습니다.** 로그인은 Django 데이터를 쓸 때만 필요하기 때문입니다.
- **`redirect` 쿼리**: `/278`에 들어가려다 로그인 페이지로 왔다면 `/login?redirect=/278`이 됩니다. 로그인 후 원래 가려던 페이지로 돌려보낼 수 있습니다.
- 가드가 있는데 응답 인터셉터의 401 처리도 필요한 이유: 가드는 "토큰이 있는지"만 알고, 그 토큰이 **서버에서 유효한지**는 모릅니다. (DB를 새로 만들었거나 토큰이 삭제된 경우)

### 9-5. 로그인 화면 — `src/views/LoginView.vue` (스크립트)
```js
const onSubmit = async () => {
  isSubmitting.value = true
  errorMessage.value = ''
  try {
    await auth.login({ username: username.value, password: password.value })
    router.replace(route.query.redirect || { name: 'movies' })
  } catch (error) {
    console.error(error)
    errorMessage.value = formatAuthError(error)
  } finally {
    isSubmitting.value = false
  }
}
```
- **`router.replace`**: `push`와 달리 방문 기록에 로그인 페이지를 남기지 않습니다. 로그인 후 뒤로가기를 눌렀을 때 다시 로그인 화면이 나오지 않습니다.
- `SignupView`는 같은 구조에 비밀번호 확인 필드가 하나 더 있고, **서버에 보내기 전에** 두 비밀번호가 같은지 먼저 확인합니다. dj-rest-auth는 가입 성공 시 바로 토큰을 주므로 가입 즉시 로그인 상태가 됩니다.
- 입력 필드의 `autocomplete="username"`, `"current-password"`, `"new-password"`는 브라우저 비밀번호 관리자가 올바르게 동작하도록 돕는 표준 속성입니다.

### ✍️ 직접 해보기
- 로그인 후 개발자도구 **Application → Local Storage**에서 `movieflix-token`을 확인하고, Network 탭에서 요청 헤더에 `Authorization: Token ...`이 붙었는지 보세요.
- 로그인한 상태에서 Django의 `db.sqlite3`를 지우고 다시 만든 뒤 영화 목록에 들어가 보세요. 401 → 자동 로그아웃 → 로그인 페이지 이동이 일어나는지 확인해 보세요.

---

## F10. 데이터 출처 전환하기

### 🎯 목표
뷰/컴포넌트 코드를 **한 줄도 바꾸지 않고**, `.env` 값 하나로 TMDB ↔ Django를 전환한다.

### 코드 — `src/api/django.js` (데이터 함수)
```js
export const DJANGO_API_URL = import.meta.env.VITE_DJANGO_API_URL || 'http://127.0.0.1:8000/api/v1'

const django = axios.create({
  baseURL: DJANGO_API_URL,
})
// (인터셉터는 F9 참고)

export async function fetchTopRated() {
  const { data } = await django.get('/movies/')
  return data
}

export async function fetchMovieDetail(movieId) {
  const { data } = await django.get(`/movies/${movieId}/`)   // Django는 끝 슬래시 필수!
  return data
}

export async function fetchRandomMovieByGenre(genreId) {
  try {
    const { data } = await django.get('/movies/recommend/', { params: { genre: genreId } })
    return data
  } catch (error) {
    // 해당 장르의 영화가 없으면 404 → 추천 없음으로 처리
    if (error.response?.status === 404) return null
    throw error
  }
}
```

### 코드 — `src/api/movies.js` (전환 레이어)
```js
import * as tmdb from './tmdb'
import * as django from './django'

export const MOVIE_API_SOURCE = import.meta.env.VITE_MOVIE_API_SOURCE === 'django' ? 'django' : 'tmdb'
const useDjango = MOVIE_API_SOURCE === 'django'

export function getTopRatedMovies() {
  return useDjango ? django.fetchTopRated() : tmdb.fetchTopRated()
}

export function getMovieDetail(movieId) {
  return useDjango ? django.fetchMovieDetail(movieId) : tmdb.fetchMovieDetail(movieId)
}
```

### 🤔 이 구조가 작동하는 이유 (중요!)
```
          뷰는 이것만 앎                 출처별 구현
MovieListView ──▶ getTopRatedMovies() ─┬─▶ tmdb.fetchTopRated()   → [{id, title, poster_path, vote_average, overview, ...}]
                                       └─▶ django.fetchTopRated() → [{id, title, poster_path, vote_average, overview, ...}]
                                                                       ↑ 반환 모양이 같다!
```
두 함수가 **같은 이름의 함수**를 export하고 **같은 모양의 데이터**를 반환하기 때문에, 뷰 입장에서는 어디서 왔는지 구분할 수 없습니다. 이것이 가능했던 결정들:
1. `tmdb.js`가 `data.results`를 꺼내서 배열로 반환 (Django도 배열로 반환)
2. Django 모델·Serializer의 필드명을 TMDB와 동일하게 (`poster_path`, `vote_average`, `overview`) — B2, B4
3. Django가 영화 ID로 TMDB ID를 그대로 사용 — B2
4. 상세의 장르 키를 두 출처에 공통인 `genre.name`으로 — F5

이런 패턴을 **어댑터(Adapter) / 리포지토리(Repository) 패턴**이라고 부릅니다. "인터페이스(약속)를 맞추면 구현을 갈아끼울 수 있다"는 것이 핵심입니다.

### 사용법
```env
VITE_MOVIE_API_SOURCE=django
```
- `.env`를 바꾼 뒤에는 **`npm run dev`를 재시작**해야 반영됩니다.
- 목록 화면 우측 상단 뱃지(`source: django`)로 현재 출처를 확인할 수 있습니다.
- 포스터 이미지는 Django 모드에서도 TMDB 이미지 서버를 씁니다. DB에는 `poster_path`(경로)만 저장했기 때문입니다.
- Django 모드의 영화 제목은 CSV의 영어 제목, 줄거리는 TMDB에서 수집한 한국어입니다.

### ✍️ 직접 해보기
- Django 서버를 끈 상태로 `source=django`로 접속해 에러 메시지를 확인하고, Network 탭에서 실패 원인을 보세요.
- `CORS_ALLOWED_ORIGINS`를 주석 처리하고 콘솔에 뜨는 CORS 에러 메시지를 읽어 보세요.

---

## F11. 날씨 기반 영화 추천

### 🎯 목표
서울의 현재 날씨(WMO 코드)를 가져와 → 어울리는 장르로 매핑하고 → 그 장르에서 영화 1편을 랜덤 추천한다.

### 흐름
```
RecommendedView onMounted
  ① fetchSeoulWeather()        → { temperature: 21.3, weathercode: 61, ... }
  ② matchWeatherGenre(61)      → { label: '비', icon: '🌧️', genre: { id: 27, name: '공포' } }
  ③ getRandomMovieByGenre(27)  → 영화 1편 (TMDB: 클라이언트가 고름 / Django: 서버가 고름 — B8)
  ④ MovieCard 로 표시 (목록 컴포넌트 재사용!)
```

### 코드 — `src/api/weather.js`
```js
const SEOUL = { latitude: 37.5665, longitude: 126.978 }

export async function fetchSeoulWeather() {
  const { data } = await axios.get('https://api.open-meteo.com/v1/forecast', {
    params: { ...SEOUL, current_weather: true, timezone: 'Asia/Seoul' },
  })
  return data.current_weather
}

const WEATHER_GENRE_RULES = [
  { codes: [0], label: '맑음', icon: '☀️', genre: { id: 12, name: '모험' } },
  { codes: [1, 2, 3], label: '구름 조금/흐림', icon: '⛅', genre: { id: 35, name: '코미디' } },
  { codes: [45, 48], label: '안개', icon: '🌫️', genre: { id: 9648, name: '미스터리' } },
  { codes: [51, 53, 55, 56, 57], label: '이슬비', icon: '🌦️', genre: { id: 18, name: '드라마' } },
  { codes: [61, 63, 65, 66, 67, 80, 81, 82], label: '비', icon: '🌧️', genre: { id: 27, name: '공포' } },
  { codes: [71, 73, 75, 77, 85, 86], label: '눈', icon: '❄️', genre: { id: 10749, name: '로맨스' } },
  { codes: [95, 96, 99], label: '뇌우', icon: '⛈️', genre: { id: 53, name: '스릴러' } },
]
const DEFAULT_RULE = { label: '알 수 없음', icon: '🌈', genre: { id: 16, name: '애니메이션' } }

export function matchWeatherGenre(weatherCode) {
  return WEATHER_GENRE_RULES.find((rule) => rule.codes.includes(weatherCode)) ?? DEFAULT_RULE
}
```

### 🤔 왜 이렇게 했나
- **`if / else if` 대신 규칙 배열(데이터)**: 매핑을 코드 로직이 아니라 **데이터 테이블**로 표현했습니다. 규칙 추가/수정이 한 줄이면 되고, 한눈에 읽힙니다. `find`가 첫 번째로 맞는 규칙을 반환합니다.
- **`DEFAULT_RULE`**: 표에 없는 코드가 와도 화면이 깨지지 않도록 항상 기본값을 둡니다 (`??`).
- `matchWeatherGenre`는 **순수 함수**(같은 입력 → 항상 같은 출력, 외부 상태 변경 없음)라 테스트하기 쉽습니다.
- 장르 ID가 TMDB 장르 ID이고 Django도 같은 ID를 PK로 쓰므로(B2), 이 표 하나로 두 모드를 모두 지원합니다. Django 데이터 20편 안에 표의 모든 장르가 최소 1편씩 들어 있는지도 확인했습니다.
- Open-Meteo는 API Key가 필요 없어 `.env`에 아무것도 추가하지 않아도 됩니다.

### 랜덤 추천 — 출처별 구현 (`api/movies.js`)
```js
export async function getRandomMovieByGenre(genreId) {
  // Django 서버는 ORM Count 집계로 직접 랜덤 1편을 골라서 응답
  if (useDjango) return django.fetchRandomMovieByGenre(genreId)

  const movies = await tmdb.fetchMoviesByGenre(genreId)            // 클라이언트가 고름
  if (!movies.length) return null
  return movies[Math.floor(Math.random() * movies.length)]
}
```
- TMDB 모드: `/discover/movie?with_genres=27&vote_count.gte=1000`로 평점 높은 장르 영화 20편을 받고, 랜덤 페이지(1~3) + 랜덤 인덱스로 고릅니다. `vote_count.gte`는 투표 수 적은 무명 영화가 평점 10점으로 상위에 오는 것을 막습니다.
- Django 모드: 서버의 `/movies/recommend/`가 골라 줍니다 (B8). 404는 `null`로 바꿔서 TMDB 모드의 "결과 없음"과 **같은 형태**로 맞췄습니다.
- `Math.floor(Math.random() * n)` → `0 ~ n-1` 범위의 정수. 배열 랜덤 선택의 기본 공식입니다. (파이썬의 `random.randrange(n)`과 같은 역할)

### 코드 — `src/views/RecommendedView.vue` (스크립트)
```js
const pickMovie = async () => {
  isPicking.value = true
  try {
    movie.value = await getRandomMovieByGenre(rule.value.genre.id)
  } catch (error) {
    movie.value = null
  } finally {
    isPicking.value = false
  }
}

onMounted(async () => {
  try {
    weather.value = await fetchSeoulWeather()
    rule.value = matchWeatherGenre(weather.value.weathercode)
  } catch (error) {
    errorMessage.value = '날씨 정보를 불러오지 못했습니다.'
    return                         // 날씨 실패 시 추천 단계로 진행하지 않음
  } finally {
    isLoading.value = false        // return 해도 finally 는 실행됨!
  }
  await pickMovie()
})
```
- **로딩 상태를 2개로 분리**: `isLoading`(날씨, 페이지 전체)와 `isPicking`(영화만). "🎲 다른 영화 추천"을 누를 때 날씨 카드는 그대로 두고 영화 영역만 스피너가 돕니다.
- `pickMovie`를 함수로 분리해서 **최초 추천**과 **다시 추천 버튼**이 같은 코드를 씁니다.
- `catch`에서 `return`해도 `finally`는 실행된다는 JS 동작을 활용했습니다.

### ✍️ 직접 해보기
- `matchWeatherGenre(weather.value.weathercode)`를 `matchWeatherGenre(71)`로 바꿔 눈 오는 날을 시뮬레이션해 보세요.
- 기온(`temperature`)도 반영해서 30도 이상이면 다른 장르를 추천하도록 규칙을 확장해 보세요.

---

## F12. 스타일링과 마무리 점검

### `src/assets/main.css` — 재사용 유틸리티 클래스
```css
.text-clamp-3 {                 /* 줄거리를 3줄까지만 보여주고 … 처리 */
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.hover-lift { transition: transform 0.15s ease, box-shadow 0.15s ease; }
.hover-lift:hover {             /* 카드에 마우스를 올리면 살짝 떠오름 */
  transform: translateY(-4px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}
```
- 줄거리 길이가 제각각이라 카드 높이가 들쭉날쭉한 문제 → `text-clamp-3` + 카드의 `h-100`으로 정렬.
- Bootstrap 그리드 `row-cols-2 row-cols-md-3 row-cols-lg-4 row-cols-xl-5`: 화면 너비에 따라 한 줄 카드 수가 2 → 5개로 변하는 **반응형 레이아웃**.
- `!important`는 Bootstrap의 `shadow-sm` 클래스(역시 `!important`)를 덮어쓰기 위해서만 사용.
- 로그인·회원가입 폼은 Bootstrap `card`와 `form-control`만으로 구성하고, `col-sm-10 col-md-6 col-lg-4`로 화면이 넓어질수록 폼 폭을 좁혀 가운데 정렬했습니다.

### 마무리 점검 목록
- [x] `.env`, `node_modules`, `dist`, `venv`, `db.sqlite3`가 `.gitignore`에 포함 (`git check-ignore -v <파일>`로 확인 가능)
- [x] `.env.example` 커밋 → 필요한 환경 변수 목록 공유
- [x] 마이그레이션 파일(`*/migrations/0001_initial.py`) 커밋
- [x] `python manage.py test movies` 통과 (16개)
- [x] `npm run build` 성공
- [x] TMDB 모드와 Django 모드 모두 화면 확인

---

# Part 3. 통합

## I1. 전체 실행 순서

### 처음 한 번 (저장소를 clone한 직후)
```bash
# 1) 백엔드
cd django-pjt
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt
python problem/problem_a.py                       # CSV → fixture (TMDB 키 불필요)
python manage.py migrate
python manage.py loaddata users.json genres.json movies.json casts.json reviews.json
python manage.py test movies                      # 16개 통과 확인

# 2) 프론트엔드
cd ../my-vue-pjt
npm install
cp .env.example .env                              # TMDB / YouTube 키 입력, VITE_MOVIE_API_SOURCE 선택
```

### 매번 실행할 때 (터미널 두 개)
```bash
# 터미널 1 — 백엔드 (http://127.0.0.1:8000)
cd django-pjt && source venv/Scripts/activate && python manage.py runserver

# 터미널 2 — 프론트엔드 (http://localhost:5173)
cd my-vue-pjt && npm run dev
```
- TMDB 모드(`VITE_MOVIE_API_SOURCE=tmdb`)라면 백엔드 없이 프론트만 실행해도 됩니다.
- Vite 개발 서버는 반드시 **5173 포트**로 띄워야 합니다. 다른 포트면 CORS 허용 목록(B9)에 없어 요청이 막힙니다.

## I2. 연동 확인 시나리오

Django 모드(`VITE_MOVIE_API_SOURCE=django`)에서 아래 순서대로 확인합니다.

| 순서 | 할 일 | 기대 결과 | 관련 단계 |
| :--- | :--- | :--- | :--- |
| 1 | 로그인 없이 Movies 클릭 | `/login?redirect=/movies`로 이동 | F9 가드 |
| 2 | 회원가입 (짧은 비밀번호로 먼저 시도) | 비밀번호 규칙 오류 메시지 표시 | B6, F9 |
| 3 | 규칙에 맞는 비밀번호로 회원가입 | 영화 목록으로 이동, 우측 상단에 사용자명 | F9 |
| 4 | 영화 목록 확인 | 20편, 평점 높은 순, 뱃지 `source: django` | B4, F10 |
| 5 | 카드 클릭 → 상세 | 줄거리·포스터·장르 표시, 예고편 재생 | B4, F5, F7 |
| 6 | Recommended | 날씨에 맞는 장르의 영화 1편, 다시 추천 동작 | B8, F11 |
| 7 | 새로고침 | 로그인 유지 | F9 localStorage |
| 8 | 로그아웃 후 `/278` 직접 입력 | 로그인 페이지로 이동, 로그인 후 `/278`로 복귀 | F9 redirect |

## I3. 자주 만나는 문제와 해결

| 증상 | 원인 | 해결 |
| :--- | :--- | :--- |
| `python manage.py test`가 `Dependency on app with no migrations` 오류 | 마이그레이션 파일이 없음 | `makemigrations accounts movies` 후 생성된 파일 커밋 (B2) |
| `loaddata` 중 `IntegrityError` / FK 오류 | 참조 대상보다 먼저 적재했거나 DB에 옛 데이터가 남음 | 5개 파일을 한 번에 순서대로 적재. 꼬였다면 `db.sqlite3` 삭제 후 `migrate`부터 다시 (B3) |
| 콘솔에 `CORS policy` 오류 | Vite가 5173이 아닌 포트로 떴거나, `CorsMiddleware` 위치 문제 | 포트 확인, `CORS_ALLOWED_ORIGINS` 확인 (B9) |
| Django 모드에서 모든 요청이 401 | 토큰이 없거나 DB를 다시 만들어 토큰이 무효 | 로그아웃 후 다시 로그인 (F9의 401 처리가 자동으로 해 줌) |
| 헤더를 넣었는데도 401 | `Bearer <key>`로 보냄 | DRF 토큰은 `Token <key>` 형식 (F9) |
| `.env`를 바꿨는데 반영 안 됨 | Vite는 시작할 때만 `.env`를 읽음 | `npm run dev` 재시작 (F1) |
| URL 끝 슬래시 없이 POST하면 오류 | Django `APPEND_SLASH`는 POST를 리다이렉트할 수 없음 | 프론트에서 항상 `/movies/1/`처럼 끝 슬래시 포함 (F10) |
| 상세 페이지 간 이동 시 화면이 안 바뀜 | 같은 컴포넌트 재사용으로 `onMounted` 미실행 | `watch` + `immediate` (F5) |
| 모달을 닫아도 영상 소리가 남 | `v-show`로 숨겨서 iframe이 살아 있음 | `v-if` 사용 (F6) |
| YouTube 검색이 갑자기 403 | 일일 할당량(10,000 unit) 초과 | 다음 날 재시도, `maxResults` 줄이기 (F7) |

---

## 복습 체크리스트와 셀프 퀴즈

### ✅ 이 프로젝트로 익힌 개념

| 분류 | 개념 | 어디서 썼나 |
| :--- | :--- | :--- |
| Django 모델 | PK 설계, 1:N(`ForeignKey`), M:N(`ManyToManyField`), 역참조 `_set`, 커스텀 User | B1, B2 |
| 데이터 | CSV 정제, fixture 형식, `loaddata`, 외부 API 수집 스크립트 | B3 |
| DRF | `ModelSerializer`, 중첩 Serializer, `ReadOnlyField(source=)`, `@api_view`, `partial` | B4, B5 |
| HTTP | 메서드별 의미, 200·201·204·400·401·403·404 | B5, B6, B8 |
| 인증/권한 | dj-rest-auth, TokenAuthentication, 전역 `IsAuthenticated`, 작성자 검사 | B6 |
| ORM 심화 | `annotate` vs `aggregate`, `Avg`, `Count`, `order_by('?')` 대안, N+1과 `select_related`·`prefetch_related` | B4, B7, B8 |
| 보안 | CORS, XSS(`v-html` 회피), 환경 변수, 서버가 정하는 author | B5, B9, F8 |
| 테스트 | `APITestCase`, fixture 기반 테스트, 예외 케이스 테스트 | B10 |
| Vue 기본 | `ref`, `computed`, `v-if/v-else-if/v-else`, `v-for` + `:key`, `v-model.trim` | 모든 뷰 |
| 생명주기 | `onMounted`, `onUnmounted` | F4, F6 |
| 반응성 | `watch` + getter + `immediate` | F5 |
| 컴포넌트 통신 | props(↓), emit(↑), slot(마크업 ↓) | F4, F5, F6 |
| 고급 기능 | `Teleport`, 이벤트 수식어 `.self` `.prevent` | F6, F8 |
| 라우터 | 동적 세그먼트, 정규식 제약, named route, `meta`, `beforeEach` 가드, `redirect` 쿼리 | F2, F9 |
| 상태 관리 | Pinia Setup Store, localStorage 동기화 | F9 |
| 비동기 | `async/await`, `try/catch/finally`, 로딩·에러 상태, axios 인터셉터 | 모든 뷰, F9 |
| 설계 | API 레이어 분리, 어댑터 패턴, 규칙 테이블, 순환 참조 회피 | F3, F9, F10, F11 |

### ❓ 셀프 퀴즈 (답은 위 본문에 있어요)

**백엔드**
1. 커스텀 User 모델을 첫 `migrate` 전에 만들어야 하는 이유는? (B1)
2. Movie와 Genre의 PK를 TMDB ID로 정한 이유 두 가지는? (B2)
3. 마이그레이션 파일을 git에 커밋하지 않으면 어떤 일이 생기나요? (B2)
4. CSV 작성자 계정의 비밀번호를 `!`로 둔 이유는? (B3)
5. `select_related`와 `prefetch_related`는 각각 언제 쓰나요? (B4)
6. 리뷰의 `author`를 요청 본문이 아니라 `request.user`로 저장하는 이유는? (B5)
7. PUT과 PATCH를 하나의 Serializer 코드로 처리한 방법은? (B5)
8. 401과 403의 차이는? (B6)
9. `aggregate`와 `annotate`의 차이는? (B7)
10. `order_by('?')` 대신 `Count` + 랜덤 offset을 쓴 이유와, `order_by('id')`를 붙인 이유는? (B8)
11. Postman에서는 되는데 Vue에서는 Django API 호출이 실패합니다. 가장 먼저 의심할 것은? (B9)

**프론트엔드**

12. `/:movieId` 라우트에 `(\\d+)`를 붙이지 않으면 어떤 문제가 생길 수 있나요? (F2)
13. `/278`에서 `/238`로 이동했는데 화면이 안 바뀝니다. 원인과 해결책은? (F5)
14. 모달을 `v-show`로 숨기면 어떤 버그가 생기나요? (F6)
15. 유튜브 제목의 `&#39;`를 해결할 때 `v-html`을 쓰면 안 되는 이유는? (F8)
16. 토큰을 Pinia에만 두지 않고 localStorage에도 저장한 이유는? (F9)
17. 라우터 가드가 있는데도 401 응답 인터셉터가 필요한 이유는? (F9)
18. `django.js`에서 store와 router를 동적 `import()`로 불러온 이유는? (F9)
19. 뷰 코드 수정 없이 TMDB → Django 전환이 가능했던 핵심 조건은? (F10)
20. `VITE_` 환경 변수에 비밀 키를 넣는 것이 실서비스에서 위험한 이유는? (F1)

### 🚀 다음 단계 도전 과제
- **리뷰 작성 화면**: 백엔드 리뷰 CRUD API(B5)는 완성되어 있으니, 상세 페이지에 리뷰 목록·작성·수정·삭제 UI 붙이기 (본인 리뷰에만 수정/삭제 버튼)
- **영화 데이터 확장**: `fetch_tmdb.py`를 확장해 TMDB Top Rated 여러 페이지를 수집하고 fixture로 만들기
- **API 키 숨기기**: YouTube/TMDB 호출을 모두 Django를 거치게 하여 프론트에서 키 제거
- **페이지네이션**: Django에 `?page=` 지원 추가(DRF `PageNumberPagination`), 프론트에 무한 스크롤 적용
- **404 페이지**: 라우터 catch-all + 상세 API 404 응답 시 안내 화면
