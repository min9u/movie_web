import axios from 'axios'

// F05: PJT02 Django REST API 서버
const django = axios.create({
  baseURL: import.meta.env.VITE_DJANGO_API_URL || 'http://127.0.0.1:8000/api/v1',
})

export async function fetchTopRated() {
  const { data } = await django.get('/movies/')
  return data
}

export async function fetchMovieDetail(movieId) {
  const { data } = await django.get(`/movies/${movieId}/`)
  return data
}

export async function fetchRandomMovieByGenre(genreId) {
  const { data } = await django.get('/movies/recommend/', { params: { genre: genreId } })
  return data
}
