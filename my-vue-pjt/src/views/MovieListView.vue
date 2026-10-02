<template>
  <div class="d-flex align-items-center justify-content-between mb-4">
    <h2 class="fw-bold mb-0">🏆 최고 평점 영화</h2>
    <span class="badge text-bg-secondary">source: {{ MOVIE_API_SOURCE }}</span>
  </div>

  <div v-if="isLoading" class="text-center py-5">
    <div class="spinner-border" role="status"></div>
  </div>
  <div v-else-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
  <div v-else class="row row-cols-2 row-cols-md-3 row-cols-lg-4 row-cols-xl-5 g-4">
    <div v-for="movie in movies" :key="movie.id" class="col">
      <MovieCard :movie="movie" />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import MovieCard from '@/components/MovieCard.vue'
import { getTopRatedMovies, MOVIE_API_SOURCE } from '@/api/movies'

const movies = ref([])
const isLoading = ref(true)
const errorMessage = ref('')

// F01: 컴포넌트 생성 시 Top Rated 영화 목록 요청
onMounted(async () => {
  try {
    movies.value = await getTopRatedMovies()
  } catch (error) {
    console.error(error)
    errorMessage.value = '영화 목록을 불러오지 못했습니다. API Key 또는 서버 상태를 확인해주세요.'
  } finally {
    isLoading.value = false
  }
})
</script>
