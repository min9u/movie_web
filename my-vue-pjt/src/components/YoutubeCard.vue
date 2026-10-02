<template>
  <div class="card h-100 border-0 shadow-sm hover-lift" role="button" @click="emit('select', video)">
    <img :src="snippet.thumbnails.high?.url ?? snippet.thumbnails.default.url" class="card-img-top" :alt="title" />
    <div class="card-body">
      <h6 class="card-title text-clamp-2">{{ title }}</h6>
      <p class="card-text small text-secondary mb-0">{{ snippet.channelTitle }}</p>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { decodeHtml } from '@/utils/decodeHtml'

const props = defineProps({
  video: { type: Object, required: true },
})
const emit = defineEmits(['select'])

const snippet = computed(() => props.video.snippet)
const title = computed(() => decodeHtml(snippet.value.title))
</script>
