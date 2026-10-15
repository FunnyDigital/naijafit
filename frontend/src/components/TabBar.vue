<template>
  <nav
    class="safe-bottom fixed inset-x-0 bottom-0 z-40 border-t border-line bg-surface/95 backdrop-blur md:hidden"
  >
    <ul class="mx-auto grid max-w-lg grid-cols-5">
      <li v-for="tab in tabs" :key="tab.name">
        <RouterLink
          :to="tab.to"
          class="flex flex-col items-center gap-1 px-1 pb-2 pt-2.5 text-[11px] font-medium transition-colors"
          :class="isActive(tab) ? 'text-accent-700' : 'text-ink-muted'"
        >
          <Icon :name="tab.icon" :size="21" :stroke-width="isActive(tab) ? 2.1 : 1.75" />
          {{ tab.label }}
        </RouterLink>
      </li>
    </ul>
  </nav>
</template>

<script setup>
import { useRoute } from 'vue-router'

import Icon from './Icon.vue'

const route = useRoute()

const tabs = [
  { name: 'Today', label: 'Today', to: '/', icon: 'home' },
  { name: 'Workouts', label: 'Workouts', to: '/workouts', icon: 'dumbbell' },
  { name: 'Meals', label: 'Meals', to: '/meals', icon: 'bowl' },
  { name: 'Progress', label: 'Progress', to: '/progress', icon: 'chart' },
  { name: 'Profile', label: 'Profile', to: '/profile', icon: 'user' },
]

function isActive(tab) {
  if (tab.name === 'Today') return route.name === 'Today'
  if (tab.name === 'Workouts') return route.name === 'Workouts' || route.name === 'WorkoutDetail'
  return route.name === tab.name
}
</script>
