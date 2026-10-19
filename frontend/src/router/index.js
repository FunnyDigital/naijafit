import { createRouter, createWebHistory } from 'vue-router'

import { authState, checkSession } from '../composables/useAuth'
import { loadProfile } from '../composables/useProfile'

import Login from '../views/Login.vue'
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
  { path: '/login', name: 'Login', component: Login, meta: { bare: true, public: true } },
  { path: '/onboarding', name: 'Onboarding', component: Onboarding, meta: { bare: true } },
  { path: '/', name: 'Today', component: Today },
  { path: '/workouts', name: 'Workouts', component: Workouts },
  { path: '/workouts/:day', name: 'WorkoutDetail', component: WorkoutDetail, props: true },
  { path: '/meals', name: 'Meals', component: Meals },
  { path: '/foods', name: 'Foods', component: Foods },
  { path: '/foods/:id', name: 'FoodDetail', component: FoodDetail, props: true },
  { path: '/progress', name: 'Progress', component: Progress },
  { path: '/profile', name: 'Profile', component: ProfileView },
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
  // checkSession() resolves once and then short-circuits, so this is cheap on
  // every navigation and can't race itself.
  await checkSession()

  if (to.meta.public) {
    if (authState.user) {
      return { path: typeof to.query.redirect === 'string' ? to.query.redirect : '/' }
    }
    return true
  }

  if (!authState.user) {
    return { name: 'Login', query: to.fullPath === '/' ? {} : { redirect: to.fullPath } }
  }

  const state = await loadProfile()

  // Server unreachable and nothing cached: let the screen show its own error
  // rather than bouncing somebody through setup again.
  if (state.error && !state.profile) return true

  if (!state.onboarded && to.name !== 'Onboarding') {
    return { name: 'Onboarding', query: { redirect: to.fullPath } }
  }
  return true
})

export default router
