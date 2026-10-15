<template>
  <div class="mx-auto w-full max-w-3xl px-4 py-5 sm:px-6 sm:py-7">
    <RouterLink
      to="/foods"
      class="inline-flex items-center gap-1.5 text-sm font-medium text-ink-muted transition-colors hover:text-ink"
    >
      <Icon name="arrowLeft" :size="16" /> Food library
    </RouterLink>

    <div v-if="loading" class="mt-5">
      <LoadingState :rows="3" />
    </div>

    <template v-else-if="food">
      <div class="mt-4 flex items-start gap-4">
        <FoodTile :food="food" size="lg" />
        <div class="min-w-0 flex-1">
          <span class="pill capitalize">{{ food.category }}</span>
          <h1 class="mt-1.5 font-display text-2xl font-semibold tracking-tight">{{ food.name }}</h1>
          <p v-if="food.name_local && food.name_local !== food.name" class="text-sm text-ink-muted">
            also called {{ food.name_local }}
          </p>
          <p class="mt-1 text-sm text-ink-muted">{{ food.serving_desc }}</p>
        </div>
      </div>

      <div v-if="food.notes" class="mt-5 rounded-xl2 bg-accent-50 px-4 py-3 text-sm leading-relaxed text-accent-800">
        {{ food.notes }}
      </div>

      <section class="card mt-5 p-4">
        <p class="section-title text-base">Per serving</p>
        <dl class="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div v-for="row in nutrition" :key="row.label" class="rounded-xl bg-canvas px-3 py-2.5">
            <dd class="font-display text-lg font-semibold text-ink">{{ row.value }}</dd>
            <dt class="text-[11px] uppercase tracking-wide text-ink-muted">{{ row.label }}</dt>
          </div>
        </dl>
        <div v-if="food.tags?.length" class="mt-3 flex flex-wrap gap-1.5">
          <span v-for="tag in food.tags" :key="tag" class="chip !py-0.5 text-[11px] capitalize">
            {{ tag.replace('_', ' ') }}
          </span>
        </div>
      </section>

      <section class="card mt-4 p-4">
        <p class="section-title text-base">Log this to today</p>
        <div class="mt-3 flex flex-wrap items-end gap-3">
          <div>
            <label class="label">Meal</label>
            <select v-model="slot" class="field w-36">
              <option v-for="item in SLOTS" :key="item" :value="item" class="capitalize">{{ item }}</option>
            </select>
          </div>
          <div>
            <span class="label">Servings</span>
            <div class="flex items-center gap-1 rounded-lg border border-line bg-surface px-1 py-1">
              <button class="icon-btn !h-7 !w-7" @click="servings = Math.max(0.5, servings - 0.5)">
                <Icon name="minus" :size="15" />
              </button>
              <span class="w-10 text-center text-sm font-semibold">{{ servings }}</span>
              <button class="icon-btn !h-7 !w-7" @click="servings = Math.min(10, servings + 0.5)">
                <Icon name="plus" :size="15" />
              </button>
            </div>
          </div>
          <button class="btn-primary btn-sm" :disabled="logging" @click="logIt">
            <Icon name="check" :size="15" /> {{ logging ? 'Logging…' : 'Log it' }}
          </button>
        </div>
        <p class="mt-2 text-xs text-ink-faint">
          That’s {{ Math.round(food.kcal * servings) }} kcal and
          {{ Math.round(food.protein_g * servings) }}g protein.
        </p>
      </section>

      <div v-if="food.is_custom" class="mt-4 flex flex-wrap gap-2">
        <RouterLink to="/foods" class="btn-ghost btn-sm" @click="editSoon">
          <Icon name="edit" :size="15" /> Edit in library
        </RouterLink>
        <button class="btn-danger btn-sm" :disabled="deleting" @click="remove">
          <Icon name="trash" :size="15" /> Delete dish
        </button>
      </div>
    </template>

    <EmptyState v-else icon="search" title="That dish isn’t here" text="It may have been removed." />
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import EmptyState from '../components/EmptyState.vue'
import FoodTile from '../components/FoodTile.vue'
import Icon from '../components/Icon.vue'
import LoadingState from '../components/LoadingState.vue'
import { api } from '../services/api'
import { pushToast } from '../composables/useToast'
import { loadDashboard } from '../composables/useDashboard'
import { todayISO } from '../utils/dates'

const SLOTS = ['breakfast', 'lunch', 'dinner', 'snack']

const props = defineProps({
  id: { type: [String, Number], required: true },
})

const router = useRouter()
const food = ref(null)
const loading = ref(true)
const logging = ref(false)
const deleting = ref(false)
const slot = ref('lunch')
const servings = ref(1)

const nutrition = computed(() => {
  if (!food.value) return []
  return [
    { label: 'Calories', value: `${Math.round(food.value.kcal)}` },
    { label: 'Protein', value: `${food.value.protein_g}g` },
    { label: 'Carbs', value: `${food.value.carbs_g}g` },
    { label: 'Fat', value: `${food.value.fat_g}g` },
    { label: 'Fibre', value: `${food.value.fiber_g}g` },
    { label: 'Sodium', value: `${Math.round(food.value.sodium_mg)}mg` },
    { label: 'Weight', value: `${Math.round(food.value.serving_grams)}g` },
  ]
})

async function load() {
  loading.value = true
  try {
    food.value = await api.getFood(props.id)
  } catch (error) {
    food.value = null
  } finally {
    loading.value = false
  }
}

async function logIt() {
  logging.value = true
  try {
    await api.logMeal({ date: todayISO(), slot: slot.value, food_id: food.value.id, servings: servings.value })
    await loadDashboard(null, true)
    pushToast('Added to today', 'success')
  } catch (error) {
    pushToast(error.message, 'error')
  } finally {
    logging.value = false
  }
}

async function remove() {
  deleting.value = true
  try {
    await api.deleteFood(food.value.id)
    pushToast('Dish removed', 'success')
    router.push('/foods')
  } catch (error) {
    pushToast(error.message, 'error')
  } finally {
    deleting.value = false
  }
}

function editSoon() {
  pushToast('Open the dish from the library to edit it')
}

onMounted(load)
</script>
