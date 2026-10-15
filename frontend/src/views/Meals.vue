<template>
  <div class="mx-auto w-full max-w-4xl px-4 py-5 sm:px-6 sm:py-7">
    <div class="flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 class="font-display text-2xl font-semibold tracking-tight sm:text-3xl">Meal plan</h1>
        <p class="mt-1 text-sm text-ink-muted">
          Seven days of Nigerian food, built around
          <b class="font-semibold text-ink-soft">{{ targets.calorie_target }} kcal</b> and
          <b class="font-semibold text-ink-soft">{{ targets.protein_g }}g protein</b> a day.
        </p>
      </div>
      <RouterLink to="/foods" class="btn-ghost btn-sm">
        <Icon name="leaf" :size="15" /> Food library
      </RouterLink>
    </div>

    <div v-if="loading" class="mt-5">
      <LoadingState :rows="5" />
    </div>

    <template v-else>
      <div class="mt-5 flex gap-2 overflow-x-auto no-scrollbar pb-1">
        <button
          v-for="day in days"
          :key="day.index"
          class="flex min-w-[4.6rem] flex-col items-center gap-1 rounded-xl2 border px-3 py-2.5 transition-colors"
          :class="
            day.index === selected
              ? 'border-accent bg-accent-50 text-accent-700'
              : 'border-line bg-surface text-ink-soft hover:border-accent/40'
          "
          @click="selected = day.index"
        >
          <span class="text-[11px] font-semibold uppercase tracking-wide">{{ day.label }}</span>
          <span class="font-display text-sm font-semibold">{{ day.kcal }}</span>
          <span class="text-[10px] text-ink-faint">kcal</span>
        </button>
      </div>

      <div class="mt-4 flex items-center justify-between gap-3 rounded-xl2 bg-accent-50 px-4 py-3">
        <div class="text-sm">
          <p class="font-semibold text-accent-800">
            {{ dayTotal }} kcal planned · {{ dayProtein }}g protein
          </p>
          <p class="text-xs text-accent-700">
            Target {{ targets.calorie_target }} kcal · {{ targets.protein_g }}g protein
          </p>
        </div>
        <span
          class="pill !bg-white"
          :class="Math.abs(dayTotal - targets.calorie_target) <= 250 ? '!text-accent-700' : '!text-warm'"
        >
          {{ deltaLabel }}
        </span>
      </div>

      <div class="mt-5 space-y-5">
        <section v-for="group in mealGroups" :key="group.slot" v-reveal="group.order * 40">
          <p class="mb-2 text-sm font-semibold uppercase tracking-wide text-ink-muted">
            {{ group.label }}
          </p>
          <div class="space-y-2">
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
            >
              <template #actions>
                <button
                  class="icon-btn"
                  title="Swap this dish"
                  :disabled="busy === meal.id"
                  @click.prevent.stop="swap(meal)"
                >
                  <Icon name="swap" :size="17" />
                </button>
              </template>
            </DishRow>
          </div>
        </section>
      </div>

      <p class="mt-6 text-center text-xs text-ink-faint">
        Log what you actually eat on the <RouterLink to="/" class="font-medium text-accent-700 hover:underline">Today</RouterLink> screen.
      </p>
    </template>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

import DishRow from '../components/DishRow.vue'
import Icon from '../components/Icon.vue'
import LoadingState from '../components/LoadingState.vue'
import { api } from '../services/api'
import { pushToast } from '../composables/useToast'
import { WEEKDAYS_SHORT, weekdayIndex } from '../utils/dates'

const SLOT_ORDER = ['breakfast', 'lunch', 'dinner', 'snack', 'extra']
const SLOT_LABELS = {
  breakfast: 'Breakfast',
  lunch: 'Lunch',
  dinner: 'Dinner',
  snack: 'Snack',
  extra: 'Protein top-up',
}

const meals = ref([])
const targets = ref({ calorie_target: 0, protein_g: 0 })
const loading = ref(true)
const busy = ref(null)
const selected = ref(weekdayIndex())

const days = computed(() =>
  WEEKDAYS_SHORT.map((label, index) => ({
    index,
    label,
    kcal: Math.round(
      meals.value.filter((meal) => meal.day_index === index).reduce((sum, meal) => sum + meal.kcal, 0),
    ),
  })),
)

const dayMeals = computed(() => meals.value.filter((meal) => meal.day_index === selected.value))
const dayTotal = computed(() => Math.round(dayMeals.value.reduce((sum, meal) => sum + meal.kcal, 0)))
const dayProtein = computed(() => Math.round(dayMeals.value.reduce((sum, meal) => sum + meal.protein_g, 0)))

const deltaLabel = computed(() => {
  const delta = dayTotal.value - targets.value.calorie_target
  if (Math.abs(delta) <= 100) return 'On target'
  return delta > 0 ? `${delta} over` : `${Math.abs(delta)} under`
})

const mealGroups = computed(() =>
  SLOT_ORDER.map((slot, order) => ({
    slot,
    order,
    label: SLOT_LABELS[slot],
    meals: dayMeals.value.filter((meal) => meal.slot === slot),
  })).filter((group) => group.meals.length),
)

async function load() {
  loading.value = true
  try {
    const plan = await api.getPlan()
    meals.value = plan.meals || []
    targets.value = plan.profile?.targets || targets.value
  } catch (error) {
    pushToast(error.message, 'error')
  } finally {
    loading.value = false
  }
}

async function swap(meal) {
  busy.value = meal.id
  try {
    const updated = await api.swapMeal(meal.id)
    const index = meals.value.findIndex((item) => item.id === meal.id)
    if (index !== -1) meals.value[index] = updated
    pushToast(`Swapped for ${updated.food.name}`, 'success')
  } catch (error) {
    pushToast(error.message, 'error')
  } finally {
    busy.value = null
  }
}

onMounted(load)
</script>
