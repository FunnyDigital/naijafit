<template>
  <div class="card p-4">
    <div class="flex items-center justify-between gap-3">
      <div class="flex items-center gap-2 text-ink-soft">
        <span class="flex h-9 w-9 items-center justify-center rounded-full bg-sky-50 text-sky-600">
          <Icon name="droplet" :size="18" />
        </span>
        <div>
          <p class="text-sm font-semibold text-ink">Water</p>
          <p class="text-xs text-ink-muted">
            {{ formatVolume(ml) }} of {{ formatVolume(target) }}
          </p>
        </div>
      </div>
      <button
        class="icon-btn"
        :disabled="ml <= 0"
        aria-label="Remove a glass"
        @click="$emit('add', -GLASS)"
      >
        <Icon name="minus" :size="18" />
      </button>
    </div>

    <div class="mt-3 flex items-center gap-3">
      <div class="h-2.5 flex-1 overflow-hidden rounded-full bg-line/70">
        <div
          class="h-full rounded-full bg-sky-500 transition-[width] duration-700 ease-out"
          :style="{ width: `${percent}%` }"
        />
      </div>
      <button class="btn-soft btn-sm" :disabled="pending" @click="$emit('add', GLASS)">
        <Icon name="plus" :size="14" /> Glass
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

import Icon from './Icon.vue'
import { formatVolume } from '../utils/format'

const GLASS = 250

const props = defineProps({
  ml: { type: Number, default: 0 },
  target: { type: Number, default: 2500 },
  units: { type: String, default: 'metric' },
  pending: { type: Boolean, default: false },
})

defineEmits(['add'])

const percent = computed(() => {
  if (!props.target) return 0
  return Math.min(100, Math.round((props.ml / props.target) * 100))
})
</script>
