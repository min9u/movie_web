import axios from 'axios'
import { DJANGO_API_URL } from './django'

// dj-rest-auth 엔드포인트는 /api/v1 이 아닌 서버 루트의 /accounts/ 아래에 있음
const accounts = axios.create({
  baseURL: DJANGO_API_URL.replace(/\/api\/v1\/?$/, '') + '/accounts',
})

export async function login({ username, password }) {
  const { data } = await accounts.post('/login/', { username, password })
  return data.key
}

export async function signup({ username, password1, password2 }) {
  const { data } = await accounts.post('/signup/', { username, password1, password2 })
  return data.key
}

// DRF 검증 오류 응답({ field: ['메시지'] })을 한 줄 메시지로
export function formatAuthError(error) {
  const data = error.response?.data
  if (!data || typeof data !== 'object') return '서버에 연결하지 못했습니다. Django 서버가 실행 중인지 확인해주세요.'
  return Object.values(data).flat().join(' ')
}
