import { reactive } from 'vue'

import { api } from '../services/api'

export const profileState = reactive({
  loaded: false,
  loading: false,
  profile: null,
  onboarded: false,
  error: null,
})

export function resetProfileState() {
  profileState.loaded = false
  profileState.loading = false
  profileState.profile = null
  profileState.onboarded = false
  profileState.error = null
}

export async function loadProfile(force = false) {
  if (profileState.loaded && !force) return profileState
  profileState.loading = true
  try {
    const data = await api.getProfile()
    profileState.profile = data.profile
    profileState.onboarded = data.onboarded
    profileState.error = null
  } catch (error) {
    profileState.error = error.message
  } finally {
    profileState.loading = false
    profileState.loaded = true
  }
  return profileState
}

export async function saveProfile(payload) {
  const data = await api.saveProfile(payload)
  profileState.profile = data.profile
  profileState.onboarded = true
  profileState.loaded = true
  profileState.error = null
  return data.profile
}

export function useProfile() {
  return { state: profileState, loadProfile, saveProfile, resetProfileState }
}
