<template>
  <h2 class="fw-bold mb-4">🌤️ 오늘 날씨 맞춤 추천</h2>

  <div v-if="isLoading" class="text-center py-5">
    <div class="spinner-border" role="status"></div>
  </div>
  <div v-else-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
  <template v-else>
    <div class="card border-0 shadow-sm mb-4">
      <div class="card-body d-flex flex-wrap align-items-center gap-3">
        <span class="display-5">{{ rule.icon }}</span>
        <div class="flex-grow-1">
          <div class="fw-bold fs-5">서울 현재 날씨 : {{ rule.label }} ({{ weather.temperature }}°C)</div>
          <div class="text-secondary">
            WMO 코드 {{ weather.weathercode }} → 추천 장르
            <span class="badge text-bg-primary">{{ rule.genre.name }}</span>
          </div>
        </div>
        <button class="btn btn-outline-dark" :disabled="isPicking" @click="pickMovie">🎲 다른 영화 추천</button>
      </div>
    </div>

    <div v-if="isPicking" class="text-center py-5">
      <div class="spinner-border" role="status"></div>
    </div>
    <p v-else-if="!movie" class="text-secondary text-center py-5">추천할 영화가 없습니다.</p>
    <div v-else class="row justify-content-center">
      <div class="col-sm-8 col-md-5 col-lg-4">
        <MovieCard :movie="movie" />
      </div>
    </div>
  </template>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import MovieCard from '@/components/MovieCard.vue'
import { fetchSeoulWeather, matchWeatherGenre } from '@/api/weather'
import { getRandomMovieByGenre } from '@/api/movies'

const weather = ref(null)
const rule = ref(null)
const movie = ref(null)
const isLoading = ref(true)
const isPicking = ref(false)
const errorMessage = ref('')

const pickMovie = async () => {
  isPicking.value = true
  try {
    movie.value = await getRandomMovieByGenre(rule.value.genre.id)
  } catch (error) {
    console.error(error)
    movie.value = null
  } finally {
    isPicking.value = false
  }
}

// F06: 생성 시 서울 현재 날씨 조회 -> 장르 매칭 -> 랜덤 영화 추천
onMounted(async () => {
  try {
    weather.value = await fetchSeoulWeather()
    rule.value = matchWeatherGenre(weather.value.weathercode)
  } catch (error) {
    console.error(error)
    errorMessage.value = '날씨 정보를 불러오지 못했습니다.'
    return
  } finally {
    isLoading.value = false
  }
  await pickMovie()
})
</script>
