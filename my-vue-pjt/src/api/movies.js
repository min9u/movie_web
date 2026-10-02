import * as tmdb from './tmdb'
import * as django from './django'

// .env 의 VITE_MOVIE_API_SOURCE 값으로 데이터 출처를 전환 (tmdb | django)
export const MOVIE_API_SOURCE = import.meta.env.VITE_MOVIE_API_SOURCE === 'django' ? 'django' : 'tmdb'
const useDjango = MOVIE_API_SOURCE === 'django'

export function getTopRatedMovies() {
  return useDjango ? django.fetchTopRated() : tmdb.fetchTopRated()
}

export function getMovieDetail(movieId) {
  return useDjango ? django.fetchMovieDetail(movieId) : tmdb.fetchMovieDetail(movieId)
}

export async function getRandomMovieByGenre(genreId) {
  // Django 서버는 ORM Count 집계로 직접 랜덤 1편을 골라서 응답
  if (useDjango) return django.fetchRandomMovieByGenre(genreId)

  const movies = await tmdb.fetchMoviesByGenre(genreId)
  if (!movies.length) return null
  return movies[Math.floor(Math.random() * movies.length)]
}

export function getPosterUrl(posterPath, size = 'w500') {
  if (!posterPath) return 'https://placehold.co/500x750?text=No+Image'
  return `${tmdb.TMDB_IMAGE_URL}/${size}${posterPath}`
}
