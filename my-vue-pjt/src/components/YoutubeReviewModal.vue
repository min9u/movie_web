<template>
  <VideoModalFrame :title="decodeHtml(video.snippet.title)" @close="emit('close')">
    <div class="ratio ratio-16x9">
      <iframe
        :src="getEmbedUrl(video.id.videoId)"
        title="YouTube review"
        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
        allowfullscreen
      ></iframe>
    </div>
    <p class="small text-secondary p-3 mb-0">{{ video.snippet.channelTitle }}</p>
  </VideoModalFrame>
</template>

<script setup>
import VideoModalFrame from '@/components/VideoModalFrame.vue'
import { getEmbedUrl } from '@/api/youtube'
import { decodeHtml } from '@/utils/decodeHtml'

defineProps({
  video: { type: Object, required: true },
})
const emit = defineEmits(['close'])
</script>
