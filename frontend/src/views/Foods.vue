<template>
  <div class="mx-auto w-full max-w-4xl px-4 py-5 sm:px-6 sm:py-7">
    <div class="flex flex-wrap items-end justify-between gap-3">
      <div>
        <h1 class="font-display text-2xl font-semibold tracking-tight sm:text-3xl">Food</h1>
        <p class="mt-1 text-sm text-ink-muted">
          Pick the Nigerian dishes you actually eat — your meal plan is built from them.
        </p>
      </div>
      <button class="btn-primary btn-sm" @click="openForm()">
        <Icon name="plus" :size="15" /> Add a dish
      </button>
    </div>

    <!-- My menu / All dishes -->
    <div class="mt-4 grid grid-cols-2 gap-1 rounded-full border border-line bg-surface p-1">
      <button
        v-for="option in tabs"
        :key="option.value"
        class="flex items-center justify-center gap-1.5 rounded-full py-2 text-sm font-medium transition-all duration-300 active:scale-[0.98]"
        :class="tab === option.value ? 'bg-accent text-white shadow-soft' : 'text-ink-soft'"
        @click="tab = option.value"
      >
        <Icon :name="option.icon" :size="15" />
        {{ option.label }}
        <span
          v-if="option.value === 'menu'"
          class="rounded-full px-1.5 text-[10px] font-bold"
          :class="tab === 'menu' ? 'bg-white/25' : 'bg-accent-50 text-accent-700'"
        >
          {{ menu.liked_count }}
        </span>
      </button>
    </div>

    <!-- Suggestions -->
    <section v-if="tab === 'menu' && suggestions.length" class="mt-4" v-reveal>
      <div class="mb-2 flex items-center justify-between gap-2">
        <p class="text-sm font-semibold uppercase tracking-wide text-ink-muted">
          Suggested for you
        </p>
        <button
          class="inline-flex items-center gap-1 text-xs font-medium text-accent-700 transition-opacity hover:opacity-70"
          :disabled="loadingSuggestions"
          @click="loadSuggestions(true)"
        >
          <Icon name="refresh" :size="13" :class="loadingSuggestions ? 'animate-spin' : ''" />
          Shuffle
        </button>
      </div>

      <div class="flex gap-3 overflow-x-auto no-scrollbar pb-1">
        <article
          v-for="(item, index) in suggestions"
          :key="item.id"
          class="card w-56 shrink-0 p-3 anim-fade-up"
          :style="{ animationDelay: `${index * 45}ms` }"
        >
          <div class="flex items-start gap-2">
            <FoodTile :food="item" size="sm" />
            <div class="min-w-0">
              <p class="truncate text-sm font-semibold text-ink">{{ item.name }}</p>
              <p class="line-clamp-2 text-[11px] leading-snug text-accent-700">{{ item.reason }}</p>
            </div>
          </div>
          <div class="mt-2.5 flex items-center justify-between gap-2">
            <span class="text-[11px] text-ink-muted">{{ Math.round(item.kcal) }} kcal</span>
            <button class="btn-soft btn-sm !px-2.5 !py-1.5" @click="addFromSuggestion(item)">
              <Icon name="plus" :size="13" /> Add
            </button>
          </div>
        </article>
      </div>
    </section>

    <!-- Search + filters -->
    <div class="mt-4 space-y-3">
      <div class="relative">
        <Icon
          name="search"
          :size="17"
          class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-ink-faint"
        />
        <input
          v-model="search"
          class="field pl-9"
          placeholder="Search jollof, egusi, moi moi…"
          type="search"
        />
      </div>

      <div class="flex gap-2 overflow-x-auto no-scrollbar pb-1">
        <button class="chip shrink-0" :class="{ 'chip-active': !category }" @click="category = ''">
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

    <template v-else>
      <p v-if="tab === 'menu'" class="mt-4 text-xs text-ink-faint">
        Your plan uses {{ menuSummary }}. Anything you haven’t picked can still show up as a “try
        this” suggestion — tap the tick to keep it for good.
      </p>

      <EmptyState
        v-if="!visible.length && tab === 'menu'"
        class="mt-6"
        icon="bookmark"
        title="Your menu is empty"
        :text="
          search || category
            ? 'Nothing here matches that filter. Try clearing it, or switch to All dishes.'
            : 'Switch to All dishes and tick the Nigerian foods you eat. Your plan is built from them.'
        "
      >
        <button class="btn-primary btn-sm" @click="tab = 'all'">
          Browse all dishes <Icon name="arrowRight" :size="14" />
        </button>
      </EmptyState>

      <EmptyState
        v-else-if="!visible.length"
        class="mt-6"
        icon="search"
        title="Nothing matched"
        text="Try a different name or category."
      />

      <TransitionGroup v-else tag="div" name="list" class="mt-4 space-y-2">
        <DishRow
          v-for="food in visible"
          :key="food.id"
          :food="food"
          :kcal="food.kcal"
          :protein="food.protein_g"
          :carbs="food.carbs_g"
          :fat="food.fat_g"
          :to="`/foods/${food.id}`"
        >
          <template #actions>
            <button
              class="icon-btn"
              :class="isLiked(food) ? '!text-accent-700' : '!text-ink-faint'"
              :title="isLiked(food) ? 'On your menu — tap to remove' : 'Add to my menu'"
              :disabled="busy === food.id"
              @click.prevent.stop="toggleMenu(food)"
            >
              <Icon
                :name="isLiked(food) ? 'circleCheck' : 'plus'"
                :size="19"
                :stroke-width="isLiked(food) ? 2.2 : 1.9"
              />
            </button>
            <button
              v-if="food.is_custom"
              class="icon-btn"
              title="Edit this dish"
              @click.prevent.stop="openForm(food)"
            >
              <Icon name="edit" :size="17" />
            </button>
          </template>
        </DishRow>
      </TransitionGroup>
    </template>

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
            <input v-model.number="draft.kcal" class="field" type="number" min="0" inputmode="decimal" />
          </div>
          <div>
            <label class="label">Protein g</label>
            <input v-model.number="draft.protein_g" class="field" type="number" min="0" step="0.1" inputmode="decimal" />
          </div>
          <div>
            <label class="label">Carbs g</label>
            <input v-model.number="draft.carbs_g" class="field" type="number" min="0" step="0.1" inputmode="decimal" />
          </div>
          <div>
            <label class="label">Fat g</label>
            <input v-model.number="draft.fat_g" class="field" type="number" min="0" step="0.1" inputmode="decimal" />
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
        <div class="flex items-center justify-between gap-2">
          <button
            v-if="editing"
            class="btn-danger btn-sm"
            :disabled="saving"
            @click="removeDish"
          >
            <Icon name="trash" :size="15" /> Delete
          </button>
          <span v-else />

          <div class="flex items-center gap-2">
            <button class="btn-ghost btn-sm" @click="closeForm">Cancel</button>
            <button class="btn-primary btn-sm" :disabled="saving || !draft.name" @click="save">
              <Icon name="check" :size="15" /> {{ saving ? 'Saving…' : 'Save dish' }}
            </button>
          </div>
        </div>
      </template>
    </Sheet>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'

