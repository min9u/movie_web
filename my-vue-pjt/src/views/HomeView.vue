<template>
  <section class="p-5 mb-4 bg-dark text-white rounded-4 shadow">
    <h1 class="display-5 fw-bold">🎬 MovieFlix</h1>
    <p class="fs-5 mb-4">평점 높은 영화를 둘러보고, 예고편과 리뷰 영상을 한 곳에서 확인하세요.</p>
    <RouterLink class="btn btn-warning btn-lg" :to="{ name: 'movies' }">영화 보러 가기</RouterLink>
  </section>

  <div class="row g-4">
    <div v-for="menu in menus" :key="menu.name" class="col-md-4">
      <RouterLink :to="{ name: menu.name }" class="text-decoration-none text-reset">
        <div class="card h-100 border-0 shadow-sm hover-lift">
          <div class="card-body">
            <div class="fs-1">{{ menu.icon }}</div>
            <h5 class="card-title fw-bold">{{ menu.title }}</h5>
            <p class="card-text text-secondary">{{ menu.description }}</p>
          </div>
        </div>
      </RouterLink>
    </div>
  </div>
</template>

<script setup>
import { RouterLink } from 'vue-router'

const menus = [
  { name: 'movies', icon: '🏆', title: 'Movies', description: '최고 평점 영화 목록과 상세 정보, 공식 예고편을 확인합니다.' },
  { name: 'reviewSearch', icon: '🔍', title: 'Review Search', description: '영화 제목으로 Youtube 리뷰 영상을 검색하고 바로 재생합니다.' },
  { name: 'recommended', icon: '🌤️', title: 'Recommended', description: '지금 서울 날씨에 어울리는 영화를 랜덤으로 추천받습니다.' },
]
</script>
