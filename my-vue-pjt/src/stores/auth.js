import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import * as accounts from '@/api/accounts'

const TOKEN_KEY = 'movieflix-token'
const USERNAME_KEY = 'movieflix-username'

// 사파리 사생활 보호 모드 등에서는 localStorage 접근이 예외를 던질 수 있음
function readStorage(key) {
  try {
    return localStorage.getItem(key)
  } catch {
    return null
  }
}

function writeStorage(key, value) {
  try {
    if (value) localStorage.setItem(key, value)
    else localStorage.removeItem(key)
  } catch {
    // 저장에 실패해도 현재 탭에서는 메모리의 토큰으로 계속 동작
  }
}

// Django(dj-rest-auth) 토큰 인증 상태
export const useAuthStore = defineStore('auth', () => {
  const token = ref(readStorage(TOKEN_KEY))
  const username = ref(readStorage(USERNAME_KEY))
  const isLoggedIn = computed(() => Boolean(token.value))

  const setSession = (newToken, newUsername) => {
    token.value = newToken
    username.value = newUsername
    writeStorage(TOKEN_KEY, newToken)
    writeStorage(USERNAME_KEY, newUsername)
  }

  const login = async (credentials) => {
    const key = await accounts.login(credentials)
    setSession(key, credentials.username)
  }

  const signup = async (payload) => {
    const key = await accounts.signup(payload)
    setSession(key, payload.username)
  }

  const logout = () => setSession(null, null)

  return { token, username, isLoggedIn, login, signup, logout }
})
