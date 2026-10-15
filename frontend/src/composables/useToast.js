import { reactive } from 'vue'

let uid = 0

export const toasts = reactive([])

export function removeToast(id) {
  const index = toasts.findIndex((toast) => toast.id === id)
  if (index !== -1) toasts.splice(index, 1)
}

export function pushToast(message, type = 'info', timeout = 2800) {
  const id = ++uid
  toasts.push({ id, message, type })
  if (timeout) setTimeout(() => removeToast(id), timeout)
  return id
}

export function useToast() {
  return { toasts, pushToast, removeToast }
}
