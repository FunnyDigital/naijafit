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
          class="relative rounded-full px-3.5 py-2 text-sm font-medium transition-colors"
          :class="
            isActive(link)
              ? 'bg-accent-50 text-accent-700'
              : 'text-ink-soft hover:bg-accent-50 hover:text-accent-700'
          "
        >
          {{ link.label }}
          <span
            v-if="isActive(link)"
            class="absolute inset-x-3 -bottom-px h-0.5 rounded-full bg-accent"
          />
        </RouterLink>
      </nav>

      <div class="flex items-center gap-1.5">
        <Transition name="pop">
          <span
            v-if="streak > 0"
            class="hidden items-center gap-1.5 rounded-full bg-warm-50 px-3 py-1.5 text-xs font-semibold text-warm xs:inline-flex"
            :title="`${streak} day streak`"
          >
            <Icon name="flame" :size="15" />
            {{ streak }}
          </span>
        </Transition>

        <RouterLink
          to="/profile"
          class="hidden max-w-[10rem] items-center gap-2 rounded-full border border-line bg-surface px-3 py-1.5 text-xs font-medium text-ink-soft transition-colors hover:border-accent hover:text-accent-700 sm:flex"
        >
          <span class="flex h-5 w-5 items-center justify-center rounded-full bg-accent text-[10px] font-bold text-white">
            {{ initial }}
          </span>
          <span class="truncate">{{ username }}</span>
        </RouterLink>

        <RouterLink to="/profile" class="icon-btn sm:hidden" aria-label="Profile">
          <Icon name="user" :size="19" />
        </RouterLink>

        <button class="icon-btn" aria-label="Sign out" title="Sign out" @click="onSignOut">
          <Icon name="logout" :size="19" />
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import Icon from './Icon.vue'
import { authState, signOut } from '../composables/useAuth'
import { resetProfileState } from '../composables/useProfile'
import { dashboardState, resetDashboardState } from '../composables/useDashboard'
import { pushToast } from '../composables/useToast'

const route = useRoute()
const router = useRouter()

const links = [
  { name: 'Today', label: 'Today', to: '/' },
  { name: 'Workouts', label: 'Workouts', to: '/workouts' },
  { name: 'Meals', label: 'Meals', to: '/meals' },
  { name: 'Foods', label: 'Foods', to: '/foods' },
  { name: 'Progress', label: 'Progress', to: '/progress' },
]

const streak = computed(() => dashboardState.data?.streak || 0)
const username = computed(() => authState.user?.username || '')
const initial = computed(() => (username.value || '?').charAt(0).toUpperCase())

function isActive(link) {
  if (link.name === 'Today') return route.name === 'Today'
  if (link.name === 'Workouts') return route.name === 'Workouts' || route.name === 'WorkoutDetail'
  if (link.name === 'Foods') return route.name === 'Foods' || route.name === 'FoodDetail'
  return route.name === link.name
}

function onSignOut() {
  signOut()
  resetProfileState()
  resetDashboardState()
  pushToast('Signed out')
  router.push({ name: 'Login' })
}
</script>

<style scoped>
.pop-enter-active,
.pop-leave-active {
  transition: opacity 0.25s ease, transform 0.25s cubic-bezier(0.2, 0.9, 0.3, 1.4);
}
.pop-enter-from,
.pop-leave-to {
  opacity: 0;
  transform: scale(0.7);
}
</style>
