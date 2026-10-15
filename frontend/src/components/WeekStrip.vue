<template>
  <div class="flex gap-1.5 overflow-x-auto no-scrollbar sm:gap-2">
    <button
      v-for="day in days"
      :key="day.day_index"
      class="flex min-w-[3.6rem] flex-1 flex-col items-center gap-1 rounded-xl2 border px-2 py-2.5 transition-colors"
      :class="
        day.day_index === active
          ? 'border-accent bg-accent-50 text-accent-700'
          : 'border-line bg-surface text-ink-soft hover:border-accent/40'
      "
      @click="$emit('select', day.day_index)"
    >
      <span class="text-[11px] font-semibold uppercase tracking-wide">
        {{ WEEKDAYS_SHORT[day.day_index] }}
      </span>
      <span v-if="day.is_rest_day" class="text-[10px] text-ink-faint">Rest</span>
      <span v-else-if="day.est_minutes" class="text-[10px] text-ink-faint">{{ day.est_minutes }}m</span>
      <span v-else class="text-[10px] text-ink-faint">—</span>
      <span
        class="h-1.5 w-1.5 rounded-full"
        :class="day.is_rest_day ? 'bg-line' : 'bg-accent'"
      />
    </button>
  </div>
</template>

<script setup>
import { WEEKDAYS_SHORT } from '../utils/dates'

defineProps({
  days: { type: Array, default: () => [] },
  active: { type: Number, default: 0 },
})

defineEmits(['select'])
</script>
