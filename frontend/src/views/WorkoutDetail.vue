<template>
  <div class="mx-auto w-full max-w-3xl px-4 py-5 sm:px-6 sm:py-7">
    <RouterLink
      to="/workouts"
      class="inline-flex items-center gap-1.5 text-sm font-medium text-ink-muted transition-colors hover:text-ink"
    >
      <Icon name="arrowLeft" :size="16" /> Your week
    </RouterLink>

    <div v-if="loading" class="mt-5">
      <LoadingState :rows="4" />
    </div>

    <template v-else-if="workout">
      <div class="mt-4 flex flex-wrap items-end justify-between gap-3">
        <div>
          <p class="text-sm text-ink-muted">{{ WEEKDAYS[workout.day_index] }}</p>
          <h1 class="font-display text-2xl font-semibold tracking-tight sm:text-3xl">
            {{ workout.title }}
          </h1>
          <p class="mt-1 text-sm text-ink-muted">{{ workout.focus }}</p>
        </div>
        <div v-if="!workout.is_rest_day" class="flex items-center gap-2">
          <span class="pill"><Icon name="timer" :size="14" /> {{ workout.est_minutes }} min</span>
          <span class="pill"><Icon name="list" :size="14" /> {{ workout.total_exercises }} moves</span>
        </div>
      </div>

      <div v-if="workout.is_rest_day" class="card mt-6 flex flex-col items-center px-6 py-10 text-center">
        <span class="flex h-14 w-14 items-center justify-center rounded-full bg-accent-50 text-accent-700">
          <Icon name="heart" :size="26" />
        </span>
        <p class="mt-4 font-display text-lg font-semibold text-ink">Rest and recover</p>
        <p class="mt-1 max-w-sm text-sm text-ink-muted">
          Nothing scheduled. Walk, stretch, sleep well — this is where the progress actually happens.
        </p>
        <RouterLink to="/workouts" class="btn-ghost btn-sm mt-5">See the other days</RouterLink>
      </div>

      <template v-else>
        <div class="mt-6 space-y-6">
          <div v-for="section in sections" :key="section.key">
            <div class="mb-2 flex items-center gap-2">
              <span class="flex h-7 w-7 items-center justify-center rounded-full bg-accent-50 text-accent-700">
                <Icon :name="section.icon" :size="15" />
              </span>
              <p class="text-sm font-semibold uppercase tracking-wide text-ink-muted">
                {{ section.label }}
              </p>
            </div>
            <div class="space-y-2">
              <ExerciseRow v-for="item in section.items" :key="item.id" :item="item" />
            </div>
          </div>
        </div>

        <div class="mt-7 flex flex-wrap items-center gap-2">
          <button v-if="!done" class="btn-primary" :disabled="saving" @click="complete">
            <Icon name="check" :size="16" /> Mark workout complete
          </button>
          <button v-else class="btn-soft" :disabled="saving" @click="undo">
            <Icon name="check" :size="16" /> Completed · tap to undo
          </button>
          <RouterLink to="/meals" class="btn-ghost">See today’s meals</RouterLink>
        </div>
      </template>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'

import ExerciseRow from '../components/ExerciseRow.vue'
import Icon from '../components/Icon.vue'
import LoadingState from '../components/LoadingState.vue'
import { api } from '../services/api'
import { loadDashboard } from '../composables/useDashboard'
import { pushToast } from '../composables/useToast'
import { WEEKDAYS, todayISO } from '../utils/dates'

const props = defineProps({
  day: { type: [String, Number], required: true },
})

const SECTION_ORDER = [
  { key: 'warmup', label: 'Warm-up', icon: 'sparkles' },
  { key: 'main', label: 'Main block', icon: 'dumbbell' },
  { key: 'finisher', label: 'Finisher', icon: 'flame' },
  { key: 'cooldown', label: 'Cool-down', icon: 'heart' },
]

const workout = ref(null)
const loading = ref(true)
const saving = ref(false)
const done = ref(false)

const sections = computed(() => {
  const items = workout.value?.items || []
  return SECTION_ORDER.map((section) => ({
    ...section,
    items: items.filter((item) => item.section === section.key),
  })).filter((section) => section.items.length)
})

async function load() {
  loading.value = true
  try {
    workout.value = await api.getWorkout(Number(props.day))
    const dash = await loadDashboard(null, true)
    done.value = !!dash?.workout_done && dash.weekday_index === Number(props.day)
  } catch (error) {
    pushToast(error.message, 'error')
  } finally {
    loading.value = false
  }
}

async function complete() {
  saving.value = true
  try {
    await api.logWorkout({
      date: todayISO(),
      day_index: Number(props.day),
      title: workout.value.title,
      duration_min: workout.value.est_minutes,
    })
    done.value = true
    await loadDashboard(null, true)
    pushToast('Workout logged. Nice one.', 'success')
  } catch (error) {
    pushToast(error.message, 'error')
  } finally {
    saving.value = false
  }
}

async function undo() {
  saving.value = true
  try {
    await api.deleteWorkout(todayISO())
    done.value = false
    await loadDashboard(null, true)
  } catch (error) {
    pushToast(error.message, 'error')
  } finally {
    saving.value = false
  }
}

watch(() => props.day, load)
onMounted(load)
</script>
