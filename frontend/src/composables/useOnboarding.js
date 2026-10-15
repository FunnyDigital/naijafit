import { reactive } from 'vue'

import { api } from '../services/api'

export function defaultForm() {
  return {
    name: '',
    sex: 'male',
    age: 30,
    height_cm: 170,
    weight_kg: 75,
    units: 'metric',
    goal: 'lose',
    activity_level: 'light',
    level: 'beginner',
    workouts_per_week: 3,
    equipment: ['none'],
    dietary_flags: [],
  }
}

export const form = reactive(defaultForm())

export const optionsState = reactive({ loaded: false, loading: false, data: null, error: null })

export function resetForm() {
  Object.assign(form, defaultForm())
}

export async function loadOptions(force = false) {
  if (optionsState.loaded && !force) return optionsState.data
  optionsState.loading = true
  try {
    optionsState.data = await api.getOptions()
    optionsState.error = null
  } catch (error) {
    optionsState.error = error.message
  } finally {
    optionsState.loading = false
    optionsState.loaded = true
  }
  return optionsState.data
}

export function setFromProfile(profile) {
  if (!profile) return
  Object.assign(form, {
    name: profile.name,
    sex: profile.sex,
    age: profile.age,
    height_cm: profile.height_cm,
    weight_kg: profile.weight_kg,
    units: profile.units,
    goal: profile.goal,
    activity_level: profile.activity_level,
    level: profile.level,
    workouts_per_week: profile.workouts_per_week,
    equipment: [...(profile.equipment || [])],
    dietary_flags: [...(profile.dietary_flags || [])],
  })
}

export function useOnboarding() {
  return { form, optionsState, loadOptions, resetForm, setFromProfile }
}
