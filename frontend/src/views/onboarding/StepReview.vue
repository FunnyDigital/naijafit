<template>
  <div>
    <h1 class="font-display text-2xl font-semibold tracking-tight sm:text-3xl">Here’s your setup</h1>
    <p class="mt-1.5 text-sm text-ink-muted">Check it over — you can change any of it later from your profile.</p>

    <div class="mt-6 grid gap-4 lg:grid-cols-2">
      <div class="card p-4">
        <p class="section-title text-base">Your numbers</p>
        <div v-if="loadingTargets" class="mt-4 space-y-3">
          <div class="h-10 animate-pulse rounded-xl bg-line/50" />
          <div class="h-10 animate-pulse rounded-xl bg-line/50" />
        </div>
        <template v-else-if="targets">
          <div class="mt-3 flex items-center gap-4">
            <div class="text-center">
              <p class="font-display text-3xl font-semibold text-ink">{{ targets.calorie_target }}</p>
              <p class="text-[11px] uppercase tracking-wide text-ink-muted">kcal / day</p>
            </div>
            <div class="grid flex-1 grid-cols-3 gap-2 text-center">
              <div class="rounded-xl bg-accent-50 py-2">
                <p class="text-sm font-semibold text-accent-700">{{ targets.protein_g }}g</p>
                <p class="text-[10px] uppercase tracking-wide text-ink-muted">Protein</p>
              </div>
              <div class="rounded-xl bg-amber-50 py-2">
                <p class="text-sm font-semibold text-amber-700">{{ targets.carbs_g }}g</p>
                <p class="text-[10px] uppercase tracking-wide text-ink-muted">Carbs</p>
              </div>
              <div class="rounded-xl bg-rose-50 py-2">
                <p class="text-sm font-semibold text-rose-700">{{ targets.fat_g }}g</p>
                <p class="text-[10px] uppercase tracking-wide text-ink-muted">Fat</p>
              </div>
            </div>
          </div>
          <dl class="mt-4 space-y-2 border-t border-line pt-3 text-sm">
            <div class="flex justify-between">
              <dt class="text-ink-muted">Burns at rest</dt>
              <dd class="font-medium text-ink-soft">{{ targets.bmr }} kcal</dd>
            </div>
            <div class="flex justify-between">
              <dt class="text-ink-muted">Daily burn with activity</dt>
              <dd class="font-medium text-ink-soft">{{ targets.tdee }} kcal</dd>
            </div>
            <div class="flex justify-between">
              <dt class="text-ink-muted">Water</dt>
              <dd class="font-medium text-ink-soft">{{ formatVolume(targets.water_ml) }}</dd>
            </div>
          </dl>
        </template>
      </div>

      <div class="card p-4">
        <p class="section-title text-base">Your answers</p>
        <dl class="mt-3 divide-y divide-line text-sm">
          <div v-for="row in summary" :key="row.label" class="flex items-start justify-between gap-4 py-2">
            <dt class="text-ink-muted">{{ row.label }}</dt>
            <dd class="text-right font-medium text-ink-soft">{{ row.value }}</dd>
          </div>
        </dl>
      </div>
    </div>

    <div class="mt-4 grid gap-3 sm:grid-cols-2">
      <div class="flex items-start gap-3 rounded-xl2 border border-line bg-surface p-4">
        <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-accent-50 text-accent-700">
          <Icon name="dumbbell" :size="18" />
        </span>
        <div>
          <p class="text-sm font-semibold text-ink">A 7-day workout plan</p>
          <p class="text-xs text-ink-muted">
            {{ form.workouts_per_week }} sessions built for {{ form.level }} level with
            {{ equipmentLabel }}.
          </p>
        </div>
      </div>
      <div class="flex items-start gap-3 rounded-xl2 border border-line bg-surface p-4">
        <span class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-amber-50 text-amber-700">
          <Icon name="bowl" :size="18" />
        </span>
        <div>
          <p class="text-sm font-semibold text-ink">A week of Nigerian meals</p>
          <p class="text-xs text-ink-muted">
            Breakfast, lunch, dinner and a snack each day — jollof, swallows, soups, beans and more.
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

import Icon from '../../components/Icon.vue'
import { api } from '../../services/api'
import { useOnboarding } from '../../composables/useOnboarding'
import { formatVolume, formatWeight, formatHeight } from '../../utils/format'
import { titleCase } from '../../utils/dates'

const { form, optionsState } = useOnboarding()

const targets = ref(null)
const loadingTargets = ref(true)

const options = computed(() => optionsState.data || {})

const equipmentLabel = computed(() => {
  const labels = (options.value.equipment || [])
    .filter((item) => form.equipment.includes(item.value))
    .map((item) => item.label.toLowerCase())
  return labels.length ? labels.join(', ') : 'bodyweight only'
})

const summary = computed(() => {
  const goal = (options.value.goals || []).find((item) => item.value === form.goal)
  const activity = (options.value.activity_levels || []).find((item) => item.value === form.activity_level)

  const rows = [
    { label: 'Name', value: form.name || '—' },
    { label: 'Sex', value: titleCase(form.sex) },
    { label: 'Age', value: `${form.age}` },
    { label: 'Height', value: formatHeight(form.height_cm, form.units) },
    { label: 'Weight', value: formatWeight(form.weight_kg, form.units) },
    { label: 'Goal', value: goal?.label || form.goal },
    { label: 'Activity', value: activity?.label || form.activity_level },
    { label: 'Training', value: `${form.workouts_per_week} days · ${titleCase(form.level)}` },
  ]
  if (form.dietary_flags.length) {
    const labels = (options.value.dietary_flags || [])
      .filter((item) => form.dietary_flags.includes(item.value))
      .map((item) => item.label)
    rows.push({ label: 'Avoiding', value: labels.join(', ') })
  }
  return rows
})

onMounted(async () => {
  try {
    targets.value = await api.previewTargets({ ...form })
  } catch {
    targets.value = null
  } finally {
    loadingTargets.value = false
  }
})
</script>
