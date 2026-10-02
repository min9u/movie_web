<template>
  <h2 class="fw-bold mb-4">🔍 영화 리뷰 검색</h2>

  <form class="input-group input-group-lg mb-4 shadow-sm" @submit.prevent="onSearch">
    <input v-model.trim="keyword" type="text" class="form-control" placeholder="영화 제목을 입력하세요" />
    <button class="btn btn-dark" type="submit" :disabled="!keyword || isLoading">검색</button>
  </form>

  <div v-if="isLoading" class="text-center py-5">
    <div class="spinner-border" role="status"></div>
  </div>
  <div v-else-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
  <p v-else-if="!searchedKeyword" class="text-secondary text-center py-5">
    영화 제목을 검색하면 Youtube 리뷰 영상을 찾아드려요.
  </p>
  <p v-else-if="!videos.length" class="text-secondary text-center py-5">
    "{{ searchedKeyword }}" 에 대한 리뷰 영상이 없습니다.
  </p>
  <template v-else>
    <p class="text-secondary">"{{ searchedKeyword }} review" 검색 결과</p>
    <div class="row row-cols-1 row-cols-sm-2 row-cols-lg-3 g-4">
      <div v-for="video in videos" :key="video.id.videoId" class="col">
        <YoutubeCard :video="video" @select="selectedVideo = $event" />
      </div>
    </div>
  </template>

  <YoutubeReviewModal v-if="selectedVideo" :video="selectedVideo" @close="selectedVideo = null" />
</template>

<script setup>
import { ref } from 'vue'
import YoutubeCard from '@/components/YoutubeCard.vue'
import YoutubeReviewModal from '@/components/YoutubeReviewModal.vue'
import { searchVideos } from '@/api/youtube'

const keyword = ref('')
const searchedKeyword = ref('')
const videos = ref([])
const selectedVideo = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')

// F04: "검색어 + review" 로 Youtube 검색
const onSearch = async () => {
  if (!keyword.value) return
  isLoading.value = true
  errorMessage.value = ''
  try {
    videos.value = await searchVideos(`${keyword.value} review`)
    searchedKeyword.value = keyword.value
  } catch (error) {
    console.error(error)
    errorMessage.value = '영상을 검색하지 못했습니다. Youtube API Key 또는 할당량을 확인해주세요.'
  } finally {
    isLoading.value = false
  }
}
</script>
