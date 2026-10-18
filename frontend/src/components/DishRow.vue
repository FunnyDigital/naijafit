<template>
  <div
    class="flex items-center gap-3 rounded-xl2 border border-line bg-surface p-3 transition-colors"
    :class="to ? 'hover:border-accent/50' : ''"
  >
    <component
      :is="to ? 'RouterLink' : 'div'"
      :to="to || undefined"
      class="flex min-w-0 flex-1 items-center gap-3"
    >
      <FoodTile :food="food" :size="size" />

      <div class="min-w-0 flex-1">
        <div class="flex items-center gap-2">
          <p class="truncate text-sm font-semibold text-ink">{{ food.name }}</p>
          <span
            v-if="badge"
            class="shrink-0 rounded-full bg-warm-50 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-warm"
          >
            {{ badge }}
          </span>
          <span
            v-else-if="slot"
            class="shrink-0 rounded-full bg-accent-50 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-accent-700"
          >
            {{ slot }}
          </span>
        </div>

        <p class="truncate text-xs text-ink-muted">
          <template v-if="servings">{{ servings }} × </template>{{ food.serving_desc }}
        </p>

        <div class="mt-1 flex flex-wrap items-center gap-x-2.5 gap-y-1 text-[11px] text-ink-muted">
          <span class="font-semibold text-ink-soft">{{ Math.round(kcal) }} kcal</span>
          <span>P {{ Math.round(protein) }}g</span>
          <span>C {{ Math.round(carbs) }}g</span>
          <span>F {{ Math.round(fat) }}g</span>
        </div>

        <p v-if="paired" class="mt-1 truncate text-[11px] text-accent-700">
          + {{ paired.name }} ({{ paired.serving_desc }})
        </p>
      </div>
    </component>

    <div v-if="$slots.actions" class="flex shrink-0 items-center gap-1">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup>
import FoodTile from './FoodTile.vue'

defineProps({
  food: { type: Object, required: true },
  paired: { type: Object, default: null },
  servings: { type: [Number, String], default: null },
  kcal: { type: Number, default: null },
  protein: { type: Number, default: null },
  carbs: { type: Number, default: null },
  fat: { type: Number, default: null },
  slot: { type: String, default: '' },
  badge: { type: String, default: '' },
  size: { type: String, default: 'md' },
  to: { type: [String, Object], default: null },
})
</script>
