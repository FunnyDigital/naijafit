<template>
  <button
    class="flex w-full items-start gap-3 rounded-xl2 border p-3.5 text-left transition-colors"
    :class="selected ? 'border-accent bg-accent-50' : 'border-line bg-surface hover:border-accent/40'"
    @click="$emit('select')"
  >
    <span
      v-if="icon"
      class="mt-0.5 flex h-9 w-9 shrink-0 items-center justify-center rounded-full"
      :class="selected ? 'bg-white text-accent-700' : 'bg-accent-50 text-accent-700'"
    >
      <Icon :name="icon" :size="18" />
    </span>

    <span class="min-w-0 flex-1">
      <span class="flex items-center justify-between gap-2">
        <span class="text-sm font-semibold text-ink">{{ label }}</span>
        <span
          v-if="selected"
          class="flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-accent text-white"
        >
          <Icon name="check" :size="13" :stroke-width="3" />
        </span>
      </span>
      <span v-if="hint" class="mt-0.5 block text-xs leading-relaxed text-ink-muted">{{ hint }}</span>
    </span>
  </button>
</template>

<script setup>
import Icon from './Icon.vue'

defineProps({
  label: { type: String, required: true },
  hint: { type: String, default: '' },
  icon: { type: String, default: '' },
  selected: { type: Boolean, default: false },
})

defineEmits(['select'])
</script>
