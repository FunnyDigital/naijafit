<template>
  <div>
    <h1 class="font-display text-2xl font-semibold tracking-tight sm:text-3xl">Training at home</h1>
    <p class="mt-1.5 text-sm text-ink-muted">How many days, how hard, and what you have around the house.</p>

    <div class="mt-6 space-y-7">
      <div>
        <span class="label">Workouts per week</span>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="day in options.workout_days"
            :key="day"
            class="h-11 w-11 rounded-full border text-sm font-semibold transition-colors"
            :class="
              form.workouts_per_week === day
                ? 'border-accent bg-accent text-white'
                : 'border-line bg-surface text-ink-soft hover:border-accent/50'
            "
            @click="form.workouts_per_week = day"
          >
            {{ day }}
          </button>
        </div>
        <p class="mt-1.5 text-xs text-ink-faint">Rest days are spread through the week for you.</p>
      </div>

      <div>
        <span class="label">Your training level</span>
        <div class="grid gap-2.5 sm:grid-cols-3">
          <ChoiceCard
            v-for="item in options.levels"
            :key="item.value"
            :label="item.label"
            :hint="item.hint"
            :selected="form.level === item.value"
            @select="form.level = item.value"
          />
        </div>
      </div>

      <div>
        <span class="label">What’s available</span>
        <div class="grid gap-2.5 sm:grid-cols-2">
          <ChoiceCard
            v-for="item in options.equipment"
            :key="item.value"
            :label="item.label"
            :hint="item.hint"
            :icon="EQUIPMENT_ICONS[item.value]"
            :selected="form.equipment.includes(item.value)"
            @select="toggleEquipment(item.value)"
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
const options = computed(() => optionsState.data || { levels: [], equipment: [], workout_days: [3] })

const EQUIPMENT_ICONS = { none: 'user', chair: 'home', band: 'swap', dumbbell: 'dumbbell' }

function toggleEquipment(value) {
  if (value === 'none') {
    form.equipment = ['none']
    return
  }
  const set = new Set(form.equipment.filter((item) => item !== 'none'))
  if (set.has(value)) set.delete(value)
  else set.add(value)
  form.equipment = set.size ? [...set] : ['none']
}
</script>
