import { createRouter, createWebHistory } from 'vue-router'

import { loadProfile } from '../composables/useProfile'

import Today from '../views/Today.vue'
import Workouts from '../views/Workouts.vue'
import WorkoutDetail from '../views/WorkoutDetail.vue'
import Meals from '../views/Meals.vue'
import Foods from '../views/Foods.vue'
import FoodDetail from '../views/FoodDetail.vue'
import Progress from '../views/Progress.vue'
import ProfileView from '../views/Profile.vue'
import Onboarding from '../views/Onboarding.vue'
import NotFound from '../views/NotFound.vue'

const routes = [
  { path: '/', name: 'Today', component: Today },
  { path: '/workouts', name: 'Workouts', component: Workouts },
  { path: '/workouts/:day', name: 'WorkoutDetail', component: WorkoutDetail, props: true },
  { path: '/meals', name: 'Meals', component: Meals },
  { path: '/foods', name: 'Foods', component: Foods },
  { path: '/foods/:id', name: 'FoodDetail', component: FoodDetail, props: true },
  { path: '/progress', name: 'Progress', component: Progress },
  { path: '/profile', name: 'Profile', component: ProfileView },
  { path: '/onboarding', name: 'Onboarding', component: Onboarding, meta: { bare: true } },
  { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach(async (to) => {
  if (to.meta.bare) return true
  const state = await loadProfile()
  // If the API is unreachable, don't trap the user on the onboarding screen.
  if (state.error) return true
  if (!state.onboarded) {
    return { name: 'Onboarding', query: { redirect: to.fullPath } }
  }
  return true
})

export default router
