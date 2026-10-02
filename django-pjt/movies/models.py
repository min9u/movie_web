from django.conf import settings
from django.db import models


class Genre(models.Model):
    # TMDB 장르 ID를 그대로 PK로 사용
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


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

    def __str__(self):
        return self.title


# Movie 1:N Cast
class Cast(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    character = models.CharField(max_length=255)
    order = models.IntegerField()

    def __str__(self):
        return f'{self.name} ({self.character})'


# Movie 1:N Review
class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    # F08: 문자열 작성자 대신 User 를 참조
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    rating = models.FloatField()

    def __str__(self):
        return f'[{self.movie}] {self.author}'
