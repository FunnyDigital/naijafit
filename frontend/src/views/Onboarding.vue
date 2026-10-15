<template>
  <div class="flex h-full flex-col bg-canvas">
    <header class="shrink-0 border-b border-line bg-canvas/90 px-4 py-3 backdrop-blur sm:px-6">
      <div class="mx-auto flex max-w-3xl items-center justify-between gap-3">
        <div class="flex items-center gap-2.5">
          <span class="flex h-9 w-9 items-center justify-center rounded-full bg-accent text-white">
            <Icon name="pulse" :size="19" :stroke-width="2" />
          </span>
          <span class="font-display text-lg font-semibold tracking-tight">NaijaFit</span>
        </div>
        <button
          v-if="existingProfile"
          class="text-xs font-medium text-ink-muted transition-colors hover:text-ink"
          @click="cancel"
        >
          Cancel
        </button>
        <span v-else class="text-xs font-medium text-ink-muted">
          Step {{ step + 1 }} of {{ steps.length }}
        </span>
      </div>

      <div class="mx-auto mt-3 flex max-w-3xl gap-1.5">
        <span
          v-for="(item, index) in steps"
          :key="item.key"
          class="h-1.5 flex-1 rounded-full transition-colors duration-300"
          :class="index <= step ? 'bg-accent' : 'bg-line'"
        />
      </div>
    </header>

    <div class="flex-1 overflow-y-auto overscroll-contain">
      <div v-if="!ready" class="mx-auto max-w-3xl px-4 py-8 sm:px-6">
        <LoadingState :rows="3" />
      </div>
      <div v-else class="mx-auto max-w-3xl px-4 py-6 sm:px-6 sm:py-9">
        <component :is="current.component" :key="current.key" v-reveal />
      </div>
    </div>

    <footer class="safe-bottom shrink-0 border-t border-line bg-surface px-4 py-3 sm:px-6">
      <div class="mx-auto flex max-w-3xl items-center justify-between gap-3">
        <button class="btn-ghost" :disabled="step === 0 || saving" @click="back">
          <Icon name="arrowLeft" :size="16" /> Back
        </button>

        <button class="btn-primary" :disabled="!canContinue || saving" @click="next">
          <template v-if="saving">
            <Icon name="refresh" :size="16" class="animate-spin" /> Building your plan…
          </template>
          <template v-else-if="isLast">
            Generate my plan <Icon name="sparkles" :size="16" />
          </template>
          <template v-else>Continue <Icon name="arrowRight" :size="16" /></template>
        </button>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import Icon from '../components/Icon.vue'
import LoadingState from '../components/LoadingState.vue'
import { useOnboarding } from '../composables/useOnboarding'
import { loadProfile, profileState, saveProfile } from '../composables/useProfile'
import { loadDashboard } from '../composables/useDashboard'
import { pushToast } from '../composables/useToast'

import StepAbout from './onboarding/StepAbout.vue'
import StepBody from './onboarding/StepBody.vue'
import StepGoal from './onboarding/StepGoal.vue'
import StepActivity from './onboarding/StepActivity.vue'
import StepTraining from './onboarding/StepTraining.vue'
import StepDiet from './onboarding/StepDiet.vue'
import StepReview from './onboarding/StepReview.vue'

const route = useRoute()
const router = useRouter()
const { form, optionsState, loadOptions, setFromProfile } = useOnboarding()

const step = ref(0)
const ready = ref(false)
const saving = ref(false)

const existingProfile = computed(() => !!profileState.profile)

const steps = [
  { key: 'about', component: StepAbout, valid: () => form.name.trim().length > 0 },
  { key: 'body', component: StepBody, valid: () => form.age >= 12 && form.height_cm > 90 && form.weight_kg > 25 },
  { key: 'goal', component: StepGoal, valid: () => true },
  { key: 'activity', component: StepActivity, valid: () => true },
  { key: 'training', component: StepTraining, valid: () => true },
  { key: 'diet', component: StepDiet, valid: () => true },
  { key: 'review', component: StepReview, valid: () => true },
]

const current = computed(() => steps[step.value])
const isLast = computed(() => step.value === steps.length - 1)
const canContinue = computed(() => current.value.valid())

function back() {
  if (step.value > 0) step.value -= 1
}

function next() {
  if (!canContinue.value) return
  if (isLast.value) return submit()
  step.value += 1
}

async function submit() {
  saving.value = true
  try {
    await saveProfile({ ...form })
    await loadDashboard(null, true)
    pushToast('Your plan is ready — let’s go', 'success')
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/'
    router.push(redirect)
  } catch (error) {
    pushToast(error.message, 'error')
  } finally {
    saving.value = false
  }
}

function cancel() {
  router.push('/profile')
}

onMounted(async () => {
  const [options] = await Promise.all([loadOptions(), loadProfile()])
  if (!options) {
    pushToast('Could not load the options', 'error')
  }
  if (profileState.profile) setFromProfile(profileState.profile)
  ready.value = true
})
</script>
