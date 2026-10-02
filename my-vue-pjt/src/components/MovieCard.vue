<template>
  <RouterLink :to="{ name: 'movieDetail', params: { movieId: movie.id } }" class="text-decoration-none text-reset">
    <div class="card h-100 border-0 shadow-sm hover-lift">
      <img :src="getPosterUrl(movie.poster_path)" class="card-img-top" :alt="movie.title" loading="lazy" />
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-start gap-2 mb-2">
          <h6 class="card-title fw-bold mb-0">{{ movie.title }}</h6>
          <span class="badge text-bg-warning">★ {{ movie.vote_average?.toFixed(1) }}</span>
        </div>
        <p class="card-text small text-secondary text-clamp-3 mb-0">
          {{ movie.overview || '줄거리 정보가 없습니다.' }}
        </p>
      </div>
    </div>
  </RouterLink>
</template>

<script setup>
import { RouterLink } from 'vue-router'
import { getPosterUrl } from '@/api/movies'

defineProps({
  movie: { type: Object, required: true },
})
</script>
