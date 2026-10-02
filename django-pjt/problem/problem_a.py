"""
제공된 CSV(problem/data)를 Django fixture(JSON)로 변환한다.

실행: python problem/problem_a.py
적재: python manage.py loaddata users.json genres.json movies.json casts.json reviews.json
"""
import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / 'data'
PROJECT_DIR = BASE_DIR.parent

# movie_details.csv 의 장르 이름 -> TMDB 장르 id
GENRE_IDS = {
    'Action': 28,
    'Adventure': 12,
    'Animation': 16,
    'Comedy': 35,
    'Crime': 80,
    'Drama': 18,
    'Family': 10751,
    'Fantasy': 14,
    'Horror': 27,
    'Mystery': 9648,
    'Romance': 10749,
    'Science Fiction': 878,
    'Thriller': 53,
    'War': 10752,
}


def read_csv(file_name):
    with open(DATA_DIR / file_name, newline='', encoding='utf-8') as file:
        return list(csv.DictReader(file))


# 'Animation, Family' -> [16, 10751]
def to_genre_ids(genres_text):
    genre_ids = []
    for name in genres_text.split(', '):
        if name not in GENRE_IDS:
            raise ValueError(f'매핑에 없는 장르 이름입니다: {name}')
        genre_ids.append(GENRE_IDS[name])
    return genre_ids


# CSV 에 실제로 등장한 장르만 id 오름차순으로
def make_genres(details):
    used_ids = {genre_id for row in details for genre_id in to_genre_ids(row['genres'])}
    names = {genre_id: name for name, genre_id in GENRE_IDS.items()}
    return [
        {'model': 'movies.genre', 'pk': genre_id, 'fields': {'name': names[genre_id]}}
        for genre_id in sorted(used_ids)
    ]


# movies.csv, movie_details.csv, movie_tmdb.csv(fetch_tmdb.py 로 수집)를 movie_id 기준으로 통합
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
                'release_date': row['release_date'],
                'popularity': float(row['popularity']),
                'budget': int(detail['budget']),
                'revenue': int(detail['revenue']),
                'runtime': int(detail['runtime']),
                'overview': tmdb['overview'],
                'poster_path': tmdb['poster_path'],
                'vote_average': float(tmdb['vote_average']),
                'genres': to_genre_ids(detail['genres']),
            },
        })
    return fixtures


# cast_id 는 영화마다 0부터 다시 시작해 겹치므로 CSV 순서대로 1부터 pk 를 붙인다
def make_casts(casts):
    return [
        {
            'model': 'movies.cast',
            'pk': pk,
            'fields': {
                'movie': int(row['movie_id']),
                'name': row['name'],
                'character': row['character'],
                'order': int(row['order']),
            },
        }
        for pk, row in enumerate(casts, start=1)
    ]


# F08: Review.author 가 User FK 이므로 CSV 의 작성자 이름마다 로그인 불가 계정을 만든다
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


# review_id 는 16진 문자열이라 CSV 순서대로 1부터 pk 를 붙인다
def make_reviews(reviews, users):
    user_pks = {user['fields']['username']: user['pk'] for user in users}
    return [
        {
            'model': 'movies.review',
            'pk': pk,
            'fields': {
                'movie': int(row['movie_id']),
                'author': user_pks[row['author']],
                'content': row['content'],
                'rating': float(row['rating']),
            },
        }
        for pk, row in enumerate(reviews, start=1)
    ]


def write_fixture(app_name, file_name, data):
    fixture_dir = PROJECT_DIR / app_name / 'fixtures'
    fixture_dir.mkdir(parents=True, exist_ok=True)
    with open(fixture_dir / file_name, 'w', newline='\n', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write('\n')
    print(f'{app_name}/fixtures/{file_name}: {len(data)}개')


def main():
    movies = read_csv('movies.csv')
    details = read_csv('movie_details.csv')
    casts = read_csv('movie_cast.csv')
    reviews = read_csv('movie_reviews.csv')
    tmdb_rows = read_csv('movie_tmdb.csv')
    users = make_users(reviews)

    write_fixture('accounts', 'users.json', users)
    write_fixture('movies', 'genres.json', make_genres(details))
    write_fixture('movies', 'movies.json', make_movies(movies, details, tmdb_rows))
    write_fixture('movies', 'casts.json', make_casts(casts))
    write_fixture('movies', 'reviews.json', make_reviews(reviews, users))


if __name__ == '__main__':
    main()
