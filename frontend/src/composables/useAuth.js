import { computed, reactive } from 'vue'

import { api, getToken, removeToken, setToken, setUnauthorizedHandler } from '../services/api'

export const authState = reactive({
  ready: false,
  user: null,
  checking: false,
})

export const isSignedIn = computed(() => !!authState.user)

export function currentUser() {
  return authState.user
}

export async function checkSession() {
  if (!getToken()) {
    authState.user = null
    authState.ready = true
    return authState
  }
  if (authState.checking) return authState
  authState.checking = true
  try {
    const data = await api.me()
    authState.user = data.user
  } catch {
    authState.user = null
    removeToken()
  } finally {
    authState.checking = false
    authState.ready = true
  }
  return authState
}

async function adopt(result) {
  setToken(result.access_token)
  authState.user = result.user
  authState.ready = true
  return result.user
}

export async function login(username, password) {
  return adopt(await api.login(username, password))
}

export async function register(username, password) {
  return adopt(await api.register(username, password))
}

export function signOut() {
  removeToken()
  authState.user = null
}

// A 401 from any call means the token is gone — drop the session immediately.
setUnauthorizedHandler(() => {
  authState.user = null
})

export function useAuth() {
  return { state: authState, isSignedIn, login, register, signOut, checkSession }
}
