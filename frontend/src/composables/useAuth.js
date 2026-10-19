import { computed, reactive } from 'vue'

import { api, getToken, removeToken, setToken, setUnauthorizedHandler } from '../services/api'

const USER_KEY = 'naijafit_user'

export const authState = reactive({
  ready: false,
  user: null,
  checking: false,
})

// One shared request, so a page load can't half-authenticate.
let inflight = null

export const isSignedIn = computed(() => !!authState.user)

function readCachedUser() {
  try {
    const raw = localStorage.getItem(USER_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

function writeCachedUser(user) {
  try {
    if (user) localStorage.setItem(USER_KEY, JSON.stringify(user))
    else localStorage.removeItem(USER_KEY)
  } catch {
    /* private mode — carry on without the cache */
  }
}

export async function checkSession(force = false) {
  // Already resolved this session and nothing has invalidated it.
  if (!force && authState.ready && authState.user) return authState

  if (!getToken()) {
    authState.user = null
    authState.ready = true
    writeCachedUser(null)
    return authState
  }

  if (inflight) {
    await inflight
    return authState
  }

  authState.checking = true
  inflight = (async () => {
    try {
      const data = await api.me()
      authState.user = data.user
      writeCachedUser(data.user)
    } catch (error) {
      // Only a real 401 means the token is dead. A network blip, a restarting
      // container or a proxy hiccup must never sign anybody out.
      if (error.status === 401) {
        authState.user = null
        removeToken()
        writeCachedUser(null)
      } else {
        // Keep the session and fall back to who we last knew we were, so the
        // app still opens when the server is briefly unreachable.
        authState.user = authState.user || readCachedUser()
      }
    } finally {
      authState.ready = true
      authState.checking = false
      inflight = null
    }
  })()

  await inflight
  return authState
}

async function adopt(result) {
  setToken(result.access_token)
  authState.user = result.user
  authState.ready = true
  writeCachedUser(result.user)
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
  authState.ready = true
  writeCachedUser(null)
}

// A 401 from any call means the token is gone — drop the session immediately.
setUnauthorizedHandler(() => {
  authState.user = null
  writeCachedUser(null)
})

export function useAuth() {
  return { state: authState, isSignedIn, login, register, signOut, checkSession }
}
