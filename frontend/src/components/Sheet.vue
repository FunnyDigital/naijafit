<template>
  <Teleport to="body">
    <Transition name="sheet">
      <div v-if="open" class="fixed inset-0 z-50 flex items-end justify-center sm:items-center">
        <div class="absolute inset-0 bg-ink/40" @click="close" />
        <div
          class="relative flex max-h-[88vh] w-full flex-col overflow-hidden rounded-t-3xl bg-surface shadow-lift sm:max-w-lg sm:rounded-3xl"
        >
          <div class="flex items-center justify-between gap-3 border-b border-line px-5 py-3.5">
            <p class="font-display text-base font-semibold text-ink">{{ title }}</p>
            <button class="icon-btn" aria-label="Close" @click="close">
              <Icon name="close" :size="18" />
            </button>
          </div>
          <div class="flex-1 overflow-y-auto overscroll-contain px-5 py-4">
            <slot />
          </div>
          <div v-if="$slots.footer" class="safe-bottom border-t border-line px-5 py-3">
            <slot name="footer" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { onBeforeUnmount, onMounted, watch } from 'vue'

import Icon from './Icon.vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: '' },
})

const emit = defineEmits(['close'])

function close() {
  emit('close')
}

function onKey(event) {
  if (event.key === 'Escape' && props.open) close()
}

watch(
  () => props.open,
  (open) => {
    document.body.style.overflow = open ? 'hidden' : ''
  },
)

onMounted(() => window.addEventListener('keydown', onKey))
onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.sheet-enter-active,
.sheet-leave-active {
  transition: opacity 0.22s ease;
}
.sheet-enter-from,
.sheet-leave-to {
  opacity: 0;
}
</style>
