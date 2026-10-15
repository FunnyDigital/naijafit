<template>
  <div>
    <h1 class="font-display text-2xl font-semibold tracking-tight sm:text-3xl">What are you after?</h1>
    <p class="mt-1.5 text-sm text-ink-muted">This sets your calories — a gentle deficit, maintenance, or a small surplus.</p>

    <div class="mt-6 grid gap-2.5">
      <ChoiceCard
        v-for="item in options.goals"
        :key="item.value"
        :label="item.label"
        :hint="item.hint"
        :icon="ICONS[item.value] || 'target'"
        :selected="form.goal === item.value"
        @select="form.goal = item.value"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

import ChoiceCard from '../../components/ChoiceCard.vue'
import { useOnboarding } from '../../composables/useOnboarding'

const { form, optionsState } = useOnboarding()
const options = computed(() => optionsState.data || { goals: [] })

const ICONS = { lose: 'trending', maintain: 'target', gain: 'dumbbell' }
</script>
