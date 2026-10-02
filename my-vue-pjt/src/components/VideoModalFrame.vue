<template>
  <Teleport to="body">
    <div class="modal d-block" tabindex="-1" @click.self="emit('close')">
      <div class="modal-dialog modal-xl modal-dialog-centered">
        <div class="modal-content bg-dark text-white">
          <div class="modal-header border-secondary">
            <h5 class="modal-title text-truncate">{{ title }}</h5>
            <button type="button" class="btn-close btn-close-white" aria-label="Close" @click="emit('close')"></button>
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
import { onMounted, onUnmounted } from 'vue'

defineProps({
  title: { type: String, default: '' },
})
const emit = defineEmits(['close'])

const onKeydown = (event) => {
  if (event.key === 'Escape') emit('close')
}

onMounted(() => {
  document.body.classList.add('modal-open')
  window.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  document.body.classList.remove('modal-open')
  window.removeEventListener('keydown', onKeydown)
})
</script>
