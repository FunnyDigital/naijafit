<template>
  <div class="rounded-xl2 border border-line bg-surface">
    <button class="flex w-full items-center gap-3 p-3 text-left" @click="open = !open">
      <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-accent-50 text-accent-700">
        <Icon :name="sectionIcon" :size="17" />
      </span>

      <span class="min-w-0 flex-1">
        <span class="flex items-center gap-2">
          <span class="truncate text-sm font-semibold text-ink">{{ item.exercise.name }}</span>
          <span
            v-if="item.section !== 'main'"
            class="shrink-0 rounded-full bg-line/60 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-ink-muted"
          >
            {{ item.section }}
          </span>
        </span>
        <span class="mt-0.5 block text-xs text-ink-muted">
          {{ dose }} · rest {{ item.rest_sec }}s
          <template v-if="muscles"> · {{ muscles }}</template>
        </span>
      </span>

      <Icon :name="open ? 'chevronUp' : 'chevronDown'" :size="18" class="shrink-0 text-ink-faint" />
    </button>

    <div v-if="open" class="border-t border-line px-3 py-3">
      <p class="text-sm leading-relaxed text-ink-soft">{{ item.exercise.instructions }}</p>
      <div class="mt-2 flex flex-wrap gap-1.5">
        <span class="chip !py-0.5 text-[11px] capitalize">{{ item.exercise.equipment }}</span>
        <span class="chip !py-0.5 text-[11px] capitalize">{{ item.exercise.level }}</span>
        <span class="chip !py-0.5 text-[11px] capitalize">{{ item.exercise.category.replace('_', ' ') }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

import Icon from './Icon.vue'

const props = defineProps({
  item: { type: Object, required: true },
})

const open = ref(false)

const SECTION_ICONS = {
  warmup: 'sparkles',
  main: 'dumbbell',
  finisher: 'flame',
  cooldown: 'heart',
}

const sectionIcon = computed(() => SECTION_ICONS[props.item.section] || 'dumbbell')

const dose = computed(() => {
  const { sets, reps, seconds } = props.item
  const volume = reps ? `${reps} reps` : `${seconds}s`
  return `${sets} × ${volume}`
})

const muscles = computed(() => (props.item.exercise.primary_muscles || []).slice(0, 3).join(', '))
</script>
