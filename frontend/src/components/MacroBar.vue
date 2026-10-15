<template>
  <div>
    <div class="mb-1 flex items-baseline justify-between gap-2">
      <span class="text-[11px] font-semibold uppercase tracking-wide text-ink-muted">{{ label }}</span>
      <span class="text-xs text-ink-muted">
        <b class="font-semibold text-ink-soft">{{ Math.round(value) }}</b> / {{ Math.round(target) }}g
      </span>
    </div>
    <div class="h-2 overflow-hidden rounded-full bg-line/70">
      <div
        class="h-full rounded-full transition-[width] duration-700 ease-out"
        :style="{ width: `${percent}%`, background: color }"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  label: { type: String, required: true },
  value: { type: Number, default: 0 },
  target: { type: Number, default: 0 },
  color: { type: String, default: '#10b981' },
})

const percent = computed(() => {
  if (!props.target) return 0
  return Math.min(100, Math.round((props.value / props.target) * 100))
})
</script>
