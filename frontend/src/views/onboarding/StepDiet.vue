<template>
  <div>
    <h1 class="font-display text-2xl font-semibold tracking-tight sm:text-3xl">Anything to avoid?</h1>
    <p class="mt-1.5 text-sm text-ink-muted">
      Pick any that apply and we’ll only plan dishes that fit. Leave blank if you eat everything.
    </p>

    <div class="mt-6 grid gap-2.5">
      <ChoiceCard
        v-for="item in options.dietary_flags"
        :key="item.value"
        :label="item.label"
        :hint="item.hint"
        :icon="ICONS[item.value] || 'leaf'"
        :selected="form.dietary_flags.includes(item.value)"
        @select="toggleFlag(item.value)"
      />
    </div>

    <p class="mt-5 rounded-xl2 bg-accent-50 px-4 py-3 text-xs leading-relaxed text-accent-800">
      Your meal plan is built from a library of {{ foodCount }} Nigerian dishes with real
      per-serving nutrition. You can add your own family dishes later from the Foods screen and
      they’ll be used in future plans.
    </p>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'

import ChoiceCard from '../../components/ChoiceCard.vue'
import { api } from '../../services/api'
import { useOnboarding } from '../../composables/useOnboarding'

const { form, optionsState } = useOnboarding()
const options = computed(() => optionsState.data || { dietary_flags: [] })

const ICONS = { vegetarian: 'leaf', gluten_free: 'bowl', lactose_free: 'droplet' }

const foodCount = ref(0)

function toggleFlag(value) {
  const set = new Set(form.dietary_flags)
  if (set.has(value)) set.delete(value)
  else set.add(value)
  form.dietary_flags = [...set]
}

onMounted(async () => {
  try {
    const data = await api.getFoods({ limit: 1 })
    foodCount.value = data.count
  } catch {
    foodCount.value = 0
  }
})
</script>