import DishRow from '../components/DishRow.vue'
import EmptyState from '../components/EmptyState.vue'
import FoodTile from '../components/FoodTile.vue'
import Icon from '../components/Icon.vue'
import LoadingState from '../components/LoadingState.vue'
import Sheet from '../components/Sheet.vue'
import { api } from '../services/api'
import { pushToast } from '../composables/useToast'

const SLOTS = ['breakfast', 'lunch', 'dinner', 'snack']

const tabs = [
  { value: 'menu', label: 'My menu', icon: 'bookmark' },
  { value: 'all', label: 'All dishes', icon: 'list' },
]

const tab = ref('menu')
const foods = ref([])
const categories = ref([])
const allCategories = ref([])
const suggestions = ref([])
const loading = ref(true)
const loadingSuggestions = ref(false)
const saving = ref(false)
const busy = ref(null)
const search = ref('')
const category = ref('')

const menu = reactive({ liked_ids: [], liked_count: 0, using_menu: false, catalog_size: 0 })

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

const likedSet = computed(() => new Set(menu.liked_ids.map(Number)))

const menuSummary = computed(() => {
  const count = menu.liked_count
  if (count === 0) return 'nothing yet'
  if (count === 1) return 'this one dish'
  return `these ${count} dishes`
})

function isLiked(food) {
  return likedSet.value.has(Number(food.id))
}

