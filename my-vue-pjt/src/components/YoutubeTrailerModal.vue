<template>
  <VideoModalFrame :title="`${movieTitle} 공식 예고편`" @close="emit('close')">
    <div v-if="isLoading" class="text-center py-5">
      <div class="spinner-border text-light" role="status"></div>
    </div>
    <p v-else-if="errorMessage" class="p-4 mb-0 text-warning">{{ errorMessage }}</p>
    <div v-else class="ratio ratio-16x9">
      <iframe
        :src="getEmbedUrl(videoId)"
        title="YouTube trailer"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen
      ></iframe>
    </div>
  </VideoModalFrame>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import VideoModalFrame from '@/components/VideoModalFrame.vue'
import { searchVideos, getEmbedUrl } from '@/api/youtube'

const props = defineProps({
  movieTitle: { type: String, required: true },
})
const emit = defineEmits(['close'])

const videoId = ref(null)
const isLoading = ref(true)
const errorMessage = ref('')

// F03: "영화제목 + trailer" 로 검색 후 첫 번째 결과 재생
onMounted(async () => {
  try {
    const [firstVideo] = await searchVideos(`${props.movieTitle} trailer`, 1)
    if (!firstVideo) {
      errorMessage.value = '예고편을 찾을 수 없습니다.'
      return
    }
    videoId.value = firstVideo.id.videoId
  } catch (error) {
    console.error(error)
    errorMessage.value = '예고편을 불러오지 못했습니다. Youtube API Key를 확인해주세요.'
  } finally {
    isLoading.value = false
  }
})
</script>
