<template>
  <div class="mx-auto w-full max-w-6xl px-4 py-5 sm:px-6 sm:py-7">
    <div class="flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 class="font-display text-2xl font-semibold tracking-tight sm:text-3xl">Your week</h1>
        <p class="mt-1 text-sm text-ink-muted">
          {{ sessions }} sessions · {{ totalMinutes }} minutes · built for {{ levelLabel }} level
        </p>
      </div>
      <button class="btn-ghost btn-sm" :disabled="regenerating" @click="regenerate">
        <Icon name="refresh" :size="15" :class="regenerating ? 'animate-spin' : ''" />
        {{ regenerating ? 'Rebuilding…' : 'New plan' }}
      </button>
    </div>

    <div v-if="loading" class="mt-5">
      <LoadingState :rows="4" />
    </div>

    <div v-else class="mt-5 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
      <RouterLink
        v-for="(workout, index) in workouts"
        :key="workout.day_index"
        v-reveal="index * 40"
        :to="`/workouts/${workout.day_index}`"
        class="card flex flex-col p-4 transition-colors hover:border-accent/50"
        :class="{ 'border-dashed bg-canvas': workout.is_rest_day }"
      >
        <div class="flex items-center justify-between gap-2">
          <span
            class="rounded-full px-2.5 py-1 text-[11px] font-semibold uppercase tracking-wide"
            :class="
              workout.day_index === todayIndex
                ? 'bg-accent text-white'
                : 'bg-accent-50 text-accent-700'
            "
          >
            {{ WEEKDAYS_SHORT[workout.day_index] }}
          </span>
          <span v-if="workout.day_index === todayIndex" class="text-[11px] font-medium text-ink-faint">
            Today
          </span>
        </div>

        <p class="mt-3 font-display text-base font-semibold text-ink">{{ workout.title }}</p>
        <p class="mt-0.5 line-clamp-2 text-xs text-ink-muted">{{ workout.focus }}</p>

        <div class="mt-auto flex items-center gap-3 pt-3 text-[11px] text-ink-muted">
          <template v-if="workout.is_rest_day">
            <Icon name="heart" :size="14" /> Recovery day
          </template>
          <template v-else>
            <span class="inline-flex items-center gap-1"><Icon name="timer" :size="14" /> {{ workout.est_minutes }} min</span>
            <span class="inline-flex items-center gap-1"><Icon name="list" :size="14" /> {{ workout.total_exercises }} moves</span>
          </template>
        </div>
      </RouterLink>
    </div>

    <p v-if="!loading && !workouts.length" class="mt-5 text-sm text-ink-muted">
      No plan yet. Finish onboarding to get one.
    </p>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

import Icon from '../components/Icon.vue'
import LoadingState from '../components/LoadingState.vue'
import { api } from '../services/api'
import { profileState } from '../composables/useProfile'
import { pushToast } from '../composables/useToast'
import { WEEKDAYS_SHORT, weekdayIndex } from '../utils/dates'
import { titleCase } from '../utils/dates'

const workouts = ref([])
const loading = ref(true)
const regenerating = ref(false)

const todayIndex = weekdayIndex()
const levelLabel = computed(() => titleCase(profileState.profile?.level || 'beginner'))

const sessions = computed(() => workouts.value.filter((workout) => !workout.is_rest_day).length)
const totalMinutes = computed(() =>
  workouts.value.reduce((sum, workout) => sum + (workout.est_minutes || 0), 0),
)

async function load() {
  loading.value = true
  try {
    const plan = await api.getPlan()
    workouts.value = plan.workouts || []
  } catch (error) {
    pushToast(error.message, 'error')
  } finally {
    loading.value = false
  }
}

async function regenerate() {
  regenerating.value = true
  try {
    await api.generatePlan()
    await load()
    pushToast('Fresh plan built', 'success')
  } catch (error) {
    pushToast(error.message, 'error')
  } finally {
    regenerating.value = false
  }
}

onMounted(load)
</script>
