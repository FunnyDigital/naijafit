<template>
  <div>
    <h1 class="font-display text-2xl font-semibold tracking-tight sm:text-3xl">Let’s meet you</h1>
    <p class="mt-1.5 text-sm text-ink-muted">
      Two quick things, then we’ll shape the plan around you. Everything stays on your own server.
    </p>

    <div class="mt-6 space-y-6">
      <div>
        <label class="label" for="name">What should we call you?</label>
        <input
          id="name"
          v-model="form.name"
          class="field"
          placeholder="e.g. Ada"
          autocomplete="given-name"
          maxlength="60"
        />
      </div>

      <div>
        <span class="label">Sex</span>
        <div class="grid gap-2.5 sm:grid-cols-2">
          <ChoiceCard
            v-for="item in options.sexes"
            :key="item.value"
            :label="item.label"
            :hint="item.value === 'male' ? 'Uses the male calorie formula.' : 'Uses the female calorie formula.'"
            :icon="item.value === 'male' ? 'user' : 'heart'"
            :selected="form.sex === item.value"
            @select="form.sex = item.value"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

import ChoiceCard from '../../components/ChoiceCard.vue'
import { useOnboarding } from '../../composables/useOnboarding'

const { form, optionsState } = useOnboarding()
const options = computed(() => optionsState.data || { sexes: [] })
</script>
