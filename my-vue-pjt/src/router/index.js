import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import MovieListView from '@/views/MovieListView.vue'
import MovieDetailView from '@/views/MovieDetailView.vue'
import ReviewSearchView from '@/views/ReviewSearchView.vue'
import RecommendedView from '@/views/RecommendedView.vue'
import LoginView from '@/views/LoginView.vue'
import SignupView from '@/views/SignupView.vue'
import { MOVIE_API_SOURCE } from '@/api/movies'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    // usesMovieApi: 영화 데이터를 불러오는 페이지 (Django 출처일 때 로그인 필요)
    { path: '/movies', name: 'movies', component: MovieListView, meta: { usesMovieApi: true } },
    { path: '/review-search', name: 'reviewSearch', component: ReviewSearchView },
    { path: '/recommended', name: 'recommended', component: RecommendedView, meta: { usesMovieApi: true } },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/signup', name: 'signup', component: SignupView },
    // 숫자 ID만 상세 페이지로 매칭되도록 제한 (정적 경로와의 충돌 방지)
    { path: '/:movieId(\\d+)', name: 'movieDetail', component: MovieDetailView, meta: { usesMovieApi: true } },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

// Django API 는 토큰 인증이 필요하므로, Django 출처일 때 비로그인 사용자는 로그인 페이지로
router.beforeEach((to) => {
  if (MOVIE_API_SOURCE !== 'django' || !to.meta.usesMovieApi) return
  if (!useAuthStore().isLoggedIn) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
})

export default router
