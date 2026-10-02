<template>
  <header>
    <nav class="navbar navbar-expand navbar-dark bg-dark sticky-top shadow-sm">
      <div class="container">
        <RouterLink class="navbar-brand fw-bold" :to="{ name: 'home' }">🎬 MovieFlix</RouterLink>
        <ul class="navbar-nav gap-1 flex-wrap">
          <li class="nav-item">
            <RouterLink class="nav-link" :to="{ name: 'home' }" exact-active-class="active">Home</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" :to="{ name: 'movies' }" active-class="active">Movies</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" :to="{ name: 'reviewSearch' }" active-class="active">Review Search</RouterLink>
          </li>
          <li class="nav-item">
            <RouterLink class="nav-link" :to="{ name: 'recommended' }" active-class="active">Recommended</RouterLink>
          </li>
        </ul>
        <div v-if="MOVIE_API_SOURCE === 'django'" class="d-flex align-items-center gap-2 ms-auto">
          <template v-if="auth.isLoggedIn">
            <span class="text-light small">{{ auth.username }}</span>
            <button class="btn btn-outline-light btn-sm" type="button" @click="onLogout">로그아웃</button>
          </template>
          <RouterLink v-else class="btn btn-outline-light btn-sm" :to="{ name: 'login' }">로그인</RouterLink>
        </div>
      </div>
    </nav>
  </header>

  <main class="container py-4">
    <RouterView />
  </main>
</template>

<script setup>
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { MOVIE_API_SOURCE } from '@/api/movies'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const onLogout = () => {
  auth.logout()
  router.push({ name: 'home' })
}
</script>
