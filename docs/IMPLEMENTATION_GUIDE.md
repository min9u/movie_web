# 📘 구현 학습 가이드 — Vue SPA 영화 서비스 (PJT 03)

> 이 문서는 "무엇을 만들었는가"보다 **"어떤 순서로, 왜 그렇게 만들었는가"** 를 따라가며 배울 수 있도록 정리한 학습용 문서입니다.
> 각 단계는 **목표 → 핵심 개념 → 코드 → 왜 이렇게 했나 → 직접 해보기** 순서로 구성되어 있습니다.
> 코드는 실제 프로젝트 파일에서 발췌했으니, 파일을 옆에 열어두고 함께 읽으면 좋습니다.

---

## 목차

0. [전체 그림 먼저 보기](#0-전체-그림-먼저-보기)
1. [Step 1. Vue 프로젝트 생성과 진입점(main.js)](#step-1-vue-프로젝트-생성과-진입점-mainjs)
2. [Step 2. 라우터와 네비게이션 바](#step-2-라우터와-네비게이션-바)
3. [Step 3. API 레이어 분리 — axios 인스턴스 만들기](#step-3-api-레이어-분리--axios-인스턴스-만들기)
4. [Step 4. F01 최고 평점 영화 목록](#step-4-f01-최고-평점-영화-목록)
5. [Step 5. F02 영화 상세 정보](#step-5-f02-영화-상세-정보)
6. [Step 6. 공통 모달 만들기 (VideoModalFrame)](#step-6-공통-모달-만들기-videomodalframe)
7. [Step 7. F03 공식 예고편 모달](#step-7-f03-공식-예고편-모달)
8. [Step 8. F04 리뷰 영상 검색](#step-8-f04-리뷰-영상-검색)
9. [Step 9. F05 Django API 서버 만들기](#step-9-f05-django-api-서버-만들기)
10. [Step 10. F05 프론트에서 데이터 출처 전환하기](#step-10-f05-프론트에서-데이터-출처-전환하기)
11. [Step 11. F06 날씨 기반 영화 추천](#step-11-f06-날씨-기반-영화-추천)
12. [Step 12. 스타일링 & 마무리 점검](#step-12-스타일링--마무리-점검)
13. [복습 체크리스트 & 셀프 퀴즈](#복습-체크리스트--셀프-퀴즈)

---

## 0. 전체 그림 먼저 보기

### 0-1. 구조 한 장 요약

```
                ┌─────────────────────── 브라우저 (Vue SPA, :5173) ───────────────────────┐
                │                                                                         │
 URL 변경  ───▶ │  router/index.js ──▶ views/*View.vue  ──(props)──▶ components/*.vue      │
                │                          │                                              │
                │                          ▼  (뷰는 api/ 폴더의 함수만 호출)                  │
                │       api/movies.js  (데이터 출처 전환 레이어)                              │
                │         ├─ api/tmdb.js    ──▶ TMDB API                                  │
                │         └─ api/django.js  ──▶ Django 서버 (:8000) ──▶ SQLite             │
                │       api/youtube.js      ──▶ Youtube Data API                          │
                │       api/weather.js      ──▶ Open-Meteo API                            │
                └─────────────────────────────────────────────────────────────────────────┘
```

### 0-2. 폴더별 책임 (이 프로젝트의 설계 원칙)

| 폴더 | 책임 | 하지 않는 일 |
| :--- | :--- | :--- |
| `router/` | URL ↔ 화면(View) 연결 | 데이터 요청 |
| `views/` | **페이지 단위**. 데이터를 요청하고 로딩/에러 상태 관리 | HTTP 세부사항(URL, 인증) 알기 |
| `components/` | **재사용 UI 조각**. props로 받은 데이터를 그리기만 함 | 직접 API 호출 (예고편 모달은 예외 — Step 7 참고) |
| `api/` | 외부 서버와 통신. 인증, baseURL, 응답 가공 | 화면 그리기 |
| `utils/` | 순수 함수 (입력 → 출력) | 상태 보관 |

> 💡 **핵심 아이디어**: "누가 무엇을 아는가"를 나누면, 나중에 TMDB → Django로 바꿀 때 `api/` 폴더만 고치면 됩니다. (Step 10에서 실제로 증명합니다.)

---

## Step 1. Vue 프로젝트 생성과 진입점 (`main.js`)

### 🎯 목표
Vite 기반 Vue 3 프로젝트를 만들고, 라이브러리(Bootstrap, Router, Pinia)를 앱에 연결한다.

### 따라하기
```bash
npm create vue@latest my-vue-pjt   # Router, Pinia 선택
cd my-vue-pjt
npm install
npm install axios bootstrap
```

### 코드 — `my-vue-pjt/src/main.js`
```js
import 'bootstrap/dist/css/bootstrap.min.css'   // ① CSS는 가장 먼저 (뒤에 오는 main.css가 덮어쓸 수 있도록)
import './assets/main.css'

import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

const app = createApp(App)   // ② 루트 컴포넌트로 앱 인스턴스 생성
app.use(createPinia())       // ③ 플러그인 등록
app.use(router)
app.mount('#app')            // ④ index.html 의 <div id="app"> 에 마운트
```

### 🤔 왜 이렇게 했나
- **CSS import 순서가 중요합니다.** 나중에 import한 CSS가 우선순위가 같을 때 이깁니다. Bootstrap을 먼저, 커스텀 `main.css`를 나중에 둬야 커스텀 스타일이 적용됩니다.
- Bootstrap은 **CSS만** 가져왔습니다. 모달을 Bootstrap JS 대신 Vue로 직접 제어하기 때문입니다 (Step 6).
- `@/` 경로 별칭은 `vite.config.js`의 `resolve.alias`에 `@ → ./src`로 설정되어 있어 `../../` 지옥을 피할 수 있습니다.

### 🔐 환경 변수 (`.env`)
```env
VITE_TMDB_API_KEY=...
VITE_YOUTUBE_API_KEY=...
VITE_MOVIE_API_SOURCE=tmdb          # 또는 django
VITE_DJANGO_API_URL=http://127.0.0.1:8000/api/v1
```
- Vite는 **`VITE_` 접두사가 붙은 변수만** `import.meta.env.XXX`로 노출합니다.
- `.env`는 `.gitignore`에 넣고, 대신 값이 비어있는 `.env.example`을 커밋해서 팀원이 어떤 키가 필요한지 알게 합니다.
- ⚠️ 주의: `VITE_` 변수는 **빌드 결과물 JS에 그대로 박힙니다.** 즉 브라우저에서 누구나 볼 수 있습니다. 학습용으로는 괜찮지만, 실서비스에서는 키를 백엔드에 숨겨야 합니다. (F05가 그 방향의 첫걸음입니다.)

### ✍️ 직접 해보기
- `console.log(import.meta.env)`를 찍어보고, `VITE_` 없는 변수를 `.env`에 추가하면 보이는지 확인해 보세요.

---

## Step 2. 라우터와 네비게이션 바

### 🎯 목표
URL에 따라 다른 페이지(View)가 보이도록 하고, 상단 메뉴로 이동할 수 있게 한다.

### 코드 — `src/router/index.js`
```js
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
```

### 핵심 개념
| 개념 | 설명 |
| :--- | :--- |
| `createWebHistory` | `/#/movies` 같은 해시 없이 깔끔한 URL 사용 (HTML5 History API) |
| `name` | 경로 문자열 대신 이름으로 이동 → 경로가 바뀌어도 링크 코드 수정 불필요 |
| `:movieId` | **동적 세그먼트**. `/278` 에서 `278`이 `route.params.movieId`로 들어옴 |
| `(\\d+)` | 동적 세그먼트에 **정규식 제약**. 숫자만 매칭 |
| `scrollBehavior` | 페이지 이동 시 스크롤을 맨 위로 |

### 🐛 트러블슈팅: 동적 라우트 충돌
명세서대로 `/:movieId`만 쓰면 `/movies`도 "movieId = 'movies'"로 해석될 *수* 있습니다. Vue Router 4는 정적 경로에 우선순위를 주긴 하지만, `/abc`처럼 오타 URL도 상세 페이지로 가서 API 404를 부릅니다. `(\\d+)`로 **"숫자일 때만 상세 페이지"** 라고 명확히 해두면 의도가 코드에 드러납니다.
(JS 문자열 안이라 `\d`를 `\\d`로 이스케이프한 것에 주의!)

### 코드 — `src/App.vue` (요약)
```vue
<RouterLink class="nav-link" :to="{ name: 'home' }" exact-active-class="active">Home</RouterLink>
<RouterLink class="nav-link" :to="{ name: 'movies' }" active-class="active">Movies</RouterLink>
...
<main class="container py-4">
  <RouterView />   <!-- 현재 URL에 매칭된 View가 여기에 그려짐 -->
</main>
```
- `RouterLink`는 `<a>` 태그를 만들지만 **페이지 새로고침 없이** 이동합니다 (SPA의 핵심).
- `active-class` vs `exact-active-class`: `/`는 모든 경로의 접두사라서 `active-class`를 쓰면 Home이 항상 활성화돼 보입니다. 그래서 Home에만 `exact-active-class`를 사용했습니다.

### ✍️ 직접 해보기
- `(\\d+)`를 지우고 `/hello`로 접속해 보세요. 무슨 일이 일어나나요?
- 존재하지 않는 경로를 위한 404 페이지 라우트(`/:pathMatch(.*)*`)를 추가해 보세요.

---

## Step 3. API 레이어 분리 — axios 인스턴스 만들기

### 🎯 목표
컴포넌트 안에 `axios.get('https://api.themoviedb.org/3/...?api_key=...')`를 매번 쓰지 않도록, **외부 API마다 파일 하나**를 만든다.

### 코드 — `src/api/tmdb.js`
```js
const TMDB_API_KEY = import.meta.env.VITE_TMDB_API_KEY
export const TMDB_IMAGE_URL = 'https://image.tmdb.org/t/p'

// v4 Read Access Token(JWT, "eyJ"로 시작)이면 Bearer 헤더, v3 API Key면 api_key 쿼리로 인증
const isBearerToken = TMDB_API_KEY?.startsWith('eyJ')

const tmdb = axios.create({
  baseURL: 'https://api.themoviedb.org/3',
  headers: isBearerToken ? { Authorization: `Bearer ${TMDB_API_KEY}` } : {},
  params: {
    language: 'ko-KR',
    ...(isBearerToken ? {} : { api_key: TMDB_API_KEY }),
  },
})

export async function fetchTopRated(page = 1) {
  const { data } = await tmdb.get('/movie/top_rated', { params: { page } })
  return data.results          // ← 뷰가 쓰기 좋은 형태(배열)로 가공해서 반환
}
```

### 핵심 개념
- **`axios.create()`**: 공통 설정(baseURL, 헤더, 기본 쿼리)을 가진 "전용 axios"를 만듭니다. 이후 `tmdb.get('/movie/top_rated')`처럼 경로만 쓰면 됩니다.
- 인스턴스의 `params`와 요청별 `params`는 **합쳐집니다**. 그래서 `language`, `api_key`는 매번 자동으로 붙습니다.
- **스프레드 + 삼항 연산자 패턴** `...(조건 ? {} : { key: value })` 은 "조건에 따라 속성을 넣거나 빼는" JS 관용구입니다.
- 함수가 `data.results`만 반환하므로 뷰는 TMDB 응답 구조(`{ page, results, total_pages }`)를 몰라도 됩니다.

### 🤔 왜 TMDB 인증을 두 방식 다 지원했나
TMDB는 v3 API Key(짧은 문자열)와 v4 Read Access Token(긴 JWT, `eyJ`로 시작) 두 가지를 발급합니다. JWT는 항상 base64 인코딩된 `{"` 로 시작하므로 `eyJ`가 됩니다. 이걸 이용해 어떤 키를 넣어도 동작하게 했습니다.

### `src/api/youtube.js`도 같은 패턴
```js
const youtube = axios.create({
  baseURL: 'https://www.googleapis.com/youtube/v3',
  params: { key: import.meta.env.VITE_YOUTUBE_API_KEY, part: 'snippet', type: 'video' },
})

export async function searchVideos(query, maxResults = 12) {
  const { data } = await youtube.get('/search', { params: { q: query, maxResults } })
  return data.items
}

export function getEmbedUrl(videoId) {
  return `https://www.youtube.com/embed/${videoId}?autoplay=1`
}
```
- `type: 'video'`를 넣어야 채널/재생목록이 검색 결과에 섞이지 않습니다 (재생목록은 `videoId`가 없어서 에러 원인이 됨).
- URL을 만드는 로직(`getEmbedUrl`)도 API 파일에 둬서 컴포넌트에는 문자열 조립이 없게 했습니다.

### ✍️ 직접 해보기
- 브라우저 개발자도구 **Network 탭**에서 실제 요청 URL을 열어 `language=ko-KR&api_key=...`가 자동으로 붙었는지 확인해 보세요.

---

## Step 4. F01 최고 평점 영화 목록

### 🎯 목표
`/movies` 진입 시 TMDB Top Rated 목록을 받아와 카드 그리드로 보여준다.

### 데이터 흐름
```
MovieListView 마운트
  → onMounted 에서 getTopRatedMovies() 호출
  → movies.value = [...20편]
  → v-for 로 MovieCard 에 :movie="movie" (props) 전달
  → MovieCard 가 포스터/제목/평점/줄거리 렌더링
```

### 코드 — `src/views/MovieListView.vue`
```vue
<template>
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
const movies = ref([])
const isLoading = ref(true)
const errorMessage = ref('')

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
```

### 핵심 개념 ① — 비동기 요청의 "3가지 상태" 패턴
이 프로젝트의 **모든 뷰**가 이 패턴을 씁니다. 한 번 익혀두면 계속 재사용할 수 있어요.

| 상태 | 변수 | 화면 |
| :--- | :--- | :--- |
| 로딩 중 | `isLoading = true` | 스피너 |
| 실패 | `errorMessage = '...'` | 빨간 알림 |
| 성공 | `movies = [...]` | 실제 콘텐츠 |

- `try / catch / finally`: `finally`는 성공·실패 **모두** 실행되므로 `isLoading = false`를 여기에 두면 빠뜨릴 일이 없습니다.
- 템플릿에서는 `v-if → v-else-if → v-else` 체인으로 **딱 하나만** 보이게 합니다.

### 핵심 개념 ② — `:key`
`v-for`에는 항상 고유한 `:key`를 줍니다. Vue가 리스트가 바뀔 때 어떤 DOM을 재사용할지 판단하는 기준입니다. 배열 인덱스 대신 `movie.id`처럼 **데이터 고유값**을 쓰세요.

### 코드 — `src/components/MovieCard.vue`
```vue
<template>
  <RouterLink :to="{ name: 'movieDetail', params: { movieId: movie.id } }" class="text-decoration-none text-reset">
    <div class="card h-100 border-0 shadow-sm hover-lift">
      <img :src="getPosterUrl(movie.poster_path)" class="card-img-top" :alt="movie.title" loading="lazy" />
      <div class="card-body">
        <h6 class="card-title fw-bold mb-0">{{ movie.title }}</h6>
        <span class="badge text-bg-warning">★ {{ movie.vote_average?.toFixed(1) }}</span>
        <p class="card-text small text-secondary text-clamp-3 mb-0">
          {{ movie.overview || '줄거리 정보가 없습니다.' }}
        </p>
      </div>
    </div>
  </RouterLink>
</template>

<script setup>
defineProps({
  movie: { type: Object, required: true },
})
</script>
```
- **props는 부모 → 자식 단방향**입니다. 카드는 받은 데이터를 그리기만 하고 수정하지 않습니다.
- 카드 전체를 `RouterLink`로 감싸서 어디를 클릭해도 상세 페이지(F02)로 이동합니다.
- `?.` (옵셔널 체이닝): `vote_average`가 없을 때 `toFixed` 호출로 앱이 터지는 것을 방지.
- `loading="lazy"`: 화면에 보일 때 이미지를 로드 → 첫 로딩 속도 개선.
- `getPosterUrl`은 TMDB가 `poster_path`로 `/abc.jpg`만 주기 때문에 `https://image.tmdb.org/t/p/w500/abc.jpg`로 조립하고, 포스터가 없으면 placeholder를 반환합니다.

### ✍️ 직접 해보기
- `.env`의 TMDB 키를 일부러 틀리게 바꾸고 에러 메시지가 뜨는지 확인해 보세요.
- "더 보기" 버튼으로 2페이지를 이어 붙여 보세요. (`fetchTopRated(page)`는 이미 page 인자를 받습니다.)

---

## Step 5. F02 영화 상세 정보

### 🎯 목표
`/278` 같은 URL로 들어오면 해당 영화의 상세 정보를 보여준다.

### 코드 — `src/views/MovieDetailView.vue` (스크립트)
```js
const route = useRoute()    // 현재 URL 정보 (읽기용)
const router = useRouter()  // 이동 기능 (router.back(), router.push())

const movie = ref(null)
const isLoading = ref(true)
const errorMessage = ref('')
const isTrailerOpen = ref(false)

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
```

### 🐛 트러블슈팅: 왜 `onMounted`가 아니라 `watch`인가?
처음엔 F01처럼 `onMounted`로 요청했다고 해봅시다.

1. `/278` 진입 → `MovieDetailView` 생성 → `onMounted` 실행 ✅
2. 같은 페이지 안에서 `/238`로 이동 (예: 추천 영화 클릭, 브라우저 뒤로가기)
3. **같은 컴포넌트를 재사용**하므로 새로 만들어지지 않음 → `onMounted` 다시 실행 안 됨 ❌
4. URL은 `/238`인데 화면은 여전히 278번 영화

해결: URL 파라미터를 **감시(watch)** 합니다.
- `() => route.params.movieId` — 감시 대상을 **getter 함수**로 넘깁니다. (`route.params.movieId`를 바로 넘기면 그 순간의 문자열 값만 전달되어 반응성이 끊김)
- `{ immediate: true }` — 값이 바뀔 때뿐 아니라 **처음 한 번도 즉시 실행** → `onMounted` 역할까지 겸함.

### 코드 — `src/components/MovieDetailInfo.vue` (요약)
```vue
<span v-for="genre in movie.genres" :key="genre.id" class="badge rounded-pill text-bg-primary me-1">
  {{ genre.name }}
</span>
...
<slot />   <!-- 부모가 넣어준 내용(예고편 버튼)이 여기에 들어감 -->
```
그리고 부모(`MovieDetailView`)에서:
```vue
<MovieDetailInfo v-else :movie="movie">
  <button class="btn btn-danger btn-lg mt-2" @click="isTrailerOpen = true">▶ 공식 예고편</button>
</MovieDetailInfo>
```

### 핵심 개념 — `slot`
`MovieDetailInfo`는 "정보 표시"만 책임지고, 예고편 버튼은 **부모가 주입**합니다. 덕분에:
- 정보 컴포넌트는 예고편 모달의 존재를 몰라도 됨
- 버튼 클릭 상태(`isTrailerOpen`)는 부모가 관리 → 모달도 부모가 띄움

props가 "데이터"를 내려준다면, slot은 "마크업(화면 조각)"을 내려준다고 생각하면 됩니다.

### ✍️ 직접 해보기
- `watch`를 `onMounted`로 바꾸고, 주소창에서 숫자만 바꿔 이동했을 때(혹은 F06 추천 카드에서 이동 후 뒤로가기) 버그를 재현해 보세요.

---

## Step 6. 공통 모달 만들기 (`VideoModalFrame`)

### 🎯 목표
F03(예고편)과 F04(리뷰) 둘 다 "영상 모달"이 필요하다. **겉 틀은 하나만** 만들고 내용만 바꿔 끼운다.

### 코드 — `src/components/VideoModalFrame.vue`
```vue
<template>
  <Teleport to="body">
    <div class="modal d-block" tabindex="-1" @click.self="emit('close')">
      <div class="modal-dialog modal-xl modal-dialog-centered">
        <div class="modal-content bg-dark text-white">
          <div class="modal-header border-secondary">
            <h5 class="modal-title text-truncate">{{ title }}</h5>
            <button type="button" class="btn-close btn-close-white" @click="emit('close')"></button>
          </div>
          <div class="modal-body p-0">
            <slot />
          </div>
        </div>
      </div>
    </div>
    <div class="modal-backdrop show"></div>
  </Teleport>
</template>

<script setup>
defineProps({ title: { type: String, default: '' } })
const emit = defineEmits(['close'])

const onKeydown = (event) => {
  if (event.key === 'Escape') emit('close')
}

onMounted(() => {
  document.body.classList.add('modal-open')        // 배경 스크롤 막기
  window.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  document.body.classList.remove('modal-open')
  window.removeEventListener('keydown', onKeydown) // 꼭 정리!
})
</script>
```

### 핵심 개념 4가지

**① `Teleport to="body"`**
모달을 컴포넌트 트리 위치가 아니라 `<body>` 바로 아래에 렌더링합니다. 부모에 `overflow: hidden`이나 `z-index`, `transform`이 있으면 모달이 잘리거나 뒤로 숨는 문제가 생기는데, 이를 원천 차단합니다.

**② `emit` — 자식 → 부모 통신**
모달은 스스로 사라질 수 없습니다(자신을 보여줄지 말지는 부모의 `v-if`가 결정). 그래서 "닫아줘"라는 **이벤트만 올려보내고**, 부모가 상태를 바꿉니다.
```
props  : 부모 ──데이터──▶ 자식
emit   : 부모 ◀──이벤트── 자식
```

**③ `@click.self`**
이벤트 수식어 `.self`는 "클릭된 요소가 **바로 그 요소 자신**일 때만" 실행합니다. 어두운 배경 클릭 → 닫힘, 영상(자식 요소) 클릭 → 안 닫힘.

**④ 이벤트 리스너는 반드시 정리**
`window`에 붙인 리스너는 컴포넌트가 사라져도 남습니다. `onUnmounted`에서 `removeEventListener`를 안 하면 모달을 열 때마다 리스너가 쌓이는 **메모리 누수**가 생깁니다. 그래서 익명 함수가 아닌 `onKeydown` 변수로 같은 함수 참조를 넘겨야 합니다.

### 🐛 트러블슈팅: 모달을 닫아도 소리가 계속 난다
Bootstrap 모달처럼 CSS(`display: none`)로 숨기면 iframe은 **살아있어서** 유튜브가 계속 재생됩니다.
→ 부모에서 모달을 **`v-if`** 로 렌더링해서, 닫으면 iframe이 DOM에서 아예 제거되도록 했습니다. (`v-show`였다면 같은 문제가 발생합니다.)
→ 부수 효과로, 열 때마다 컴포넌트가 새로 생성되므로 `onMounted`/`onUnmounted`가 정확히 열기/닫기 타이밍에 맞춰 실행됩니다.

### ✍️ 직접 해보기
- 부모의 `v-if`를 `v-show`로 바꿔서 소리 버그를 재현해 보세요.
- `onUnmounted`의 `removeEventListener`를 지우고, 모달을 3번 열고 닫은 뒤 ESC를 눌렀을 때 `close`가 몇 번 emit되는지 Vue DevTools로 확인해 보세요.

---

## Step 7. F03 공식 예고편 모달

### 🎯 목표
상세 페이지에서 **[공식 예고편]** 버튼을 누르면 `"영화제목 trailer"`로 유튜브를 검색하고 첫 번째 영상을 모달에서 재생한다.

### 코드 — 부모 (`MovieDetailView.vue`)
```vue
<YoutubeTrailerModal
  v-if="isTrailerOpen"
  :movie-title="movie.original_title || movie.title"
  @close="isTrailerOpen = false"
/>
```

### 코드 — `src/components/YoutubeTrailerModal.vue`
```vue
<template>
  <VideoModalFrame :title="`${movieTitle} 공식 예고편`" @close="emit('close')">
    <div v-if="isLoading" class="text-center py-5"><div class="spinner-border text-light"></div></div>
    <p v-else-if="errorMessage" class="p-4 mb-0 text-warning">{{ errorMessage }}</p>
    <div v-else class="ratio ratio-16x9">
      <iframe :src="getEmbedUrl(videoId)" allow="autoplay; encrypted-media; picture-in-picture" allowfullscreen></iframe>
    </div>
  </VideoModalFrame>
</template>

<script setup>
const props = defineProps({ movieTitle: { type: String, required: true } })
const emit = defineEmits(['close'])

const videoId = ref(null)
const isLoading = ref(true)
const errorMessage = ref('')

onMounted(async () => {
  try {
    const [firstVideo] = await searchVideos(`${props.movieTitle} trailer`, 1)
    if (!firstVideo) {
      errorMessage.value = '예고편을 찾을 수 없습니다.'
      return
    }
    videoId.value = firstVideo.id.videoId
  } catch (error) {
    errorMessage.value = '예고편을 불러오지 못했습니다. Youtube API Key를 확인해주세요.'
  } finally {
    isLoading.value = false
  }
})
</script>
```

### 🤔 왜 이렇게 했나
- **`original_title` 우선 사용**: `language=ko-KR` 때문에 `title`은 한국어("쇼생크 탈출")입니다. 공식 예고편은 원제("The Shawshank Redemption trailer")로 검색해야 훨씬 정확합니다.
- **`maxResults = 1`**: 첫 번째 결과만 쓰므로 1개만 요청 → Youtube API 할당량 절약 (search는 요청당 100 unit 소모, 하루 10,000 unit 제한).
- **배열 구조 분해** `const [firstVideo] = ...` 로 첫 원소만 꺼냅니다. 결과가 빈 배열이면 `undefined` → "찾을 수 없음" 처리.
- **`onMounted`에서 요청해도 되는 이유**: 부모의 `v-if` 덕분에 모달을 열 때마다 새로 생성되기 때문 (Step 6의 부수 효과).
- **컴포넌트가 직접 API를 부르는 예외**: 모달은 열릴 때만 데이터가 필요하고 다른 곳에서 결과를 공유하지 않으므로, 부모가 미리 요청하는 것보다 응집도가 높습니다.
- **`ratio ratio-16x9`**: Bootstrap 유틸리티로 iframe을 16:9 비율로 반응형 유지.
- **props 이름 표기법**: 템플릿에서는 `:movie-title`, 스크립트에서는 `movieTitle` — Vue가 자동 변환합니다.

---

## Step 8. F04 리뷰 영상 검색

### 🎯 목표
검색어를 입력하면 `"검색어 review"`로 유튜브를 검색해 카드 목록을 보여주고, 카드를 누르면 모달로 재생한다.

### 컴포넌트 관계
```
ReviewSearchView  (상태: keyword, videos, selectedVideo)
 ├─ YoutubeCard × N        ── emit('select', video) ──▶ selectedVideo = video
 └─ YoutubeReviewModal     (v-if="selectedVideo")  ── emit('close') ──▶ selectedVideo = null
      └─ VideoModalFrame   (Step 6의 공통 틀 재사용)
```

### 코드 — `src/views/ReviewSearchView.vue` (핵심)
```vue
<form class="input-group input-group-lg mb-4" @submit.prevent="onSearch">
  <input v-model.trim="keyword" type="text" class="form-control" placeholder="영화 제목을 입력하세요" />
  <button class="btn btn-dark" type="submit" :disabled="!keyword || isLoading">검색</button>
</form>
...
<p v-else-if="!searchedKeyword">영화 제목을 검색하면 Youtube 리뷰 영상을 찾아드려요.</p>
<p v-else-if="!videos.length">"{{ searchedKeyword }}" 에 대한 리뷰 영상이 없습니다.</p>
<template v-else>
  <div v-for="video in videos" :key="video.id.videoId" class="col">
    <YoutubeCard :video="video" @select="selectedVideo = $event" />
  </div>
</template>

<YoutubeReviewModal v-if="selectedVideo" :video="selectedVideo" @close="selectedVideo = null" />
```
```js
const keyword = ref('')          // 입력창과 양방향 바인딩 (타이핑할 때마다 변함)
const searchedKeyword = ref('')  // 실제로 검색을 실행한 단어 (검색 버튼 누를 때만 변함)

const onSearch = async () => {
  if (!keyword.value) return
  isLoading.value = true
  errorMessage.value = ''
  try {
    videos.value = await searchVideos(`${keyword.value} review`)
    searchedKeyword.value = keyword.value
  } catch (error) { ... } finally { isLoading.value = false }
}
```

### 핵심 개념
| 문법 | 의미 |
| :--- | :--- |
| `<form @submit.prevent>` | 버튼 클릭과 **Enter 키** 둘 다 처리 + 페이지 새로고침(기본 동작) 방지 |
| `v-model.trim` | 입력값 앞뒤 공백 자동 제거 → `"   "`만 입력하면 빈 문자열 → 버튼 비활성화 |
| `:disabled="!keyword \|\| isLoading"` | 빈 검색, 중복 클릭 방지 |
| `$event` | 템플릿 인라인 핸들러에서 emit이 보낸 값 (여기선 `video`) |

### 🤔 왜 `keyword`와 `searchedKeyword`를 나눴나
하나만 쓰면, "어벤져스" 검색 후 입력창에 "타이타닉"을 **타이핑만 해도** 결과 위 문구가 `"타이타닉 review 검색 결과"`로 바뀝니다. 입력 중인 값과 확정된 값은 **다른 상태**입니다. 또 `searchedKeyword`가 비어있는지로 "아직 검색 전" / "검색했는데 결과 0개"를 구분할 수 있습니다 — 빈 화면도 상황별로 다르게 안내하는 것이 좋은 UX입니다.

### 🐛 트러블슈팅: 제목에 `&#39;`, `&quot;`가 보인다
Youtube API의 `snippet.title`은 `Marvel&#39;s Avengers`처럼 **HTML 엔티티로 인코딩**되어 옵니다.

- ❌ `v-html="title"` — 동작은 하지만, 제목에 `<img onerror=...>` 같은 스크립트가 섞여 있으면 그대로 실행됩니다 (**XSS 취약점**).
- ✅ `utils/decodeHtml.js`:
  ```js
  export function decodeHtml(text = '') {
    return new DOMParser().parseFromString(text, 'text/html').documentElement.textContent
  }
  ```
  `DOMParser`는 문자열을 **실행하지 않고** 파싱만 합니다. 거기서 `textContent`(순수 텍스트)만 꺼내 `{{ }}`로 출력하면 안전합니다.

### `YoutubeCard.vue`의 `computed`
```js
const props = defineProps({ video: { type: Object, required: true } })
const emit = defineEmits(['select'])

const snippet = computed(() => props.video.snippet)
const title = computed(() => decodeHtml(snippet.value.title))
```
- 템플릿에서 `video.snippet.thumbnails...`처럼 길게 쓰지 않도록 `computed`로 별칭을 만들었습니다.
- `computed`는 **캐싱**됩니다. 의존 값이 안 바뀌면 `decodeHtml`을 다시 실행하지 않습니다.
- 썸네일은 `thumbnails.high?.url ?? thumbnails.default.url` — 고화질이 없으면 기본 화질로 대체(`??` 널 병합 연산자).

### ✍️ 직접 해보기
- `decodeHtml`을 빼고 `"I'm"`이 들어간 영화를 검색해 보세요.
- 검색 결과에 "다음 페이지" 기능을 추가해 보세요. (힌트: 응답의 `nextPageToken`을 `pageToken` 파라미터로 전달)

---

## Step 9. F05 Django API 서버 만들기

### 🎯 목표
TMDB를 직접 부르는 대신, **우리 Django 서버**가 DB에 저장한 영화 데이터를 내려준다.

### 9-1. 전체 흐름
```
[1회] python manage.py load_tmdb  ──▶ TMDB API ──▶ SQLite (Genre, Movie 테이블)
[매번] Vue ──▶ GET /api/v1/movies/ ──▶ Django View ──▶ ORM ──▶ Serializer ──▶ JSON
```

### 9-2. 모델 — `movies/models.py`
```python
class Genre(models.Model):
    id = models.IntegerField(primary_key=True)   # TMDB 장르 ID를 그대로 PK로 사용
    name = models.CharField(max_length=50)

class Movie(models.Model):
    id = models.IntegerField(primary_key=True)   # TMDB 영화 ID를 그대로 PK로 사용
    title = models.CharField(max_length=200)
    original_title = models.CharField(max_length=200, blank=True)
    overview = models.TextField(blank=True)
    poster_path = models.CharField(max_length=200, blank=True)
    release_date = models.DateField(null=True, blank=True)
    vote_average = models.FloatField(default=0)
    vote_count = models.IntegerField(default=0)
    popularity = models.FloatField(default=0)
    genres = models.ManyToManyField(Genre, related_name='movies')
```

**🤔 왜 PK를 TMDB ID로 했나?**
자동 증가 PK(1, 2, 3...)를 쓰면 DB의 `id=1`과 TMDB의 `id=278`이 달라집니다. 그러면 프론트의 `/:movieId` URL이 출처에 따라 다른 영화를 가리키게 됩니다. TMDB ID를 PK로 쓰면 **`/278`은 TMDB 모드든 Django 모드든 항상 쇼생크 탈출**입니다. 또 `update_or_create(id=...)`로 재실행해도 중복 없이 갱신됩니다.

**ManyToMany**: 영화 하나는 장르 여러 개, 장르 하나는 영화 여러 개 → 중간 테이블이 자동 생성됩니다. `related_name='movies'` 덕에 `genre.movies.all()`로 역참조가 가능합니다.

### 9-3. 데이터 적재 — 커스텀 관리 명령어 `load_tmdb`
`movies/management/commands/load_tmdb.py` 파일을 만들면 `python manage.py load_tmdb`라는 명령어가 생깁니다. (폴더마다 `__init__.py` 필요)

```python
def handle(self, *args, **options):
    # 1) 장르 저장
    genres = self.get('/genre/movie/list')['genres']
    for genre in genres:
        Genre.objects.update_or_create(id=genre['id'], defaults={'name': genre['name']})

    # 2) top_rated 여러 페이지 저장
    for page in range(1, options['pages'] + 1):
        saved += self.save_movies(self.get('/movie/top_rated', page=page)['results'])

    # 3) 날씨 추천(F06)에서 모든 장르가 후보를 갖도록 장르별 평점 상위 영화도 수집
    for genre in genres:
        results = self.get('/discover/movie', with_genres=genre['id'], ...)['results']
        saved += self.save_movies(results)

def save_movies(self, results):
    for data in results:
        movie, _ = Movie.objects.update_or_create(id=data['id'], defaults={...})
        movie.genres.set(data.get('genre_ids', []))   # M2M 관계는 저장 후 set()
```
- **`update_or_create`**: 있으면 수정, 없으면 생성 → 몇 번을 실행해도 안전 (**멱등성**).
- **M2M은 객체가 먼저 저장된 뒤에** `.set()` 할 수 있습니다 (중간 테이블에 movie의 PK가 필요하므로).
- `genre_ids`가 `[27, 53]` 같은 ID 배열이라 Genre 객체를 조회할 필요 없이 바로 `set()`에 넘길 수 있습니다 — 장르 PK를 TMDB ID로 맞춘 또 하나의 이점.
- 3번 단계가 왜 필요한가? top_rated에는 드라마/범죄가 대부분이라 "공포" 영화가 거의 없습니다. 비 오는 날 공포 영화를 추천하려면 장르별로 따로 채워둬야 합니다.
- API 키는 `settings.TMDB_API_KEY = os.environ.get('TMDB_API_KEY', '')`로 **환경 변수**에서 읽습니다 (코드에 키를 쓰지 않음).

### 9-4. Serializer — `movies/serializers.py`
```python
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('id', 'name')

# 목록용: MovieCard 에 필요한 필드만
class MovieListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ('id', 'title', 'overview', 'poster_path', 'vote_average')

# 상세용: genres 를 [{id, name}] 로 중첩 (TMDB 응답과 같은 모양)
class MovieSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    class Meta:
        model = Movie
        fields = '__all__'
```
- 기본 ModelSerializer는 M2M을 `"genres": [27, 53]` (ID 배열)로 내보냅니다. 그런데 프론트 `MovieDetailInfo`는 `genre.name`을 출력하므로 **TMDB처럼 `[{id, name}]`** 이어야 합니다. → 중첩 Serializer로 해결.
- 목록/상세 Serializer를 나눈 이유: 목록에서는 20편 × 필요한 필드만 보내 응답을 가볍게.
- **필드명을 TMDB와 똑같이** (`poster_path`, `vote_average`) 맞춘 것이 Step 10의 핵심 전제입니다.

### 9-5. View & URL — `movies/views.py`, `movies/urls.py`
```python
@api_view(['GET'])
def movie_list(request):
    movies = Movie.objects.order_by('-vote_average', '-vote_count')[:20]
    return Response(MovieListSerializer(movies, many=True).data)

@api_view(['GET'])
def movie_detail(request, movie_pk):
    movie = get_object_or_404(Movie.objects.prefetch_related('genres'), pk=movie_pk)
    return Response(MovieSerializer(movie).data)
```
```python
urlpatterns = [
    path('movies/', views.movie_list),
    path('movies/recommend/', views.movie_recommend),   # ← <int:movie_pk> 보다 위!
    path('movies/<int:movie_pk>/', views.movie_detail),
    path('genres/', views.genre_list),
]
```
- `@api_view(['GET'])`: DRF 함수형 뷰. 허용 안 된 메서드는 자동으로 405 응답.
- `get_object_or_404`: 없는 ID면 500 에러 대신 **404** 응답.
- `prefetch_related('genres')`: 장르를 별도 쿼리 1번으로 미리 가져와 **N+1 쿼리 문제** 방지.
- `[:20]`: QuerySet 슬라이싱 → SQL의 `LIMIT 20`으로 변환 (전부 가져와서 자르는 게 아님).
- URL 순서: 여기선 `<int:...>`라 `recommend`와 충돌하진 않지만, 정적 경로를 동적 경로보다 위에 두는 습관이 안전합니다 (Step 2의 Vue 라우터와 같은 원리!).

### 9-6. CORS 설정 — `my_api/settings.py`
```python
INSTALLED_APPS = [..., 'rest_framework', 'corsheaders', 'movies']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',          # ← CommonMiddleware 보다 위
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = ['http://localhost:5173', 'http://127.0.0.1:5173']
```
- **출처(Origin) = 프로토콜 + 도메인 + 포트**. `localhost:5173`(Vite)과 `127.0.0.1:8000`(Django)은 포트가 달라 **다른 출처**입니다.
- 브라우저는 다른 출처의 응답을 기본적으로 막습니다 (Same-Origin Policy). 서버가 `Access-Control-Allow-Origin` 헤더로 "이 출처는 허용"이라고 알려줘야 합니다.
- `CorsMiddleware`가 위에 있어야 하는 이유: `CommonMiddleware`가 먼저 리다이렉트 응답(예: 끝 슬래시 추가) 등을 만들어버리면 CORS 헤더가 안 붙습니다.
- ⚠️ CORS는 **브라우저**의 보안 정책입니다. Postman이나 `curl`로는 CORS 설정 없이도 잘 되기 때문에 "Postman에선 되는데 Vue에선 안 돼요"의 단골 원인입니다.

### 9-7. 테스트 — `movies/tests.py`
```python
class MovieApiTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        horror = Genre.objects.create(id=27, name='공포')
        drama = Genre.objects.create(id=18, name='드라마')
        Movie.objects.create(id=1, title='A', vote_average=8.0).genres.set([horror])
        Movie.objects.create(id=2, title='B', vote_average=9.0).genres.set([drama])
        Movie.objects.create(id=3, title='C', vote_average=7.0).genres.set([horror, drama])

    def test_movie_list_is_sorted_by_vote_average(self):
        response = self.client.get('/api/v1/movies/')
        self.assertEqual([m['id'] for m in response.data], [2, 1, 3])
```
- 테스트는 **별도의 빈 테스트 DB**에서 실행되므로 실제 `db.sqlite3`가 오염되지 않습니다.
- `setUpTestData`는 클래스당 1번만 데이터를 만들어 빠릅니다.
- 실행: `python manage.py test movies` → 6개 테스트 통과.

---

## Step 10. F05 프론트에서 데이터 출처 전환하기

### 🎯 목표
뷰/컴포넌트 코드를 **한 줄도 바꾸지 않고**, `.env` 값 하나로 TMDB ↔ Django를 전환한다.

### 코드 — `src/api/django.js`
```js
const django = axios.create({
  baseURL: import.meta.env.VITE_DJANGO_API_URL || 'http://127.0.0.1:8000/api/v1',
})

export async function fetchTopRated() {
  const { data } = await django.get('/movies/')
  return data
}
export async function fetchMovieDetail(movieId) {
  const { data } = await django.get(`/movies/${movieId}/`)   // Django는 끝 슬래시 필수!
  return data
}
```

### 코드 — `src/api/movies.js` (전환 레이어)
```js
import * as tmdb from './tmdb'
import * as django from './django'

export const MOVIE_API_SOURCE = import.meta.env.VITE_MOVIE_API_SOURCE === 'django' ? 'django' : 'tmdb'
const useDjango = MOVIE_API_SOURCE === 'django'

export function getTopRatedMovies() {
  return useDjango ? django.fetchTopRated() : tmdb.fetchTopRated()
}

export function getMovieDetail(movieId) {
  return useDjango ? django.fetchMovieDetail(movieId) : tmdb.fetchMovieDetail(movieId)
}
```

### 🤔 이 구조가 작동하는 이유 (중요!)
```
          뷰는 이것만 앎                 출처별 구현
MovieListView ──▶ getTopRatedMovies() ─┬─▶ tmdb.fetchTopRated()   → [{id, title, poster_path, vote_average, ...}]
                                       └─▶ django.fetchTopRated() → [{id, title, poster_path, vote_average, ...}]
                                                                       ↑ 반환 모양이 같다!
```
두 함수가 **같은 이름의 함수**를 export하고 **같은 모양의 데이터**를 반환하기 때문에, 뷰 입장에서는 어디서 왔는지 구분할 수 없습니다. 이것이 가능했던 3가지 결정:
1. `tmdb.js`가 `data.results`를 꺼내서 배열로 반환 (Django도 배열로 반환)
2. Django Serializer의 필드명을 TMDB와 동일하게 (`poster_path`, `vote_average`)
3. 상세의 `genres`를 중첩 Serializer로 `[{id, name}]` 모양으로

이런 패턴을 **어댑터(Adapter) / 리포지토리(Repository) 패턴**이라고 부릅니다. "인터페이스(약속)를 맞추면 구현을 갈아끼울 수 있다"는 것이 핵심입니다.

### 사용법
```env
VITE_MOVIE_API_SOURCE=django
```
- `.env`를 바꾼 뒤에는 **`npm run dev`를 재시작**해야 반영됩니다.
- 목록 화면 우측 상단 뱃지(`source: django`)로 현재 출처를 확인할 수 있게 해 두었습니다.
- 포스터 이미지는 Django 모드에서도 TMDB 이미지 서버를 씁니다. DB에는 `poster_path`(경로)만 저장했기 때문입니다.

### ✍️ 직접 해보기
- Django 서버를 끈 상태로 `source=django`로 접속해 에러 메시지를 확인하고, Network 탭에서 실패 원인을 보세요.
- `CORS_ALLOWED_ORIGINS`를 주석 처리하고 콘솔에 뜨는 CORS 에러 메시지를 읽어 보세요.

---

## Step 11. F06 날씨 기반 영화 추천

### 🎯 목표
서울의 현재 날씨(WMO 코드)를 가져와 → 어울리는 장르로 매핑하고 → 그 장르에서 영화 1편을 랜덤 추천한다.

### 흐름
```
RecommendedView onMounted
  ① fetchSeoulWeather()        → { temperature: 21.3, weathercode: 61, ... }
  ② matchWeatherGenre(61)      → { label: '비', icon: '🌧️', genre: { id: 27, name: '공포' } }
  ③ getRandomMovieByGenre(27)  → 영화 1편
  ④ MovieCard 로 표시 (F01 컴포넌트 재사용!)
```

### 코드 — `src/api/weather.js`
```js
const SEOUL = { latitude: 37.5665, longitude: 126.978 }

export async function fetchSeoulWeather() {
  const { data } = await axios.get('https://api.open-meteo.com/v1/forecast', {
    params: { ...SEOUL, current_weather: true, timezone: 'Asia/Seoul' },
  })
  return data.current_weather
}

const WEATHER_GENRE_RULES = [
  { codes: [0], label: '맑음', icon: '☀️', genre: { id: 12, name: '모험' } },
  { codes: [1, 2, 3], label: '구름 조금/흐림', icon: '⛅', genre: { id: 35, name: '코미디' } },
  { codes: [61, 63, 65, 66, 67, 80, 81, 82], label: '비', icon: '🌧️', genre: { id: 27, name: '공포' } },
  // ... 안개, 이슬비, 눈, 뇌우
]
const DEFAULT_RULE = { label: '알 수 없음', icon: '🌈', genre: { id: 16, name: '애니메이션' } }

export function matchWeatherGenre(weatherCode) {
  return WEATHER_GENRE_RULES.find((rule) => rule.codes.includes(weatherCode)) ?? DEFAULT_RULE
}
```

### 🤔 왜 이렇게 했나
- **`if / else if` 대신 규칙 배열(데이터)**: 매핑을 코드 로직이 아니라 **데이터 테이블**로 표현했습니다. 규칙 추가/수정이 한 줄이면 되고, 한눈에 읽힙니다. `find`가 첫 번째로 맞는 규칙을 반환합니다.
- **`DEFAULT_RULE`**: 표에 없는 코드가 와도 화면이 깨지지 않도록 항상 기본값을 둡니다 (`??`).
- `matchWeatherGenre`는 **순수 함수**(같은 입력 → 항상 같은 출력, 외부 상태 변경 없음)라 테스트하기 쉽습니다.
- Open-Meteo는 API Key가 필요 없어 `.env`에 아무것도 추가하지 않아도 됩니다.

### 랜덤 추천 — 출처별 구현 (`api/movies.js`)
```js
export async function getRandomMovieByGenre(genreId) {
  if (useDjango) return django.fetchRandomMovieByGenre(genreId)   // 서버가 골라줌

  const movies = await tmdb.fetchMoviesByGenre(genreId)            // 클라이언트가 고름
  if (!movies.length) return null
  return movies[Math.floor(Math.random() * movies.length)]
}
```
- TMDB 모드: `/discover/movie?with_genres=27&vote_count.gte=1000`로 평점 높은 장르 영화 20편을 받고, 랜덤 페이지(1~3) + 랜덤 인덱스로 고릅니다. `vote_count.gte`는 투표 수 적은 무명 영화가 평점 10점으로 상위에 오는 것을 막습니다.
- `Math.floor(Math.random() * n)` → `0 ~ n-1` 범위의 정수. 배열 랜덤 선택의 기본 공식입니다.

### Django 쪽 랜덤 추천 — `movie_recommend` 뷰
```python
@api_view(['GET'])
def movie_recommend(request):
    genre_id = request.query_params.get('genre')
    if not genre_id or not genre_id.isdigit():
        return Response({'detail': 'genre 쿼리 파라미터(정수)가 필요합니다.'}, status=400)

    movies = Movie.objects.filter(genres__id=genre_id)
    total = movies.aggregate(total=Count('id'))['total']
    if total == 0:
        return Response({'detail': '해당 장르의 영화가 없습니다.'}, status=404)

    movie = movies.order_by('id')[random.randrange(total)]
    return Response(MovieListSerializer(movie).data)
```
- **입력 검증**: 쿼리 파라미터는 항상 문자열이고, 사용자가 아무 값이나 보낼 수 있습니다. 없거나 숫자가 아니면 **400 Bad Request**.
- **`genres__id`**: 더블 언더스코어로 M2M 관계를 넘어 필터링 (SQL JOIN 자동 생성).
- **왜 `order_by('?')`를 안 썼나?** `?`는 DB에서 `ORDER BY RANDOM()` → 모든 행에 난수를 매기고 **전체 정렬**합니다. 데이터가 많으면 느립니다. 대신:
  1. `aggregate(Count('id'))`로 후보 개수만 셈 (`SELECT COUNT`)
  2. `random.randrange(total)`로 랜덤 위치 결정
  3. `[n]` 인덱싱 → `LIMIT 1 OFFSET n` 으로 **딱 1건만** 조회
  - `order_by('id')`를 붙인 이유: 정렬 없는 OFFSET은 DB가 순서를 보장하지 않아 결과가 불안정할 수 있습니다.
- **`aggregate` vs `annotate`** (`genre_list` 뷰에서 사용):
  - `aggregate` → QuerySet 전체를 **하나의 값**으로 요약 (`{'total': 42}`)
  - `annotate` → **각 행마다** 계산 값을 붙임 (장르마다 `movie_count`)

### 코드 — `src/views/RecommendedView.vue` (스크립트)
```js
const pickMovie = async () => {
  isPicking.value = true
  try {
    movie.value = await getRandomMovieByGenre(rule.value.genre.id)
  } catch (error) {
    movie.value = null
  } finally {
    isPicking.value = false
  }
}

onMounted(async () => {
  try {
    weather.value = await fetchSeoulWeather()
    rule.value = matchWeatherGenre(weather.value.weathercode)
  } catch (error) {
    errorMessage.value = '날씨 정보를 불러오지 못했습니다.'
    return                         // 날씨 실패 시 추천 단계로 진행하지 않음
  } finally {
    isLoading.value = false        // return 해도 finally 는 실행됨!
  }
  await pickMovie()
})
```
- **로딩 상태를 2개로 분리**: `isLoading`(날씨, 페이지 전체)와 `isPicking`(영화만). "🎲 다른 영화 추천"을 누를 때 날씨 카드는 그대로 두고 영화 영역만 스피너가 돕니다.
- `pickMovie`를 함수로 분리해서 **최초 추천**과 **다시 추천 버튼**이 같은 코드를 씁니다.
- `catch`에서 `return`해도 `finally`는 실행된다는 JS 동작을 활용했습니다.

### ✍️ 직접 해보기
- `matchWeatherGenre(weather.value.weathercode)`를 `matchWeatherGenre(71)`로 바꿔 눈 오는 날을 시뮬레이션해 보세요.
- 기온(`temperature`)도 반영해서 30도 이상이면 다른 장르를 추천하도록 규칙을 확장해 보세요.

---

## Step 12. 스타일링 & 마무리 점검

### `src/assets/main.css` — 재사용 유틸리티 클래스
```css
.text-clamp-3 {                 /* 줄거리를 3줄까지만 보여주고 … 처리 */
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.hover-lift { transition: transform 0.15s ease, box-shadow 0.15s ease; }
.hover-lift:hover {             /* 카드에 마우스를 올리면 살짝 떠오름 */
  transform: translateY(-4px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15) !important;
}
```
- 줄거리 길이가 제각각이라 카드 높이가 들쭉날쭉한 문제 → `text-clamp-3` + 카드의 `h-100`으로 정렬.
- Bootstrap 그리드 `row-cols-2 row-cols-md-3 row-cols-lg-4 row-cols-xl-5`: 화면 너비에 따라 한 줄 카드 수가 2 → 5개로 변하는 **반응형 레이아웃**.
- `!important`는 Bootstrap의 `shadow-sm` 클래스(역시 `!important`)를 덮어쓰기 위해서만 사용.

### 제출 전 점검 목록
- [x] `.env`, `node_modules`, `dist`, `venv`, `db.sqlite3`가 `.gitignore`에 포함 (`git check-ignore -v <파일>`로 확인 가능)
- [x] `.env.example` 커밋 → 필요한 환경 변수 목록 공유
- [x] `python manage.py test movies` 통과
- [x] `npm run build` 성공
- [ ] 참고: `pinia`는 설치·등록만 되어 있고 아직 store를 사용하지 않습니다. 현재는 페이지 간 공유할 상태가 없어서 각 뷰의 `ref`로 충분했기 때문입니다.

---

## 복습 체크리스트 & 셀프 퀴즈

### ✅ 이 프로젝트로 익힌 개념

| 분류 | 개념 | 어디서 썼나 |
| :--- | :--- | :--- |
| Vue 기본 | `ref`, `computed`, `v-if/v-else-if/v-else`, `v-for` + `:key`, `v-model.trim` | 모든 뷰 |
| 생명주기 | `onMounted`, `onUnmounted` | MovieListView, VideoModalFrame |
| 반응성 | `watch` + getter + `immediate` | MovieDetailView |
| 컴포넌트 통신 | props(↓), emit(↑), slot(마크업 ↓) | MovieCard, VideoModalFrame, MovieDetailInfo |
| 고급 기능 | `Teleport`, 이벤트 수식어 `.self` `.prevent` | VideoModalFrame, ReviewSearchView |
| 라우터 | 동적 세그먼트, 정규식 제약, named route, `useRoute`/`useRouter` | router/index.js |
| 비동기 | `async/await`, `try/catch/finally`, 로딩·에러 상태 | 모든 뷰 |
| 설계 | API 레이어 분리, 어댑터 패턴, 규칙 테이블 | api/ |
| 보안 | XSS(`v-html` 회피), 환경 변수, CORS | decodeHtml, settings.py |
| Django | 모델 PK 설계, M2M, 중첩 Serializer, `get_object_or_404`, `prefetch_related` | movies/ |
| ORM 심화 | `aggregate` vs `annotate`, `Count`, `order_by('?')` 대안 | views.py |
| 기타 | 커스텀 management command, `update_or_create`, APITestCase | load_tmdb.py, tests.py |

### ❓ 셀프 퀴즈 (답은 위 본문에 있어요)

1. `/:movieId` 라우트에 `(\\d+)`를 붙이지 않으면 어떤 문제가 생길 수 있나요?
2. `/278`에서 `/238`로 이동했는데 화면이 안 바뀝니다. 원인과 해결책은?
3. 모달을 `v-show`로 숨기면 어떤 버그가 생기나요?
4. `window.addEventListener`를 `onUnmounted`에서 제거하지 않으면?
5. 유튜브 제목의 `&#39;`를 해결할 때 `v-html`을 쓰면 안 되는 이유는?
6. `keyword`와 `searchedKeyword`를 분리한 이유는?
7. Django `Movie` 모델의 PK를 TMDB ID로 정한 이유 두 가지는?
8. 뷰 코드 수정 없이 TMDB → Django 전환이 가능했던 핵심 조건은?
9. Postman에서는 되는데 Vue에서는 Django API 호출이 실패합니다. 가장 먼저 의심할 것은?
10. `order_by('?')` 대신 `Count` + 랜덤 offset을 쓴 이유는?
11. `aggregate`와 `annotate`의 차이는?
12. `VITE_` 환경 변수에 비밀 키를 넣는 것이 실서비스에서 위험한 이유는?

### 🚀 다음 단계 도전 과제
- **Pinia store 도입**: 영화 목록을 store에 캐싱해서 상세 → 목록으로 돌아올 때 재요청하지 않기
- **API 키 숨기기**: Youtube/TMDB 호출을 모두 Django를 거치게 하여 프론트에서 키 제거
- **페이지네이션**: Django에 `?page=` 지원 추가, 프론트에 무한 스크롤 적용
- **404 페이지**: 라우터 catch-all + 상세 API 404 응답 시 안내 화면
