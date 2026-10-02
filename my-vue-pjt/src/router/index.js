import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import MovieListView from '@/views/MovieListView.vue'
import MovieDetailView from '@/views/MovieDetailView.vue'
import ReviewSearchView from '@/views/ReviewSearchView.vue'
import RecommendedView from '@/views/RecommendedView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/movies', name: 'movies', component: MovieListView },
    { path: '/review-search', name: 'reviewSearch', component: ReviewSearchView },
    { path: '/recommended', name: 'recommended', component: RecommendedView },
    // 숫자 ID만 상세 페이지로 매칭되도록 제한 (정적 경로와의 충돌 방지)
    { path: '/:movieId(\\d+)', name: 'movieDetail', component: MovieDetailView },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router
