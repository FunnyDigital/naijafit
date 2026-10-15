<template>
  <div class="mx-auto w-full max-w-3xl px-4 py-5 sm:px-6 sm:py-7">
    <h1 class="font-display text-2xl font-semibold tracking-tight sm:text-3xl">Profile</h1>
    <p class="mt-1 text-sm text-ink-muted">Your details, your targets, and your data.</p>

    <section v-if="profile" class="card mt-5 p-4">
      <div class="flex items-start justify-between gap-3">
        <div class="flex items-center gap-3">
          <span class="flex h-12 w-12 items-center justify-center rounded-full bg-accent text-lg font-semibold text-white">
            {{ initial }}
          </span>
          <div>
            <p class="font-display text-lg font-semibold text-ink">{{ profile.name }}</p>
            <p class="text-xs text-ink-muted">
              {{ titleCase(profile.level) }} · {{ profile.workouts_per_week }} days a week
            </p>
          </div>
        </div>
        <RouterLink to="/onboarding" class="btn-ghost btn-sm">
          <Icon name="edit" :size="15" /> Edit
        </RouterLink>
      </div>

      <dl class="mt-4 divide-y divide-line text-sm">
        <div v-for="row in details" :key="row.label" class="flex items-start justify-between gap-4 py-2">
          <dt class="text-ink-muted">{{ row.label }}</dt>
          <dd class="text-right font-medium text-ink-soft">{{ row.value }}</dd>
        </div>
      </dl>
    </section>

    <section v-if="profile" class="card mt-4 p-4">
      <p class="section-title text-base">Daily targets</p>
      <div class="mt-3 grid grid-cols-2 gap-3 sm:grid-cols-4">
        <div class="rounded-xl bg-accent-50 px-3 py-2.5">
          <p class="font-display text-lg font-semibold text-accent-700">{{ targets.calorie_target }}</p>
          <p class="text-[11px] uppercase tracking-wide text-ink-muted">Calories</p>
        </div>
        <div class="rounded-xl bg-canvas px-3 py-2.5">
          <p class="font-display text-lg font-semibold text-ink">{{ targets.protein_g }}g</p>
          <p class="text-[11px] uppercase tracking-wide text-ink-muted">Protein</p>
        </div>
        <div class="rounded-xl bg-canvas px-3 py-2.5">
          <p class="font-display text-lg font-semibold text-ink">{{ targets.carbs_g }}g</p>
          <p class="text-[11px] uppercase tracking-wide text-ink-muted">Carbs</p>
        </div>
        <div class="rounded-xl bg-canvas px-3 py-2.5">
          <p class="font-display text-lg font-semibold text-ink">{{ targets.fat_g }}g</p>
          <p class="text-[11px] uppercase tracking-wide text-ink-muted">Fat</p>
        </div>
      </div>
      <div class="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-line pt-3">
        <div class="text-sm">
          <p class="font-medium text-ink-soft">{{ formatVolume(targets.water_ml) }} of water a day</p>
          <p class="text-xs text-ink-muted">Water target scales with your weight.</p>
        </div>
        <div class="inline-flex rounded-full border border-line bg-surface p-1">
          <button
            v-for="option in unitOptions"
            :key="option.value"
            class="rounded-full px-3.5 py-1.5 text-xs font-medium transition-colors"
            :class="profile.units === option.value ? 'bg-accent text-white' : 'text-ink-soft'"
            :disabled="savingUnits"
            @click="setUnits(option.value)"
          >
            {{ option.label }}
          </button>
        </div>
      </div>
    </section>

    <section class="card mt-4 p-4">
      <p class="section-title text-base">Your plan</p>
      <p class="mt-1 text-xs text-ink-muted">
        Rebuild a fresh week of workouts and meals from your current details.
      </p>
      <button class="btn-ghost btn-sm mt-3" :disabled="regenerating" @click="regenerate">
        <Icon name="refresh" :size="15" :class="regenerating ? 'animate-spin' : ''" />
        {{ regenerating ? 'Rebuilding…' : 'Regenerate plan' }}
      </button>
    </section>

    <section class="card mt-4 p-4">
      <p class="section-title text-base">Your data</p>
      <p class="mt-1 text-xs text-ink-muted">
        Everything lives in this app’s own database. Back it up as one file, or move it to another
        machine.
      </p>
      <div class="mt-3 flex flex-wrap gap-2">
        <button class="btn-ghost btn-sm" :disabled="busy" @click="download">
          <Icon name="download" :size="15" /> Download backup
        </button>
        <label class="btn-ghost btn-sm cursor-pointer">
          <Icon name="upload" :size="15" /> Restore from file
          <input type="file" accept="application/json,.json" class="hidden" @change="restore" />
        </label>
      </div>

      <div class="mt-4 border-t border-line pt-3">
        <button class="btn-danger btn-sm" :disabled="busy" @click="startOver">
          <Icon name="trash" :size="15" />
          {{ confirmReset ? 'Tap again to erase everything' : 'Start over' }}
        </button>
        <p class="mt-2 text-xs text-ink-faint">
          Deletes your profile, plan, logs and any dishes you added. The built-in library stays.
        </p>
      </div>
    </section>

    <section class="mt-4 pb-2 text-center">
      <p class="inline-flex items-center gap-1.5 text-xs text-ink-faint">
        <Icon name="pulse" :size="13" /> NaijaFit {{ version }} · self-hosted on your own server
      </p>
    </section>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import Icon from '../components/Icon.vue'
