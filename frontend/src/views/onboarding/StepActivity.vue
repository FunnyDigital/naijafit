<template>
  <div>
    <h1 class="font-display text-2xl font-semibold tracking-tight sm:text-3xl">How active are you?</h1>
    <p class="mt-1.5 text-sm text-ink-muted">
      Think about a normal day outside of these workouts — work, walking, chores.
    </p>

    <div class="mt-6 grid gap-2.5">
      <ChoiceCard
        v-for="item in options.activity_levels"
        :key="item.value"
        :label="item.label"
        :hint="item.hint"
        :icon="ICONS[item.value] || 'pulse'"
        :selected="form.activity_level === item.value"
        @select="form.activity_level = item.value"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

import ChoiceCard from '../../components/ChoiceCard.vue'
import { useOnboarding } from '../../composables/useOnboarding'

const { form, optionsState } = useOnboarding()
const options = computed(() => optionsState.data || { activity_levels: [] })

const ICONS = {
  sedentary: 'clock',
  light: 'pulse',
  moderate: 'trending',
  active: 'flame',
  very_active: 'trophy',
}
</script>
