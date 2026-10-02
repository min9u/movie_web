import axios from 'axios'

export const DJANGO_API_URL = import.meta.env.VITE_DJANGO_API_URL || 'http://127.0.0.1:8000/api/v1'

// F05: PJT02 Django REST API 서버
const django = axios.create({
  baseURL: DJANGO_API_URL,
})

// 서버의 모든 API 가 토큰 인증을 요구하므로 로그인 시 발급받은 토큰을 헤더에 싣는다
// (store 를 지연 import 해서 stores/auth.js ↔ api 모듈 간 순환 참조를 피함)
django.interceptors.request.use(async (config) => {
  const { useAuthStore } = await import('@/stores/auth')
  const auth = useAuthStore()
  if (auth.token) config.headers.Authorization = `Token ${auth.token}`
  return config
})

// 토큰이 없거나 만료되면 로그아웃 후 로그인 페이지로
django.interceptors.response.use(undefined, async (error) => {
  if (error.response?.status === 401) {
    const [{ useAuthStore }, { default: router }] = await Promise.all([
      import('@/stores/auth'),
      import('@/router'),
    ])
    useAuthStore().logout()
    router.push({ name: 'login', query: { redirect: router.currentRoute.value.fullPath } })
  }
  return Promise.reject(error)
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
  try {
    const { data } = await django.get('/movies/recommend/', { params: { genre: genreId } })
    return data
  } catch (error) {
    // 해당 장르의 영화가 없으면 404 → 추천 없음으로 처리
    if (error.response?.status === 404) return null
    throw error
  }
}
