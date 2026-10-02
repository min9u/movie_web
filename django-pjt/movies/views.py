from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Genre, Movie, Review
from .serializers import GenreSerializer, MovieListSerializer, MovieSerializer, ReviewSerializer


# F02: 전체 장르 목록 조회
@api_view(['GET'])
def genre_list(request):
    genres = Genre.objects.all()
    serializer = GenreSerializer(genres, many=True)
    return Response(serializer.data)


# F03: 전체 영화 목록 조회
@api_view(['GET'])
def movie_list(request):
    movies = Movie.objects.prefetch_related('genres')
    serializer = MovieListSerializer(movies, many=True)
    return Response(serializer.data)


# F04: 단일 영화 상세 정보 조회 (+ F09: 평균 평점, 총 투표 수)
@api_view(['GET'])
def movie_detail(request, movie_pk):
    movies = Movie.objects.annotate(
        average_rating=Avg('review__rating'),
        # rating 값이 있는 리뷰만 센다
        vote_count=Count('review__rating'),
    ).prefetch_related('genres', 'cast_set', 'review_set__author')
    movie = get_object_or_404(movies, pk=movie_pk)
    serializer = MovieSerializer(movie)
    return Response(serializer.data)


# F05: 전체 리뷰 목록 조회
@api_view(['GET'])
def review_list(request):
    reviews = Review.objects.select_related('movie', 'author')
    serializer = ReviewSerializer(reviews, many=True)
    return Response(serializer.data)


# F06: 단일 리뷰 조회/수정/삭제
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def review_detail(request, review_pk):
    review = get_object_or_404(Review.objects.select_related('movie', 'author'), pk=review_pk)

    if request.method == 'GET':
        serializer = ReviewSerializer(review)
        return Response(serializer.data)

    # F08: 수정/삭제는 작성자 본인만
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


# F07: 특정 영화에 대한 리뷰 생성
@api_view(['POST'])
def review_create(request, movie_pk):
    movie = get_object_or_404(Movie, pk=movie_pk)
    serializer = ReviewSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(movie=movie, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
