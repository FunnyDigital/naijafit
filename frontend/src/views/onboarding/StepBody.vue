<template>
  <div>
    <h1 class="font-display text-2xl font-semibold tracking-tight sm:text-3xl">Your body</h1>
    <p class="mt-1.5 text-sm text-ink-muted">
      We use these for your daily calories and macros. You can change them any time.
    </p>

    <div class="mt-6 space-y-6">
      <div>
        <span class="label">Units</span>
        <div class="inline-flex rounded-full border border-line bg-surface p-1">
          <button
            v-for="option in unitOptions"
            :key="option.value"
            class="rounded-full px-4 py-1.5 text-sm font-medium transition-colors"
            :class="form.units === option.value ? 'bg-accent text-white' : 'text-ink-soft'"
            @click="form.units = option.value"
          >
            {{ option.label }}
          </button>
        </div>
      </div>

      <div class="grid gap-5 sm:grid-cols-2">
        <div>
          <label class="label" for="age">Age</label>
          <input id="age" v-model.number="form.age" class="field" type="number" inputmode="numeric" min="12" max="100" />
        </div>

        <div v-if="form.units === 'metric'">
          <label class="label" for="height">Height (cm)</label>
          <input id="height" v-model.number="form.height_cm" class="field" type="number" inputmode="decimal" min="100" max="250" />
        </div>
        <div v-else>
          <span class="label">Height</span>
          <div class="flex gap-2">
            <div class="relative flex-1">
              <input v-model.number="feet" class="field pr-8" type="number" inputmode="numeric" min="3" max="8" />
              <span class="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-xs text-ink-faint">ft</span>
            </div>
            <div class="relative flex-1">
              <input v-model.number="inches" class="field pr-8" type="number" inputmode="numeric" min="0" max="11" />
              <span class="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-xs text-ink-faint">in</span>
            </div>
          </div>
        </div>

        <div v-if="form.units === 'metric'">
          <label class="label" for="weight">Weight (kg)</label>
          <input id="weight" v-model.number="form.weight_kg" class="field" type="number" inputmode="decimal" min="30" max="300" step="0.1" />
        </div>
        <div v-else>
          <label class="label" for="weight-lb">Weight (lb)</label>
          <input id="weight-lb" v-model.number="pounds" class="field" type="number" inputmode="decimal" min="66" max="660" step="0.5" />
        </div>

        <div>
          <span class="label">Body mass index</span>
          <div class="flex h-[2.6rem] items-center gap-2 rounded-lg border border-line bg-surface px-3">
            <span class="font-display text-lg font-semibold text-ink">{{ bmi }}</span>
            <span class="pill">{{ bmiBand }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

import { useOnboarding } from '../../composables/useOnboarding'
import { cmToIn, inToCm, kgToLb, lbToKg, round } from '../../utils/format'

const { form } = useOnboarding()

const unitOptions = [
  { value: 'metric', label: 'kg / cm' },
  { value: 'imperial', label: 'lb / ft' },
]

const rawInches = computed(() => cmToIn(form.height_cm))

const feet = computed({
  get: () => Math.floor(rawInches.value / 12),
  set: (value) => {
    const remainder = rawInches.value - Math.floor(rawInches.value / 12) * 12
    form.height_cm = round(inToCm(Number(value) * 12 + remainder), 1)
  },
})

const inches = computed({
  get: () => Math.round(rawInches.value - Math.floor(rawInches.value / 12) * 12),
  set: (value) => {
    const wholeFeet = Math.floor(rawInches.value / 12)
    form.height_cm = round(inToCm(wholeFeet * 12 + Number(value)), 1)
  },
})

const pounds = computed({
  get: () => round(kgToLb(form.weight_kg), 1),
  set: (value) => {
    form.weight_kg = round(lbToKg(Number(value)), 1)
  },
})

const bmi = computed(() => {
  const metres = form.height_cm / 100
  if (!metres) return '—'
  return round(form.weight_kg / (metres * metres), 1)
})

const bmiBand = computed(() => {
  const value = Number(bmi.value)
  if (!value) return '—'
  if (value < 18.5) return 'Underweight'
  if (value < 25) return 'Healthy'
  if (value < 30) return 'Overweight'
  return 'Obese'
})
</script>
