<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-5 sm:px-6 sm:py-7">
    <div class="flex flex-wrap items-end justify-between gap-3">
      <div>
        <p class="text-sm text-ink-muted">{{ longDate(today) }}</p>
        <h1 class="font-display text-2xl font-semibold tracking-tight sm:text-3xl">
          {{ greeting() }}, {{ firstName }}
        </h1>
      </div>
      <div class="flex items-center gap-2">
        <span v-if="streak" class="pill !bg-warm-50 !text-warm">
          <Icon name="flame" :size="14" /> {{ streak }} day streak
        </span>
        <RouterLink to="/meals" class="btn-ghost btn-sm">
          Full meal plan <Icon name="arrowRight" :size="14" />
        </RouterLink>
      </div>
    </div>

    <div v-if="loading" class="mt-6">
      <LoadingState :rows="4" />
    </div>

    <EmptyState
      v-else-if="!dash"
      class="mt-10"
      icon="alert"
      title="We couldn’t load your day"
      :text="error || 'The server didn’t answer. Check that the backend is running, then try again.'"
    >
      <button class="btn-primary" @click="refresh(true)">Try again</button>
    </EmptyState>

    <div
      v-else
      class="mt-5 grid gap-4 lg:grid-cols-[minmax(0,1.55fr)_minmax(0,1fr)] lg:items-start"
    >
      <!-- Today's workout -->
      <section
        v-reveal
        class="order-1 card overflow-hidden lg:col-start-1 lg:row-start-1"
      >
        <div class="flex items-start justify-between gap-3 border-b border-line px-4 py-3.5">
          <div>
            <p class="text-[11px] font-semibold uppercase tracking-wide text-ink-muted">
              Today’s workout
            </p>
            <p class="section-title">{{ dash.workout?.title || 'Nothing planned' }}</p>
          </div>
          <span v-if="dash.workout && !dash.workout.is_rest_day" class="pill">
            <Icon name="timer" :size="14" /> {{ dash.workout.est_minutes }} min
          </span>
        </div>

        <div v-if="!dash.workout || dash.workout.is_rest_day" class="px-4 py-6 text-center">
          <span class="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-accent-50 text-accent-700">
            <Icon name="heart" :size="22" />
          </span>
          <p class="mt-3 font-display text-base font-semibold text-ink">Rest and recover</p>
          <p class="mx-auto mt-1 max-w-sm text-sm text-ink-muted">
            No session today. A walk, some stretching and good water intake all count.
          </p>
        </div>

        <div v-else class="px-4 py-3.5">
          <p class="text-xs text-ink-muted">{{ dash.workout.focus }}</p>
          <ul class="mt-3 space-y-1.5">
            <li
              v-for="item in dash.workout.items.slice(0, 5)"
              :key="item.id"
              class="flex items-center justify-between gap-3 text-sm"
            >
              <span class="truncate text-ink-soft">{{ item.exercise.name }}</span>
              <span class="shrink-0 text-xs text-ink-faint">
                {{ item.sets }} × {{ item.reps ? `${item.reps} reps` : `${item.seconds}s` }}
              </span>
            </li>
          </ul>
          <p v-if="dash.workout.items.length > 5" class="mt-2 text-xs text-ink-faint">
            + {{ dash.workout.items.length - 5 }} more
          </p>

          <div class="mt-4 flex flex-wrap items-center gap-2">
            <RouterLink :to="`/workouts/${dash.weekday_index}`" class="btn-ghost btn-sm">
              <Icon name="play" :size="14" /> Open workout
            </RouterLink>
            <button v-if="!dash.workout_done" class="btn-primary btn-sm" :disabled="logging" @click="completeWorkout">
              <Icon name="check" :size="14" /> Mark complete
            </button>
            <button v-else class="btn-soft btn-sm" :disabled="logging" @click="undoWorkout">
              <Icon name="check" :size="14" /> Done today · undo
            </button>
          </div>
        </div>
      </section>

      <!-- Calories, water and weight: above the meals on a phone, side column on desktop -->
      <div class="order-2 space-y-4 lg:col-start-2 lg:row-span-2 lg:row-start-1">
        <section v-reveal="30" class="card p-4">
          <div class="flex items-center gap-4">
            <StatRing :value="consumed.kcal" :max="targets.calorie_target" :size="132">
              <span class="font-display text-2xl font-semibold text-ink">
                <CountUp :value="Math.abs(remaining)" />
              </span>
              <span class="text-[10px] uppercase tracking-wide text-ink-muted">
                {{ remaining >= 0 ? 'kcal left' : 'kcal over' }}
              </span>
            </StatRing>

            <div class="min-w-0 flex-1 space-y-2.5">
              <div class="flex items-baseline justify-between text-sm">
                <span class="text-ink-muted">Target</span>
                <span class="font-semibold text-ink-soft">{{ targets.calorie_target }} kcal</span>
              </div>
              <div class="flex items-baseline justify-between text-sm">
                <span class="text-ink-muted">Eaten</span>
                <span class="font-semibold text-ink-soft">{{ Math.round(consumed.kcal) }} kcal</span>
              </div>
              <p class="text-[11px] leading-relaxed text-ink-faint">
                Log meals as you eat them to keep this honest.
              </p>
            </div>
          </div>

          <div class="mt-4 space-y-2.5 border-t border-line pt-4">
            <MacroBar label="Protein" :value="consumed.protein_g" :target="targets.protein_g" color="#10b981" />
            <MacroBar label="Carbs" :value="consumed.carbs_g" :target="targets.carbs_g" color="#f59e0b" />
            <MacroBar label="Fat" :value="consumed.fat_g" :target="targets.fat_g" color="#f43f5e" />
          </div>
        </section>

        <WaterTracker
          v-reveal="90"
          :ml="dash.water.ml"
          :target="dash.water.target_ml"
          :units="units"
          :pending="logging"
          @add="addWater"
        />

        <section v-reveal="120" class="card p-4">
          <div class="flex items-center justify-between gap-3">
            <div class="flex items-center gap-2 text-ink-soft">
              <span class="flex h-9 w-9 items-center justify-center rounded-full bg-accent-50 text-accent-700">
                <Icon name="scale" :size="18" />
              </span>
              <div>
                <p class="text-sm font-semibold text-ink">Weight</p>
                <p class="text-xs text-ink-muted">{{ formatWeight(dash.weight, units) }}</p>
              </div>
            </div>
            <RouterLink to="/progress" class="btn-ghost btn-sm">Log</RouterLink>
          </div>
        </section>
      </div>

      <!-- Meals -->
      <section
        v-reveal="60"
        class="order-3 card overflow-hidden lg:col-start-1 lg:row-start-2"
      >
        <div class="flex items-center justify-between gap-3 border-b border-line px-4 py-3.5">
          <p class="section-title">Today’s meals</p>
          <RouterLink to="/foods" class="text-xs font-medium text-accent-700 hover:underline">
            Food library
          </RouterLink>
        </div>

        <div v-if="!mealGroups.length" class="px-4 py-6">
          <p class="text-sm text-ink-muted">No meals planned yet — regenerate your plan from Profile.</p>
        </div>

        <div v-else class="divide-y divide-line">
          <div v-for="group in mealGroups" :key="group.slot" class="px-4 py-3.5">
            <p class="text-[11px] font-semibold uppercase tracking-wide text-ink-muted">
              {{ group.label }}
            </p>
            <div class="mt-2 space-y-2">
              <DishRow
                v-for="meal in group.meals"
                :key="meal.id"
                :food="meal.food"
                :paired="meal.paired_food"
                :servings="meal.servings"
                :kcal="meal.kcal"
                :protein="meal.protein_g"
                :carbs="meal.carbs_g"
                :fat="meal.fat_g"
                :to="`/foods/${meal.food.id}`"
                :badge="meal.is_suggestion ? 'Try this' : ''"
                size="sm"
              >
                <template #actions>
                  <button
                    v-if="meal.is_suggestion"
                    class="icon-btn !text-warm"
                    title="Keep this on my menu"
                    :disabled="busyMeal === meal.id"
                    @click.prevent.stop="acceptSuggestion(meal)"
                  >
                    <Icon name="circleCheck" :size="18" :stroke-width="2.1" />
                  </button>
                  <button
                    class="icon-btn"
                    title="Swap this dish"
                    :disabled="busyMeal === meal.id"
                    @click.prevent.stop="swapMeal(meal)"
                  >
                    <Icon name="swap" :size="17" />
                  </button>
                  <button
                    v-if="!isLogged(meal)"
                    class="icon-btn"
                    title="I ate this"
                    @click.prevent.stop="logMeal(meal)"
                  >
                    <Icon name="plus" :size="17" />
                  </button>
                  <button
                    v-else
                    class="icon-btn !text-accent-700"
                    title="Eaten — tap to remove"
                    @click.prevent.stop="unlogMeal(meal)"
                  >
                    <Icon name="check" :size="17" :stroke-width="2.4" />
                  </button>
                </template>
              </DishRow>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

