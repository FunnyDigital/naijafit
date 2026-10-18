import { reactive } from 'vue'

import { api } from '../services/api'

export const dashboardState = reactive({
  loaded: false,
  loading: false,
  data: null,
  error: null,
})

export function resetDashboardState() {
  dashboardState.loaded = false
  dashboardState.loading = false
  dashboardState.data = null
  dashboardState.error = null
}

export async function loadDashboard(date = null, force = false) {
  if (dashboardState.loaded && dashboardState.data?.date === date && !force) {
    return dashboardState.data
  }
  dashboardState.loading = true
  try {
    const data = await api.getDashboard(date)
    dashboardState.data = data
    dashboardState.error = null
  } catch (error) {
    dashboardState.error = error.message
    if (error.status === 404) dashboardState.data = null
  } finally {
    dashboardState.loading = false
    dashboardState.loaded = true
  }
  return dashboardState.data
}

export function useDashboard() {
  return { state: dashboardState, loadDashboard, resetDashboardState }
}
