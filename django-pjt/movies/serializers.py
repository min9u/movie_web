from rest_framework import serializers
from .models import Cast, Genre, Movie, Review


# F02: 장르 목록
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('id', 'name')


# F03: 영화 목록 - genres 는 장르 id 목록으로
class MovieListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = '__all__'


# F05, F06, F07: 리뷰 - 참조 중인 movie 는 id, title 만
class ReviewSerializer(serializers.ModelSerializer):
    class MovieTitleSerializer(serializers.ModelSerializer):
        class Meta:
            model = Movie
            fields = ('id', 'title')

    movie = MovieTitleSerializer(read_only=True)
    # F08: 작성자는 요청한 유저로 저장되므로 입력받지 않고 username 만 보여준다
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Review
        fields = ('id', 'movie', 'author', 'content', 'rating')


# F04: 영화 상세 - 영화를 참조하는 Cast, Review 와 M:N 관계의 Genre 이름을 함께
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
    # F09: view 에서 Avg / Count 로 annotate 한 값
    average_rating = serializers.FloatField(read_only=True)
    vote_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Movie
        fields = (
            'title', 'release_date', 'popularity', 'budget', 'revenue', 'runtime',
            'genres', 'cast_set', 'review_set', 'average_rating', 'vote_count',
        )