import CountUp from '../components/CountUp.vue'
import DishRow from '../components/DishRow.vue'
import EmptyState from '../components/EmptyState.vue'
import Icon from '../components/Icon.vue'
import LoadingState from '../components/LoadingState.vue'
import MacroBar from '../components/MacroBar.vue'
import StatRing from '../components/StatRing.vue'
import WaterTracker from '../components/WaterTracker.vue'
import { api } from '../services/api'
import { dashboardState, loadDashboard } from '../composables/useDashboard'
import { pushToast } from '../composables/useToast'
import { useUnits } from '../utils/format'
import { greeting, longDate, todayISO } from '../utils/dates'

const SLOT_LABELS = {
  breakfast: 'Breakfast',
  lunch: 'Lunch',
  dinner: 'Dinner',
  snack: 'Snack',
  extra: 'Extra protein',
}

const today = todayISO()
const dash = computed(() => dashboardState.data)
const loading = computed(() => dashboardState.loading && !dashboardState.data)
const error = computed(() => dashboardState.error)
const logging = ref(false)
const busyMeal = ref(null)
const { units, formatWeight } = useUnits()

const firstName = computed(() => (dash.value?.profile_name || 'there').split(' ')[0])
const targets = computed(() => dash.value?.targets || { calorie_target: 0, protein_g: 0, carbs_g: 0, fat_g: 0 })
const consumed = computed(() => dash.value?.consumed || { kcal: 0, protein_g: 0, carbs_g: 0, fat_g: 0 })
const streak = computed(() => dash.value?.streak || 0)
const remaining = computed(() => Math.round(targets.value.calorie_target - consumed.value.kcal))

