<template>
  <button class="btn btn-link px-0 mb-3" @click="router.back()">← 뒤로 가기</button>

  <div v-if="isLoading" class="text-center py-5">
    <div class="spinner-border" role="status"></div>
  </div>
  <div v-else-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
  <MovieDetailInfo v-else :movie="movie">
    <button class="btn btn-danger btn-lg mt-2" @click="isTrailerOpen = true">▶ 공식 예고편</button>
  </MovieDetailInfo>

  <YoutubeTrailerModal
    v-if="isTrailerOpen"
    :movie-title="movie.original_title || movie.title"
    @close="isTrailerOpen = false"
  />
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MovieDetailInfo from '@/components/MovieDetailInfo.vue'
import YoutubeTrailerModal from '@/components/YoutubeTrailerModal.vue'
import { getMovieDetail } from '@/api/movies'

const route = useRoute()
const router = useRouter()

const movie = ref(null)
const isLoading = ref(true)
const errorMessage = ref('')
const isTrailerOpen = ref(false)

// F02: URL 파라미터의 movieId 로 상세 정보 요청
// (같은 컴포넌트에서 다른 영화로 이동해도 다시 요청하도록 watch 사용)
watch(
  () => route.params.movieId,
  async (movieId) => {
    if (!movieId) return
    isLoading.value = true
    errorMessage.value = ''
    isTrailerOpen.value = false
    try {
      movie.value = await getMovieDetail(movieId)
    } catch (error) {
      console.error(error)
      errorMessage.value = '영화 정보를 불러오지 못했습니다.'
    } finally {
      isLoading.value = false
    }
  },
  { immediate: true },
)
</script>