import { api } from '../services/api'
import { loadProfile, profileState, saveProfile } from '../composables/useProfile'
import { loadDashboard } from '../composables/useDashboard'
import { resetForm, setFromProfile } from '../composables/useOnboarding'
import { pushToast } from '../composables/useToast'
import { formatHeight, formatVolume, formatWeight } from '../utils/format'
import { titleCase, todayISO } from '../utils/dates'

const router = useRouter()

const version = ref('1.0.0')
const busy = ref(false)
const regenerating = ref(false)
const savingUnits = ref(false)
const confirmReset = ref(false)

const unitOptions = [
  { value: 'metric', label: 'kg / cm' },
  { value: 'imperial', label: 'lb / ft' },
]

const profile = computed(() => profileState.profile)
const targets = computed(() => profile.value?.targets || { calorie_target: 0, protein_g: 0, carbs_g: 0, fat_g: 0, water_ml: 0 })
const initial = computed(() => (profile.value?.name || '?').charAt(0).toUpperCase())

const details = computed(() => {
  if (!profile.value) return []
  const goal = { lose: 'Lose fat', maintain: 'Stay the same', gain: 'Build muscle' }[profile.value.goal]
  const activity = {
    sedentary: 'Sedentary',
    light: 'Lightly active',
    moderate: 'Moderately active',
    active: 'Very active',
    very_active: 'Extremely active',
  }[profile.value.activity_level]

  const equipment = (profile.value.equipment || [])
    .map((item) => ({ none: 'Bodyweight', chair: 'Chair or step', band: 'Resistance band', dumbbell: 'Dumbbells' }[item] || item))
    .join(', ')

  const rows = [
    { label: 'Age', value: `${profile.value.age}` },
    { label: 'Height', value: formatHeight(profile.value.height_cm, profile.value.units) },
    { label: 'Weight', value: formatWeight(profile.value.weight_kg, profile.value.units) },
    { label: 'Goal', value: goal },
    { label: 'Activity', value: activity },
    { label: 'Equipment', value: equipment || 'Bodyweight' },
  ]
  if (profile.value.dietary_flags?.length) {
    rows.push({ label: 'Avoiding', value: profile.value.dietary_flags.map((flag) => flag.replace('_', ' ')).join(', ') })
  }
  return rows
})

function payloadFrom(profile, overrides = {}) {
  return {
    name: profile.name,
    sex: profile.sex,
    age: profile.age,
    height_cm: profile.height_cm,
    weight_kg: profile.weight_kg,
    goal: profile.goal,
    activity_level: profile.activity_level,
    level: profile.level,
    workouts_per_week: profile.workouts_per_week,
    equipment: profile.equipment,
    dietary_flags: profile.dietary_flags,
    units: profile.units,
    ...overrides,
  }
}

async function setUnits(units) {
  if (units === profile.value.units) return
  savingUnits.value = true
  try {
    await saveProfile(payloadFrom(profile.value, { units }))
    pushToast('Units updated', 'success')
  } catch (error) {
    pushToast(error.message, 'error')
  } finally {
    savingUnits.value = false
  }
}

async function regenerate() {
  regenerating.value = true
  try {
    await api.generatePlan()
    await loadDashboard(null, true)
    pushToast('Fresh plan built', 'success')
  } catch (error) {
    pushToast(error.message, 'error')
  } finally {
    regenerating.value = false
  }
}

async function download() {
  busy.value = true
  try {
    const data = await api.getBackup()
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `naijafit-backup-${todayISO()}.json`
    link.click()
    URL.revokeObjectURL(url)
  } catch (error) {
    pushToast(error.message, 'error')
  } finally {
    busy.value = false
  }
}

async function restore(event) {
  const file = event.target.files?.[0]
  if (!file) return
  busy.value = true
  const reader = new FileReader()
  reader.onload = async () => {
    try {
      const payload = JSON.parse(String(reader.result))
      await api.restore(payload)
      await loadProfile(true)
      await loadDashboard(null, true)
      pushToast('Backup restored', 'success')
    } catch (error) {
      pushToast('That file could not be restored', 'error')
    } finally {
      busy.value = false
      event.target.value = ''
    }
  }
  reader.readAsText(file)
}

async function startOver() {
  if (!confirmReset.value) {
    confirmReset.value = true
    setTimeout(() => {
      confirmReset.value = false
    }, 5000)
    return
  }
  busy.value = true
  try {
    await api.resetData()
    resetForm()
    await loadProfile(true)
    pushToast('All clear — time for a fresh start', 'success')
    router.push('/onboarding')
  } catch (error) {
    pushToast(error.message, 'error')
  } finally {
    busy.value = false
    confirmReset.value = false
  }
}

onMounted(async () => {
  try {
    const site = await api.getSite()
    version.value = site.version
  } catch {
    /* keep the default */
  }
  if (profileState.profile) setFromProfile(profileState.profile)
})
</script>
