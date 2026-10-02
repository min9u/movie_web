<template>
  <div class="row justify-content-center">
    <div class="col-sm-10 col-md-6 col-lg-4">
      <h2 class="fw-bold mb-4">📝 회원가입</h2>

      <form class="card card-body shadow-sm gap-3" @submit.prevent="onSubmit">
        <div>
          <label for="username" class="form-label">아이디</label>
          <input id="username" v-model.trim="username" type="text" class="form-control" autocomplete="username" required />
        </div>
        <div>
          <label for="password1" class="form-label">비밀번호</label>
          <input id="password1" v-model="password1" type="password" class="form-control" autocomplete="new-password" required />
        </div>
        <div>
          <label for="password2" class="form-label">비밀번호 확인</label>
          <input id="password2" v-model="password2" type="password" class="form-control" autocomplete="new-password" required />
        </div>
        <div v-if="errorMessage" class="alert alert-danger py-2 mb-0">{{ errorMessage }}</div>
        <button class="btn btn-dark" type="submit" :disabled="isSubmitting">가입하기</button>
      </form>

      <p class="text-center mt-3 small">
        이미 계정이 있나요? <RouterLink :to="{ name: 'login', query: route.query }">로그인</RouterLink>
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
const password1 = ref('')
const password2 = ref('')
const isSubmitting = ref(false)
const errorMessage = ref('')

// 가입 성공 시 dj-rest-auth 가 바로 토큰을 발급하므로 로그인 상태로 이동
const onSubmit = async () => {
  if (password1.value !== password2.value) {
    errorMessage.value = '비밀번호가 일치하지 않습니다.'
    return
  }
  isSubmitting.value = true
  errorMessage.value = ''
  try {
    await auth.signup({ username: username.value, password1: password1.value, password2: password2.value })
    router.replace(route.query.redirect || { name: 'movies' })
  } catch (error) {
    console.error(error)
    errorMessage.value = formatAuthError(error)
  } finally {
    isSubmitting.value = false
  }
}
</script>
