# 02-pjt: DB 설계를 활용한 REST API 설계

영화·출연진·리뷰·장르 데이터를 제공하고 리뷰 CRUD 를 지원하는 DRF API 서버.

## 실행

```bash
python -m venv venv
source venv/Scripts/activate
pip install -r requirements.txt

python problem/problem_a.py   # CSV(problem/data) -> fixture(JSON) 생성
python manage.py migrate
python manage.py loaddata users.json genres.json movies.json casts.json reviews.json
python manage.py runserver
```

테스트: `python manage.py test movies`

## 모델 (F01)

| 모델 | 필드 | 관계 |
|---|---|---|
| Movie | id(TMDB id, PK), title, release_date, popularity, budget, revenue, runtime | Genre 와 M:N (`genres`) |
| Genre | id(TMDB 장르 id, PK), name | |
| Cast | movie, name, character, order | Movie 1:N |
| Review | movie, author, content, rating | Movie 1:N, User 1:N (F08) |

- `movie_cast.csv` 의 `cast_id` 는 영화마다 겹치고, `movie_reviews.csv` 의 `review_id` 는 16진 문자열이라 둘 다 CSV 순서대로 1부터 pk 를 다시 붙였다.
- `movie_details.csv` 의 장르 이름(`"Animation, Family"`)은 TMDB 장르 id 로 바꿔 M:N 으로 연결했다.
- F08 로 Review.author 가 User FK 가 되어, CSV 의 작성자 이름마다 로그인할 수 없는 계정(비밀번호 `!`)을 만들어 연결했다.

## API

`/accounts/signup/`, `/accounts/login/` 를 제외한 모든 요청은 헤더에 `Authorization: Token <key>` 가 필요하다 (F08).

| 번호 | Method | URL | 설명 |
|---|---|---|---|
| F02 | GET | `/api/v1/genres/` | 장르 목록 `[{id, name}]` |
| F03 | GET | `/api/v1/movies/` | 영화 목록 (genres 는 장르 id 목록) |
| F04 / F09 | GET | `/api/v1/movies/<movie_pk>/` | 영화 상세 + genres(name), cast_set, review_set, average_rating, vote_count |
| F05 | GET | `/api/v1/reviews/` | 리뷰 목록 (movie 는 `{id, title}`) |
| F06 | GET | `/api/v1/reviews/<review_pk>/` | 리뷰 조회 |
| F06 | PUT | `/api/v1/reviews/<review_pk>/` | 전체 수정 (content, rating 모두 필요, 하나라도 없으면 400) |
| F06 | PATCH | `/api/v1/reviews/<review_pk>/` | 일부 수정 |
| F06 | DELETE | `/api/v1/reviews/<review_pk>/` | 삭제 (204, `{"delete": "N번 째 리뷰가 정상적으로 삭제되었습니다."}`) |
| F07 | POST | `/api/v1/movies/<movie_pk>/reviews/` | 리뷰 생성 (201) |
| F08 | POST | `/accounts/signup/` | 회원가입 (username, password1, password2) → 토큰 발급 |
| F08 | POST | `/accounts/login/` | 로그인 (username, password) → `{"key": "<token>"}` |

- 리뷰 수정/삭제는 작성자 본인만 가능하고, 다른 사용자는 403을 받는다 (F08).
- author 는 요청한 사용자로 저장되므로 PUT/POST 본문에 넣지 않는다. 명세의 PUT 필수 필드(author, content, rating) 중 author 는 F08 적용으로 토큰 사용자로 대체되었다.
- F09 의 average_rating 은 `Avg('review__rating')`, vote_count 는 `Count('review__rating')` 로 계산한다. 리뷰가 없으면 average_rating 은 `null` 이다.

## 회고

### 학습한 내용

### 어려웠던 부분

### 새로 배운 것 / 느낀 점
