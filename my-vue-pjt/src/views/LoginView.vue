<template>
  <div class="row justify-content-center">
    <div class="col-sm-10 col-md-6 col-lg-4">
      <h2 class="fw-bold mb-2">🔑 로그인</h2>
      <p class="text-secondary small mb-4">영화 데이터는 Django API 서버에서 제공되며, 로그인한 사용자만 조회할 수 있습니다.</p>

      <form class="card card-body shadow-sm gap-3" @submit.prevent="onSubmit">
        <div>
          <label for="username" class="form-label">아이디</label>
          <input id="username" v-model.trim="username" type="text" class="form-control" autocomplete="username" required />
        </div>
        <div>
          <label for="password" class="form-label">비밀번호</label>
          <input id="password" v-model="password" type="password" class="form-control" autocomplete="current-password" required />
        </div>
        <div v-if="errorMessage" class="alert alert-danger py-2 mb-0">{{ errorMessage }}</div>
        <button class="btn btn-dark" type="submit" :disabled="isSubmitting">로그인</button>
      </form>

      <p class="text-center mt-3 small">
        계정이 없나요? <RouterLink :to="{ name: 'signup', query: route.query }">회원가입</RouterLink>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { formatAuthError } from '@/api/accounts'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const isSubmitting = ref(false)
const errorMessage = ref('')

const onSubmit = async () => {
  isSubmitting.value = true
  errorMessage.value = ''
  try {
    await auth.login({ username: username.value, password: password.value })
    router.replace(route.query.redirect || { name: 'movies' })
  } catch (error) {
    console.error(error)
    errorMessage.value = formatAuthError(error)
  } finally {
    isSubmitting.value = false
  }
}
</script>