const mealGroups = computed(() => {
  const order = ['breakfast', 'lunch', 'dinner', 'snack', 'extra']
  const groups = {}
  for (const meal of dash.value?.meals || []) {
    if (!groups[meal.slot]) groups[meal.slot] = []
    groups[meal.slot].push(meal)
  }
  return order.filter((slot) => groups[slot]).map((slot) => ({
    slot,
    label: SLOT_LABELS[slot] || slot,
    meals: groups[slot],
  }))
})

function isLogged(meal) {
  return (dash.value?.meal_logs || []).some(
    (log) => log.food_id === meal.food.id && log.slot === meal.slot,
  )
}

function loggedEntry(meal) {
  return (dash.value?.meal_logs || []).find(
    (log) => log.food_id === meal.food.id && log.slot === meal.slot,
  )
}

async function refresh(force = false) {
  await loadDashboard(today, force)
}

async function completeWorkout() {
  logging.value = true
  try {
    await api.logWorkout({
      date: today,
      day_index: dash.value.weekday_index,
      title: dash.value.workout?.title || '',
      duration_min: dash.value.workout?.est_minutes || 0,
    })
    await refresh(true)
    pushToast('Workout logged. Nice one.', 'success')
  } catch (err) {
    pushToast(err.message, 'error')
  } finally {
    logging.value = false
  }
}

async function undoWorkout() {
  logging.value = true
  try {
    await api.deleteWorkout(today)
    await refresh(true)
  } catch (err) {
    pushToast(err.message, 'error')
  } finally {
    logging.value = false
  }
}

async function logMeal(meal) {
  busyMeal.value = meal.id
  try {
    await api.logMeal({ date: today, slot: meal.slot, food_id: meal.food.id, servings: meal.servings })
    await refresh(true)
  } catch (err) {
    pushToast(err.message, 'error')
  } finally {
    busyMeal.value = null
  }
}

async function unlogMeal(meal) {
  const entry = loggedEntry(meal)
  if (!entry) return
  busyMeal.value = meal.id
  try {
    await api.deleteMeal(entry.id)
    await refresh(true)
  } catch (err) {
    pushToast(err.message, 'error')
  } finally {
    busyMeal.value = null
  }
}

async function swapMeal(meal) {
  busyMeal.value = meal.id
  try {
    const updated = await api.swapMeal(meal.id)
    await refresh(true)
    pushToast(`Swapped for ${updated.food.name}`, 'success')
  } catch (err) {
    pushToast(err.message, 'error')
  } finally {
    busyMeal.value = null
  }
}

async function acceptSuggestion(meal) {
  busyMeal.value = meal.id
  try {
    await api.acceptSuggestion(meal.id)
    await refresh(true)
    pushToast(`${meal.food.name} added to your menu`, 'success')
  } catch (err) {
    pushToast(err.message, 'error')
  } finally {
    busyMeal.value = null
  }
}

async function addWater(delta) {
  logging.value = true
  try {
    await api.logWater({ date: today, ml: delta })
    await refresh(true)
  } catch (err) {
    pushToast(err.message, 'error')
  } finally {
    logging.value = false
  }
}

onMounted(() => refresh(true))
</script>
