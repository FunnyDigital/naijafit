const API_BASE = '/api'
const TOKEN_KEY = 'naijafit_token'

let onUnauthorized = null

export function setUnauthorizedHandler(handler) {
  onUnauthorized = handler
}

export function getToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function removeToken() {
  localStorage.removeItem(TOKEN_KEY)
}

export function isAuthenticated() {
  return !!getToken()
}

function query(params = {}) {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') search.append(key, value)
  })
  const qs = search.toString()
  return qs ? `?${qs}` : ''
}

async function request(path, { method = 'GET', body = null, anonymous = false } = {}) {
  const options = { method, headers: {} }
  if (body != null) {
    options.headers['Content-Type'] = 'application/json'
    options.body = JSON.stringify(body)
  }
  const token = getToken()
  if (token && !anonymous) options.headers.Authorization = `Bearer ${token}`

  let res
  try {
    res = await fetch(`${API_BASE}${path}`, options)
  } catch (cause) {
    const error = new Error('Cannot reach the server. Is the backend running?')
    error.status = 0
    throw error
  }

  if (res.status === 401 && !anonymous) {
    removeToken()
    if (onUnauthorized) onUnauthorized()
  }

  if (!res.ok) {
    let detail = res.statusText || 'Something went wrong'
    try {
      const data = await res.json()
      if (data && data.detail) detail = data.detail
    } catch {
      /* keep the status text */
    }
    const error = new Error(detail)
    error.status = res.status
    throw error
  }

  if (res.status === 204) return null
  return res.json()
}

export const api = {
  // meta
  getSite: () => request('/site', { anonymous: true }),
  getOptions: () => request('/onboarding/options', { anonymous: true }),

  // accounts
  register: (username, password) =>
    request('/auth/register', {
      method: 'POST',
      body: { username, password },
      anonymous: true,
    }),
  login: (username, password) =>
    request('/auth/login', {
      method: 'POST',
      body: { username, password },
      anonymous: true,
    }),
  me: () => request('/auth/me'),

  // profile
  getProfile: () => request('/profile'),
  saveProfile: (payload) => request('/profile', { method: 'PUT', body: payload }),
  previewTargets: (payload) => request('/profile/preview', { method: 'POST', body: payload }),
  getTargets: () => request('/targets'),

  // plan
  getPlan: () => request('/plan'),
  generatePlan: () => request('/plan/generate', { method: 'POST' }),
  getWorkout: (dayIndex) => request(`/plan/workout/${dayIndex}`),
  getDayMeals: (dayIndex) => request(`/plan/meals/${dayIndex}`),
  swapMeal: (mealId) => request(`/plan/meals/${mealId}/swap`, { method: 'POST' }),
  acceptSuggestion: (mealId) => request(`/plan/meals/${mealId}/accept`, { method: 'POST' }),

  // catalogs
  getFoods: (params = {}) => request(`/foods${query(params)}`),
  getFood: (id) => request(`/foods/${id}`),
  createFood: (payload) => request('/foods', { method: 'POST', body: payload }),
  updateFood: (id, payload) => request(`/foods/${id}`, { method: 'PUT', body: payload }),
  deleteFood: (id) => request(`/foods/${id}`, { method: 'DELETE' }),
  getExercises: (params = {}) => request(`/exercises${query(params)}`),

  // personal menu
  getMenu: () => request('/menu'),
  setMenuItem: (foodId, status = 'liked') =>
    request(`/menu/${foodId}`, { method: 'POST', body: { status } }),
  clearMenuItem: (foodId) => request(`/menu/${foodId}`, { method: 'DELETE' }),
  getMenuSuggestions: (limit = 6) => request(`/menu/suggestions${query({ limit })}`),

  // logs
  logWorkout: (payload) => request('/logs/workout', { method: 'POST', body: payload }),
  listWorkouts: (days = 60) => request(`/logs/workout${query({ days })}`),
  deleteWorkout: (date) => request(`/logs/workout/${date}`, { method: 'DELETE' }),
  logMeal: (payload) => request('/logs/meal', { method: 'POST', body: payload }),
  listMeals: (date) => request(`/logs/meal${query({ date })}`),
  deleteMeal: (id) => request(`/logs/meal/${id}`, { method: 'DELETE' }),
  logWeight: (payload) => request('/logs/weight', { method: 'POST', body: payload }),
  listWeight: (days = 180) => request(`/logs/weight${query({ days })}`),
  logWater: (payload) => request('/logs/water', { method: 'POST', body: payload }),
  getWater: (date) => request(`/logs/water${query({ date })}`),

  // dashboard + admin
  getDashboard: (date) => request(`/dashboard${query({ date })}`),
  getBackup: () => request('/admin/backup'),
  restore: (payload) => request('/admin/restore', { method: 'POST', body: payload }),
  resetData: () => request('/admin/data', { method: 'DELETE' }),
}
