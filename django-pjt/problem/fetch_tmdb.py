"""
movies.csv 의 영화마다 TMDB 상세 API 에서 줄거리·포스터 경로·평점을 받아 CSV 로 저장한다.
프론트엔드 화면(카드, 상세)에 필요한 데이터가 제공된 CSV 에는 없어서 추가로 수집한다.

실행: TMDB_API_KEY=<v3 키 또는 v4 토큰> python problem/fetch_tmdb.py
결과: problem/data/movie_tmdb.csv  (problem_a.py 가 fixture 를 만들 때 합친다)
"""
import csv
import os
from pathlib import Path

import requests

DATA_DIR = Path(__file__).resolve().parent / 'data'
TMDB_URL = 'https://api.themoviedb.org/3/movie/{movie_id}'


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
        response = session.get(TMDB_URL.format(movie_id=movie_id), params={'language': 'en-US'}, timeout=10)
        response.raise_for_status()
        overview = response.json()['overview']
    return {
        'movie_id': movie_id,
        'overview': overview,
        'poster_path': movie['poster_path'] or '',
        'vote_average': movie['vote_average'],
    }


def main():
    api_key = os.environ.get('TMDB_API_KEY')
    if not api_key:
        raise SystemExit('TMDB_API_KEY 환경 변수를 설정해주세요.')

    with open(DATA_DIR / 'movies.csv', newline='', encoding='utf-8') as file:
        movie_ids = [row['id'] for row in csv.DictReader(file)]

    session = tmdb_session(api_key)
    rows = [fetch_movie(session, movie_id) for movie_id in movie_ids]

    with open(DATA_DIR / 'movie_tmdb.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['movie_id', 'overview', 'poster_path', 'vote_average'])
        writer.writeheader()
        writer.writerows(rows)
    print(f'problem/data/movie_tmdb.csv: {len(rows)}개')


if __name__ == '__main__':
    main()
