<template>
  <div class="row g-4">
    <div class="col-md-4">
      <img :src="getPosterUrl(movie.poster_path)" class="img-fluid rounded shadow" :alt="movie.title" />
    </div>
    <div class="col-md-8">
      <h2 class="fw-bold">{{ movie.title }}</h2>
      <p v-if="movie.tagline" class="fst-italic text-secondary">{{ movie.tagline }}</p>

      <ul class="list-unstyled mb-3">
        <li><strong>개봉일</strong> : {{ movie.release_date || '-' }}</li>
        <li v-if="movie.runtime"><strong>러닝타임</strong> : {{ movie.runtime }}분</li>
        <li>
          <strong>평점</strong> : <span class="text-warning">★</span> {{ movie.vote_average?.toFixed(1) }}
          <span v-if="movie.vote_count" class="text-secondary small">({{ movie.vote_count.toLocaleString() }}명)</span>
        </li>
      </ul>

      <div class="mb-3">
        <span v-for="genre in movie.genres" :key="genre.name" class="badge rounded-pill text-bg-primary me-1">
          {{ genre.name }}
        </span>
      </div>

      <h5 class="fw-bold">줄거리</h5>
      <p class="lh-lg">{{ movie.overview || '줄거리 정보가 없습니다.' }}</p>

      <slot />
    </div>
  </div>
</template>

<script setup>
import { getPosterUrl } from '@/api/movies'

defineProps({
  movie: { type: Object, required: true },
})
</script>
