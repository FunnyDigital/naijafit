<template>
  <div class="mx-auto w-full max-w-4xl px-4 py-5 sm:px-6 sm:py-7">
    <div class="flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 class="font-display text-2xl font-semibold tracking-tight sm:text-3xl">Food library</h1>
        <p class="mt-1 text-sm text-ink-muted">
          {{ count }} Nigerian dishes with per-serving nutrition — the same library your plan is
          built from.
        </p>
      </div>
      <button class="btn-primary btn-sm" @click="openForm()">
        <Icon name="plus" :size="15" /> Add a dish
      </button>
    </div>

    <div class="mt-4 space-y-3">
      <div class="relative">
        <Icon name="search" :size="17" class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-ink-faint" />
        <input
          v-model="search"
          class="field pl-9"
          placeholder="Search jollof, egusi, moi moi…"
          type="search"
        />
      </div>

      <div class="flex gap-2 overflow-x-auto no-scrollbar pb-1">
        <button
          class="chip shrink-0"
          :class="{ 'chip-active': !category }"
          @click="category = ''"
        >
          All
        </button>
        <button
          v-for="item in categories"
          :key="item"
          class="chip shrink-0 capitalize"
          :class="{ 'chip-active': category === item }"
          @click="category = category === item ? '' : item"
        >
          {{ item }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="mt-5">
      <LoadingState :rows="5" />
    </div>

    <div v-else class="mt-4 space-y-2">
      <DishRow
        v-for="food in filtered"
        :key="food.id"
        :food="food"
        :kcal="food.kcal"
        :protein="food.protein_g"
        :carbs="food.carbs_g"
        :fat="food.fat_g"
        :to="`/foods/${food.id}`"
      />
      <EmptyState
        v-if="!filtered.length"
        icon="search"
        title="Nothing matched"
        text="Try a different name or category."
      />
    </div>

    <Sheet :open="showForm" :title="editing ? 'Edit dish' : 'Add a dish'" @close="closeForm">
      <div class="space-y-3">
        <div>
          <label class="label">Name</label>
          <input v-model="draft.name" class="field" placeholder="e.g. Grandma’s ofada" />
        </div>
        <div class="grid grid-cols-2 gap-3">
          <div>
            <label class="label">Category</label>
            <select v-model="draft.category" class="field">
              <option v-for="item in allCategories" :key="item" :value="item" class="capitalize">
                {{ item }}
              </option>
            </select>
          </div>
          <div>
            <label class="label">Serving</label>
            <input v-model="draft.serving_desc" class="field" placeholder="1 cup" />
          </div>
        </div>
        <div>
          <label class="label">Meal slots</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="slot in SLOTS"
              :key="slot"
              class="chip capitalize"
              :class="{ 'chip-active': draft.meal_slots.includes(slot) }"
              @click="toggleSlot(slot)"
            >
              {{ slot }}
            </button>
          </div>
        </div>
        <div class="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <div>
            <label class="label">Kcal</label>
            <input v-model.number="draft.kcal" class="field" type="number" min="0" />
          </div>
          <div>
            <label class="label">Protein g</label>
            <input v-model.number="draft.protein_g" class="field" type="number" min="0" step="0.1" />
          </div>
          <div>
            <label class="label">Carbs g</label>
            <input v-model.number="draft.carbs_g" class="field" type="number" min="0" step="0.1" />
          </div>
          <div>
            <label class="label">Fat g</label>
            <input v-model.number="draft.fat_g" class="field" type="number" min="0" step="0.1" />
          </div>
        </div>
        <div>
          <label class="label">Photo URL (optional)</label>
          <input v-model="draft.photo_url" class="field" placeholder="https://…" />
        </div>
        <div>
          <label class="label">Notes (optional)</label>
          <textarea v-model="draft.notes" class="field" rows="2" placeholder="How it’s cooked, swaps, anything useful." />
        </div>
      </div>

      <template #footer>
        <div class="flex items-center justify-end gap-2">
          <button class="btn-ghost btn-sm" @click="closeForm">Cancel</button>
          <button class="btn-primary btn-sm" :disabled="saving || !draft.name" @click="save">
            <Icon name="check" :size="15" /> {{ saving ? 'Saving…' : 'Save dish' }}
          </button>
        </div>
      </template>
    </Sheet>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'

import DishRow from '../components/DishRow.vue'
import EmptyState from '../components/EmptyState.vue'
import Icon from '../components/Icon.vue'
import LoadingState from '../components/LoadingState.vue'
import Sheet from '../components/Sheet.vue'
import { api } from '../services/api'
import { pushToast } from '../composables/useToast'

const SLOTS = ['breakfast', 'lunch', 'dinner', 'snack']

const foods = ref([])
const categories = ref([])
const allCategories = ref([])
const count = ref(0)
const loading = ref(true)
const saving = ref(false)
const search = ref('')
const category = ref('')

const showForm = ref(false)
const editing = ref(null)

const draft = reactive({
  name: '',
  category: 'protein',
  serving_desc: '1 serving',
  meal_slots: [],
  kcal: 0,
  protein_g: 0,
  carbs_g: 0,
  fat_g: 0,
  photo_url: '',
  notes: '',
})

const filtered = computed(() => {
  const term = search.value.trim().toLowerCase()
  if (!term) return foods.value
  return foods.value.filter((food) => food.name.toLowerCase().includes(term))
})

async function load() {
  loading.value = true
  try {
    const data = await api.getFoods({ limit: 500 })
    foods.value = data.items || []
    categories.value = data.categories || []
    allCategories.value = data.categories || []
    count.value = data.count || 0
  } catch (error) {
    pushToast(error.message, 'error')
  } finally {
    loading.value = false
  }
}

async function loadCategory() {
  try {
    const data = await api.getFoods({ category: category.value || undefined, limit: 500 })
    foods.value = data.items || []
  } catch (error) {
    pushToast(error.message, 'error')
  }
}

function openForm(food = null) {
  editing.value = food
  Object.assign(draft, {
    name: food?.name || '',
    category: food?.category || 'protein',
    serving_desc: food?.serving_desc || '1 serving',
    meal_slots: food?.meal_slots ? [...food.meal_slots] : ['lunch', 'dinner'],
    kcal: food?.kcal ?? 0,
    protein_g: food?.protein_g ?? 0,
    carbs_g: food?.carbs_g ?? 0,
    fat_g: food?.fat_g ?? 0,
    photo_url: food?.photo_url || '',
    notes: food?.notes || '',
  })
  showForm.value = true
}

function closeForm() {
  showForm.value = false
  editing.value = null
}

function toggleSlot(slot) {
  const set = new Set(draft.meal_slots)
  if (set.has(slot)) set.delete(slot)
  else set.add(slot)
  draft.meal_slots = [...set]
}

async function save() {
  saving.value = true
  try {
    const payload = { ...draft, photo_url: draft.photo_url || null, notes: draft.notes || null }
    if (editing.value) await api.updateFood(editing.value.id, payload)
    else await api.createFood(payload)
    closeForm()
    await load()
    pushToast(editing.value ? 'Dish updated' : 'Dish added', 'success')
  } catch (error) {
    pushToast(error.message, 'error')
  } finally {
    saving.value = false
  }
}

watch(category, loadCategory)
watch(search, () => {})
onMounted(load)
</script>
