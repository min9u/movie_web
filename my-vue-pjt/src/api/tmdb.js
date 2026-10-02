import axios from 'axios'

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
  return data.results
}

export async function fetchMovieDetail(movieId) {
  const { data } = await tmdb.get(`/movie/${movieId}`)
  return data
}

export async function fetchMoviesByGenre(genreId) {
  const { data } = await tmdb.get('/discover/movie', {
    params: {
      with_genres: genreId,
      sort_by: 'vote_average.desc',
      'vote_count.gte': 1000,
      page: Math.floor(Math.random() * 3) + 1,
    },
  })
  return data.results
}
