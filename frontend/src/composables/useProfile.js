import { reactive } from 'vue'

import { api } from '../services/api'
import { authState } from './useAuth'

const CACHE_KEY = 'naijafit_profile'

export const profileState = reactive({
  loaded: false,
  loading: false,
  profile: null,
  onboarded: false,
  error: null,
  fromCache: false,
})

function readCache() {
  try {
    const raw = localStorage.getItem(CACHE_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw)
    // Keyed by account: never show one person's profile to another.
    if (!parsed || parsed.userId !== authState.user?.id) return null
    return parsed
  } catch {
    return null
  }
}

function writeCache() {
  try {
    if (!authState.user?.id) return
    localStorage.setItem(
      CACHE_KEY,
      JSON.stringify({
        userId: authState.user.id,
        profile: profileState.profile,
        onboarded: profileState.onboarded,
      }),
    )
  } catch {
    /* private mode — carry on without the cache */
  }
}

export function clearProfileCache() {
  try {
    localStorage.removeItem(CACHE_KEY)
  } catch {
    /* ignore */
  }
}

export function resetProfileState() {
  profileState.loaded = false
  profileState.loading = false
  profileState.profile = null
  profileState.onboarded = false
  profileState.error = null
  profileState.fromCache = false
  clearProfileCache()
}

export async function loadProfile(force = false) {
  if (profileState.loaded && !force) return profileState
  profileState.loading = true
  try {
    const data = await api.getProfile()
    profileState.profile = data.profile
    profileState.onboarded = data.onboarded
    profileState.error = null
    profileState.fromCache = false
    writeCache()
  } catch (error) {
    profileState.error = error.message
    // If we already know who they are, a failed fetch must not look like
    // "you never finished setup" — that sends people back through onboarding.
    const cached = readCache()
    if (cached) {
      profileState.profile = cached.profile
      profileState.onboarded = cached.onboarded
      profileState.fromCache = true
    }
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
  profileState.fromCache = false
  writeCache()
  return data.profile
}

export function useProfile() {
  return { state: profileState, loadProfile, saveProfile, resetProfileState, clearProfileCache }
}
