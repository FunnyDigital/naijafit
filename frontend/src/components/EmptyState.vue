<template>
  <div class="flex flex-col items-center justify-center px-6 py-10 text-center">
    <span class="flex h-12 w-12 items-center justify-center rounded-full bg-accent-50 text-accent-700">
      <Icon :name="icon" :size="22" />
    </span>
    <p class="mt-3 font-display text-base font-semibold text-ink">{{ title }}</p>
    <p v-if="text" class="mt-1 max-w-sm text-sm text-ink-muted">{{ text }}</p>
    <div class="mt-4">
      <slot />
    </div>
  </div>
</template>

<script setup>
import Icon from './Icon.vue'

defineProps({
  icon: { type: String, default: 'info' },
  title: { type: String, required: true },
  text: { type: String, default: '' },
})
</script>
