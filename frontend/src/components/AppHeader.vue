<template>
  <header class="sticky top-0 z-40 border-b border-line bg-canvas/85 backdrop-blur">
    <div class="mx-auto flex h-14 w-full max-w-6xl items-center justify-between gap-3 px-4 sm:h-16 sm:px-6">
      <RouterLink to="/" class="flex min-w-0 items-center gap-2.5 text-ink">
        <span class="flex h-9 w-9 items-center justify-center rounded-full bg-accent text-white">
          <Icon name="pulse" :size="19" :stroke-width="2" />
        </span>
        <span class="truncate font-display text-lg font-semibold tracking-tight">NaijaFit</span>
      </RouterLink>

      <nav class="hidden items-center gap-1 md:flex">
        <RouterLink
          v-for="link in links"
          :key="link.name"
          :to="link.to"
          class="rounded-full px-3.5 py-2 text-sm font-medium text-ink-soft transition-colors hover:bg-accent-50 hover:text-accent-700"
          :class="{ 'bg-accent-50 text-accent-700': route.name === link.name }"
        >
          {{ link.label }}
        </RouterLink>
      </nav>

      <div class="flex items-center gap-1.5">
        <span
          v-if="streak > 0"
          class="hidden items-center gap-1.5 rounded-full bg-warm-50 px-3 py-1.5 text-xs font-semibold text-warm xs:inline-flex"
          :title="`${streak} day streak`"
        >
          <Icon name="flame" :size="15" />
          {{ streak }}
        </span>
        <RouterLink to="/profile" class="icon-btn" aria-label="Profile">
          <Icon name="user" :size="19" />
        </RouterLink>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import Icon from './Icon.vue'
import { dashboardState } from '../composables/useDashboard'

const route = useRoute()

const links = [
  { name: 'Today', label: 'Today', to: '/' },
  { name: 'Workouts', label: 'Workouts', to: '/workouts' },
  { name: 'Meals', label: 'Meals', to: '/meals' },
  { name: 'Foods', label: 'Foods', to: '/foods' },
  { name: 'Progress', label: 'Progress', to: '/progress' },
]

const streak = computed(() => dashboardState.data?.streak || 0)
</script>
