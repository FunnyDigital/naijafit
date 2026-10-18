<template>
  <nav
    class="safe-bottom fixed inset-x-0 bottom-0 z-40 border-t border-line bg-surface/95 backdrop-blur md:hidden"
  >
    <ul class="mx-auto grid max-w-lg grid-cols-5">
      <li v-for="tab in tabs" :key="tab.name">
        <RouterLink
          :to="tab.to"
          class="relative flex flex-col items-center gap-1 px-1 pb-2 pt-2.5 text-[11px] font-medium transition-colors duration-200"
          :class="isActive(tab) ? 'text-accent-700' : 'text-ink-muted'"
        >
          <span
            class="absolute inset-x-4 top-0 h-0.5 origin-center rounded-full bg-accent transition-transform duration-300"
            :class="isActive(tab) ? 'scale-x-100' : 'scale-x-0'"
          />
          <span
            class="transition-transform duration-300"
            :class="isActive(tab) ? '-translate-y-px scale-110' : ''"
          >
            <Icon :name="tab.icon" :size="21" :stroke-width="isActive(tab) ? 2.2 : 1.75" />
          </span>
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
