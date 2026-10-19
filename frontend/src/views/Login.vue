<template>
  <div class="relative flex h-full flex-col overflow-hidden bg-canvas">
    <div class="pointer-events-none absolute -right-24 -top-24 h-72 w-72 rounded-full bg-accent-100 blur-3xl" />
    <div class="pointer-events-none absolute -bottom-32 -left-24 h-80 w-80 rounded-full bg-accent-50 blur-3xl" />

    <div class="relative flex flex-1 items-center justify-center overflow-y-auto overscroll-contain px-5 py-8">
      <div class="w-full max-w-sm">
        <div class="flex flex-col items-center text-center" v-reveal>
          <span class="flex h-14 w-14 items-center justify-center rounded-2xl bg-accent text-white shadow-lift">
            <Icon name="pulse" :size="28" :stroke-width="2" />
          </span>
          <h1 class="mt-4 font-display text-3xl font-semibold tracking-tight">NaijaFit</h1>
          <p class="mt-1.5 text-sm text-ink-muted">
            Home workouts and Nigerian meal plans, built around your body.
          </p>
        </div>

        <div class="card mt-6 p-5" v-reveal="80">
          <div class="mb-5 grid grid-cols-2 gap-1 rounded-full border border-line bg-canvas p-1">
            <button
              v-for="option in modes"
              :key="option.value"
              class="rounded-full py-2 text-sm font-medium transition-all duration-300"
              :class="mode === option.value ? 'bg-accent text-white shadow-soft' : 'text-ink-soft'"
              @click="switchMode(option.value)"
            >
              {{ option.label }}
            </button>
          </div>

          <form class="space-y-4" @submit.prevent="submit">
            <div>
              <label class="label" for="username">Username</label>
              <input
                id="username"
                v-model="username"
                class="field"
                autocomplete="username"
                autocapitalize="none"
                spellcheck="false"
                placeholder="e.g. ada"
                maxlength="50"
              />
            </div>

            <div>
              <label class="label" for="password">Password</label>
              <input
                id="password"
                v-model="password"
                class="field"
                type="password"
                :autocomplete="mode === 'login' ? 'current-password' : 'new-password'"
                placeholder="At least 6 characters"
                maxlength="128"
              />
            </div>

            <div v-if="mode === 'register'">
              <label class="label" for="confirm">Confirm password</label>
              <input
                id="confirm"
                v-model="confirm"
                class="field"
                type="password"
                autocomplete="new-password"
                maxlength="128"
              />
            </div>

            <Transition name="fade">
              <p
                v-if="error"
                class="flex items-start gap-2 rounded-xl bg-red-50 px-3 py-2.5 text-sm text-red-700"
              >
                <Icon name="alert" :size="16" class="mt-0.5 shrink-0" />
                {{ error }}
              </p>
            </Transition>

            <button class="btn-primary w-full" type="submit" :disabled="!canSubmit || busy">
              <Icon v-if="busy" name="refresh" :size="16" class="animate-spin" />
              <Icon v-else :name="mode === 'login' ? 'login' : 'userPlus'" :size="16" />
              {{ busy ? 'Just a moment…' : mode === 'login' ? 'Sign in' : 'Create my account' }}
            </button>
          </form>

          <p class="mt-4 text-center text-xs leading-relaxed text-ink-faint">
            <template v-if="mode === 'register'">
              Your profile, plan and logs are yours alone — nobody else can see them.
            </template>
            <template v-else>
              New here? Tap <b class="font-semibold text-ink-muted">Create account</b>
              to set up your plan.
            </template>
          </p>
        </div>

        <p class="mt-5 text-center text-xs text-ink-faint">
          Self-hosted · your data stays on your own server
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import Icon from '../components/Icon.vue'
import { login, register } from '../composables/useAuth'
import { loadProfile } from '../composables/useProfile'
import { resetDashboardState } from '../composables/useDashboard'
import { pushToast } from '../composables/useToast'

const router = useRouter()
const route = useRoute()

const modes = [
  { value: 'login', label: 'Sign in' },
  { value: 'register', label: 'Create account' },
]

const mode = ref('login')
const username = ref('')
const password = ref('')
const confirm = ref('')
const error = ref('')
const busy = ref(false)

const canSubmit = computed(() => {
  if (username.value.trim().length < 3 || password.value.length < 6) return false
  if (mode.value === 'register' && confirm.value !== password.value) return false
  return true
})

function switchMode(next) {
  mode.value = next
  error.value = ''
}

async function submit() {
  error.value = ''
  if (mode.value === 'register' && confirm.value !== password.value) {
    error.value = 'Those two passwords don’t match'
    return
  }

  busy.value = true
  try {
    if (mode.value === 'login') {
      await login(username.value.trim(), password.value)
    } else {
      await register(username.value.trim(), password.value)
      pushToast(`Welcome, ${username.value.trim()}`, 'success')
    }

    resetDashboardState()
    const state = await loadProfile(true)

    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : null
    if (redirect) router.push(redirect)
    else if (state.onboarded) router.push('/')
    // A failed fetch is not the same as "no profile" — land on Today and let
    // the app retry rather than dragging someone through setup again.
    else if (state.error) router.push('/')
    else router.push('/onboarding')
  } catch (err) {
    error.value = err.message
  } finally {
    busy.value = false
  }
}
</script>
