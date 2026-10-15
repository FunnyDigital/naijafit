<template>
  <div class="mx-auto w-full max-w-4xl px-4 py-5 sm:px-6 sm:py-7">
    <h1 class="font-display text-2xl font-semibold tracking-tight sm:text-3xl">Progress</h1>
    <p class="mt-1 text-sm text-ink-muted">The slow, boring, effective part. Keep showing up.</p>

    <div class="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
      <div v-for="tile in tiles" :key="tile.label" class="card p-3.5">
        <span class="flex h-8 w-8 items-center justify-center rounded-full" :class="tile.bg">
          <Icon :name="tile.icon" :size="16" />
        </span>
        <p class="mt-2 font-display text-xl font-semibold text-ink">{{ tile.value }}</p>
        <p class="text-[11px] uppercase tracking-wide text-ink-muted">{{ tile.label }}</p>
      </div>
    </div>

    <section class="card mt-4 p-4">
      <div class="flex flex-wrap items-end justify-between gap-3">
        <div>
          <p class="section-title text-base">Weight</p>
          <p class="text-xs text-ink-muted">
            <template v-if="weightChange !== null">
              {{ weightChange > 0 ? '+' : '' }}{{ weightChange }} {{ weightUnit }} since your first log
            </template>
            <template v-else>Log your weight to see the trend.</template>
          </p>
        </div>
        <form class="flex flex-wrap items-end gap-2" @submit.prevent="saveWeight">
          <div>
            <label class="label" :for="'w'">Today ({{ weightUnit }})</label>
            <input
              id="w"
              v-model.number="weightInput"
              class="field w-28"
              type="number"
              step="0.1"
              inputmode="decimal"
            />
          </div>
          <button class="btn-primary btn-sm" type="submit" :disabled="savingWeight">
            <Icon name="check" :size="15" /> Save
          </button>
        </form>
      </div>

      <div class="mt-4">
        <ProgressChart
          v-if="weightPoints.length"
          :points="weightPoints"
          :goal="goalWeight"
          color="#10b981"
          :height="160"
        />
        <p v-else class="py-6 text-center text-sm text-ink-muted">No weigh-ins yet.</p>
      </div>
    </section>

    <section class="card mt-4 p-4">
      <p class="section-title text-base">Calories eaten — last 7 days</p>
      <p class="text-xs text-ink-muted">
        Dashed line is your {{ targets.calorie_target }} kcal target.
      </p>
      <div class="mt-4">
        <ProgressChart
          :points="caloriePoints"
          type="bar"
          :goal="targets.calorie_target"
          color="#10b981"
          :height="150"
        />
      </div>
    </section>

    <section class="card mt-4 p-4">
      <p class="section-title text-base">Workouts — last 8 weeks</p>
      <p class="text-xs text-ink-muted">
        {{ workoutTotal }} sessions logged · current streak {{ streak }} days
      </p>
      <div class="mt-4">
        <ProgressChart :points="workoutPoints" type="bar" color="#f59e0b" :height="140" />
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

import Icon from '../components/Icon.vue'
import ProgressChart from '../components/ProgressChart.vue'
import { api } from '../services/api'
import { profileState } from '../composables/useProfile'
import { dashboardState } from '../composables/useDashboard'
import { pushToast } from '../composables/useToast'
import { formatWeight, kgToLb, lbToKg, round } from '../utils/format'
import { shiftISO, shortDate, todayISO } from '../utils/dates'

const units = computed(() => profileState.profile?.units || 'metric')
const weightUnit = computed(() => (units.value === 'imperial' ? 'lb' : 'kg'))
const targets = computed(() => profileState.profile?.targets || { calorie_target: 0 })

const weights = ref([])
const meals = ref([])
const workouts = ref([])
const weightInput = ref(null)
const savingWeight = ref(false)

const streak = computed(() => dashboardState.data?.streak || 0)
const weightTotal = computed(() => weights.value.length)
const mealTotal = computed(() => meals.value.length)
const workoutTotal = computed(() => workouts.value.length)

const displayWeight = (kg) => (units.value === 'imperial' ? round(kgToLb(kg), 1) : round(kg, 1))

const weightChange = computed(() => {
  if (weights.value.length < 2) return null
  const first = weights.value[0].weight_kg
  const last = weights.value[weights.value.length - 1].weight_kg
  return round(displayWeight(last) - displayWeight(first), 1)
})

const weightPoints = computed(() =>
  weights.value.slice(-24).map((log) => ({ label: shortDate(log.date), value: displayWeight(log.weight_kg) })),
)

const goalWeight = computed(() => {
  const goal = profileState.profile
  if (!goal) return null
  return displayWeight(goal.weight_kg)
})

const caloriePoints = computed(() => {
  const today = todayISO()
  const byDate = {}
  for (const meal of meals.value) {
    byDate[meal.date] = (byDate[meal.date] || 0) + meal.kcal
  }
  return Array.from({ length: 7 }, (_, index) => {
    const date = shiftISO(today, index - 6)
    return { label: shortDate(date), value: Math.round(byDate[date] || 0) }
  })
})

const workoutPoints = computed(() => {
  const today = todayISO()
  const weeks = Array.from({ length: 8 }, () => 0)
  const byDate = new Set(workouts.value.map((log) => log.date))
  for (let index = 0; index < 56; index += 1) {
    const date = shiftISO(today, -index)
    if (byDate.has(date)) {
      const weekIndex = Math.floor(index / 7)
      if (weekIndex < 8) weeks[7 - weekIndex] += 1
    }
  }
  return weeks.map((value, index) => ({ label: index === 0 ? '8w ago' : index === 7 ? 'this week' : '', value }))
})

const tiles = computed(() => [
  { label: 'Day streak', value: streak.value, icon: 'flame', bg: 'bg-warm-50 text-warm' },
  { label: 'Workouts', value: workoutTotal.value, icon: 'dumbbell', bg: 'bg-accent-50 text-accent-700' },
  { label: 'Meals logged', value: mealTotal.value, icon: 'bowl', bg: 'bg-amber-50 text-amber-700' },
  { label: 'Weigh-ins', value: weightTotal.value, icon: 'scale', bg: 'bg-sky-50 text-sky-600' },
])

async function load() {
  try {
    const [weightData, mealData, workoutData] = await Promise.all([
      api.listWeight(180),
      api.listMeals(),
      api.listWorkouts(120),
    ])
    weights.value = weightData.items || []
    meals.value = mealData.items || []
    workouts.value = workoutData.items || []
    const latest = weights.value[weights.value.length - 1]
    weightInput.value = latest ? displayWeight(latest.weight_kg) : displayWeight(profileState.profile?.weight_kg || 0)
  } catch (error) {
    pushToast(error.message, 'error')
  }
}

async function saveWeight() {
  if (weightInput.value == null || weightInput.value === '') return
  savingWeight.value = true
  try {
    const kg = units.value === 'imperial' ? round(lbToKg(weightInput.value), 2) : weightInput.value
    await api.logWeight({ date: todayISO(), weight_kg: kg })
    await load()
    pushToast('Weight saved', 'success')
  } catch (error) {
    pushToast(error.message, 'error')
  } finally {
    savingWeight.value = false
  }
}

onMounted(load)
</script>