const visible = computed(() => {
  const term = search.value.trim().toLowerCase()
  return foods.value.filter((food) => {
    if (tab.value === 'menu' && !isLiked(food)) return false
    if (category.value && food.category !== category.value) return false
    if (term && !food.name.toLowerCase().includes(term)) return false
    return true
  })
})

async function load() {
  loading.value = true
  try {
    const [foodData, menuData] = await Promise.all([
      api.getFoods({ limit: 500 }),
      api.getMenu(),
    ])
    foods.value = foodData.items || []
    categories.value = foodData.categories || []
    allCategories.value = foodData.categories || []
    Object.assign(menu, menuData)
    await loadSuggestions()
  } catch (error) {
    pushToast(error.message, 'error')
  } finally {
    loading.value = false
  }
}

async function loadSuggestions(shuffle = false) {
  loadingSuggestions.value = true
  try {
    const data = await api.getMenuSuggestions(6)
    if (shuffle) {
      // nudge the server's deterministic pick so "Shuffle" actually changes it
      data.items.sort(() => Math.random() - 0.5)
    }
    suggestions.value = data.items || []
  } catch {
    suggestions.value = []
  } finally {
    loadingSuggestions.value = false
  }
}

function applyMenu(result) {
  if (!result) return
  menu.liked_ids = result.liked_ids || []
  menu.liked_count = result.liked_count || 0
  menu.using_menu = !!result.using_menu
}

async function toggleMenu(food) {
  busy.value = food.id
  try {
    if (isLiked(food)) {
      applyMenu(await api.clearMenuItem(food.id))
      pushToast(`${food.name} removed`, 'info')
    } else {
      applyMenu(await api.setMenuItem(food.id, 'liked'))
      pushToast(`${food.name} added to your menu`, 'success')
    }
    await loadSuggestions()
  } catch (error) {
    pushToast(error.message, 'error')
  } finally {
    busy.value = null
  }
}

async function addFromSuggestion(item) {
  busy.value = item.id
  try {
    applyMenu(await api.setMenuItem(item.id, 'liked'))
    suggestions.value = suggestions.value.filter((entry) => entry.id !== item.id)
    pushToast(`${item.name} added`, 'success')
  } catch (error) {
    pushToast(error.message, 'error')
  } finally {
    busy.value = null
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
    let saved
    if (editing.value) saved = await api.updateFood(editing.value.id, payload)
    else saved = await api.createFood(payload)

    closeForm()
    await load()
    if (saved && !editing.value) applyMenu(await api.setMenuItem(saved.id, 'liked'))
    pushToast(editing.value ? 'Dish updated' : 'Dish added to your menu', 'success')
  } catch (error) {
    pushToast(error.message, 'error')
  } finally {
    saving.value = false
  }
}

async function removeDish() {
  if (!editing.value) return
  saving.value = true
  try {
    await api.deleteFood(editing.value.id)
    closeForm()
    await load()
    pushToast('Dish deleted', 'success')
  } catch (error) {
    pushToast(error.message, 'error')
  } finally {
    saving.value = false
  }
}

watch(tab, (value) => {
  if (value === 'all') category.value = ''
})

onMounted(load)
</script>
