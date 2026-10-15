<template>
  <div class="pointer-events-none fixed inset-x-0 bottom-24 z-50 flex flex-col items-center gap-2 px-4 md:bottom-8">
    <TransitionGroup name="toast">
      <button
        v-for="toast in toasts"
        :key="toast.id"
        class="pointer-events-auto flex max-w-sm items-center gap-2 rounded-full border px-4 py-2 text-sm shadow-lift"
        :class="styleFor(toast.type)"
        @click="removeToast(toast.id)"
      >
        <Icon :name="iconFor(toast.type)" :size="16" />
        <span>{{ toast.message }}</span>
      </button>
    </TransitionGroup>
  </div>
</template>

<script setup>
import Icon from './Icon.vue'
import { toasts, removeToast } from '../composables/useToast'

function styleFor(type) {
  if (type === 'error') return 'border-red-200 bg-white text-red-700'
  if (type === 'success') return 'border-accent-100 bg-white text-accent-700'
  return 'border-line bg-white text-ink-soft'
}

function iconFor(type) {
  if (type === 'error') return 'alert'
  if (type === 'success') return 'check'
  return 'info'
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateY(8px);
}
</style>
