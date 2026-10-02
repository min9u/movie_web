from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from accounts.models import User
from .models import Review


class MovieApiTests(APITestCase):
    fixtures = ['users.json', 'genres.json', 'movies.json', 'casts.json', 'reviews.json']

    def setUp(self):
        # 리뷰 1번(Inside Out 2)의 작성자 Hotplix 로 인증
        self.author = Review.objects.get(pk=1).author
        self.login(self.author)

    def login(self, user):
        token, _ = Token.objects.get_or_create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

    # F02
    def test_genre_list(self):
        response = self.client.get('/api/v1/genres/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 14)
        self.assertEqual(set(response.data[0]), {'id', 'name'})

    # F03
    def test_movie_list(self):
        response = self.client.get('/api/v1/movies/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 20)
        inside_out = next(movie for movie in response.data if movie['id'] == 1022789)
        self.assertEqual(
            set(inside_out),
            {
                'id', 'title', 'release_date', 'popularity', 'budget', 'revenue', 'runtime',
                'overview', 'poster_path', 'vote_average', 'genres',
            },
        )
        self.assertCountEqual(inside_out['genres'], [16, 10751, 18, 12, 35])
        # 평점 높은 순
        averages = [movie['vote_average'] for movie in response.data]
        self.assertEqual(averages, sorted(averages, reverse=True))

    # F04, F09
    def test_movie_detail(self):
        response = self.client.get('/api/v1/movies/1022789/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['title'], 'Inside Out 2')
        self.assertEqual(response.data['id'], 1022789)
        self.assertTrue(response.data['overview'])
        self.assertTrue(response.data['poster_path'].startswith('/'))
        self.assertEqual(set(response.data['genres'][0]), {'name'})
        self.assertEqual(set(response.data['cast_set'][0]), {'name', 'character', 'order'})
        self.assertEqual(set(response.data['review_set'][0]), {'author', 'content', 'rating'})

        ratings = list(Review.objects.filter(movie=1022789).values_list('rating', flat=True))
        self.assertEqual(response.data['vote_count'], len(ratings))
        self.assertAlmostEqual(response.data['average_rating'], sum(ratings) / len(ratings))

    def test_movie_detail_not_found(self):
        self.assertEqual(self.client.get('/api/v1/movies/1/').status_code, 404)

    # 날씨 기반 추천
    def test_movie_recommend(self):
        response = self.client.get('/api/v1/movies/recommend/', {'genre': 27})
        self.assertEqual(response.status_code, 200)
        self.assertIn(27, response.data['genres'])
        self.assertIn('poster_path', response.data)

    def test_movie_recommend_invalid_genre(self):
        self.assertEqual(self.client.get('/api/v1/movies/recommend/').status_code, 400)
        self.assertEqual(self.client.get('/api/v1/movies/recommend/', {'genre': 'abc'}).status_code, 400)
        # 영화가 없는 장르(TV 영화)
        self.assertEqual(self.client.get('/api/v1/movies/recommend/', {'genre': 10770}).status_code, 404)

    # F05
    def test_review_list(self):
        response = self.client.get('/api/v1/reviews/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 62)
        self.assertEqual(response.data[0]['movie'], {'id': 1022789, 'title': 'Inside Out 2'})
        self.assertEqual(set(response.data[0]), {'id', 'movie', 'author', 'content', 'rating'})

    # F06
    def test_review_detail(self):
        response = self.client.get('/api/v1/reviews/1/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['author'], 'Hotplix')

    def test_review_put(self):
        response = self.client.put('/api/v1/reviews/1/', {'content': 'review update', 'rating': 5.9})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['content'], 'review update')
        self.assertEqual(response.data['rating'], 5.9)

    def test_review_put_partial_fails(self):
        response = self.client.put('/api/v1/reviews/1/', {'content': 'review update 2'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('rating', response.data)

    def test_review_patch(self):
        response = self.client.patch('/api/v1/reviews/1/', {'content': 'review update 2'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['content'], 'review update 2')

    def test_review_delete(self):
        response = self.client.delete('/api/v1/reviews/1/')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(response.data, {'delete': '1번 째 리뷰가 정상적으로 삭제되었습니다.'})
        self.assertFalse(Review.objects.filter(pk=1).exists())

    # F07
    def test_review_create(self):
        response = self.client.post(
            '/api/v1/movies/653346/reviews/', {'content': 'new review create', 'rating': 3}
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['movie'], {'id': 653346, 'title': 'Kingdom of the Planet of the Apes'})
        self.assertEqual(response.data['author'], self.author.username)
        self.assertEqual(response.data['rating'], 3.0)

    # F08
    def test_requires_token(self):
        self.client.credentials()
        self.assertEqual(self.client.get('/api/v1/movies/').status_code, 401)

    def test_only_author_can_modify(self):
        self.login(User.objects.create_user(username='other', password='pw-for-test-123'))
        self.assertEqual(self.client.get('/api/v1/reviews/1/').status_code, 200)
        self.assertEqual(self.client.patch('/api/v1/reviews/1/', {'rating': 1}).status_code, 403)
        self.assertEqual(self.client.delete('/api/v1/reviews/1/').status_code, 403)

    def test_signup_and_login(self):
        self.client.credentials()
        password = 'ssafy-movie-1234'
        response = self.client.post(
            '/accounts/signup/', {'username': 'newbie', 'password1': password, 'password2': password}
        )
        self.assertEqual(response.status_code, 201, response.data)

        response = self.client.post('/accounts/login/', {'username': 'newbie', 'password': password})
        self.assertEqual(response.status_code, 200)
        self.assertIn('key', response.data)

        self.client.credentials(HTTP_AUTHORIZATION=f"Token {response.data['key']}")
        self.assertEqual(self.client.get('/api/v1/genres/').status_code, 200)
