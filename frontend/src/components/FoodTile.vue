<template>
  <div
    class="relative flex shrink-0 items-center justify-center overflow-hidden rounded-2xl bg-gradient-to-br"
    :class="[style.bg, style.fg, sizeClass]"
  >
    <img
      v-if="food && food.photo_url"
      :src="food.photo_url"
      :alt="food.name"
      class="absolute inset-0 h-full w-full object-cover"
      loading="lazy"
    />
    <Icon v-else :name="style.icon" :size="iconSize" :stroke-width="1.6" />
    <span
      v-if="food && food.is_custom && showBadge"
      class="absolute right-1 top-1 rounded-full bg-white/85 px-1.5 text-[9px] font-semibold text-ink-muted"
    >
      Yours
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

import Icon from './Icon.vue'

const props = defineProps({
  food: { type: Object, default: null },
  size: { type: String, default: 'md' }, // sm | md | lg
  showBadge: { type: Boolean, default: true },
})

const STYLES = {
  breakfast: { bg: 'from-amber-100 to-amber-50', fg: 'text-amber-600', icon: 'egg' },
  swallow: { bg: 'from-stone-200 to-stone-100', fg: 'text-stone-600', icon: 'bowl' },
  soup: { bg: 'from-emerald-100 to-emerald-50', fg: 'text-emerald-600', icon: 'utensils' },
  stew: { bg: 'from-orange-100 to-orange-50', fg: 'text-orange-600', icon: 'utensils' },
  rice: { bg: 'from-lime-100 to-lime-50', fg: 'text-lime-700', icon: 'bowl' },
  porridge: { bg: 'from-teal-100 to-teal-50', fg: 'text-teal-600', icon: 'bowl' },
  protein: { bg: 'from-rose-100 to-rose-50', fg: 'text-rose-600', icon: 'fish' },
  side: { bg: 'from-green-100 to-green-50', fg: 'text-green-700', icon: 'leaf' },
  snack: { bg: 'from-yellow-100 to-yellow-50', fg: 'text-yellow-700', icon: 'star' },
  fruit: { bg: 'from-pink-100 to-pink-50', fg: 'text-pink-600', icon: 'apple' },
  drink: { bg: 'from-sky-100 to-sky-50', fg: 'text-sky-600', icon: 'droplet' },
}

const FALLBACK = { bg: 'from-accent-100 to-accent-50', fg: 'text-accent-700', icon: 'bowl' }

const style = computed(() => STYLES[props.food?.category] || FALLBACK)

const sizeClass = computed(
  () => ({ sm: 'h-9 w-9 rounded-xl', md: 'h-12 w-12', lg: 'h-20 w-20' })[props.size] || 'h-12 w-12',
)

const iconSize = computed(() => ({ sm: 16, md: 22, lg: 34 })[props.size] || 22)
</script>
