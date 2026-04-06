import { ref, inject, provide } from 'vue'

const TOAST_KEY = Symbol('toast')
let _id = 0

export function createToastProvider() {
  const toasts = ref([])

  function add(message, type = 'info', duration = 4000) {
    const id = ++_id
    toasts.value.push({ id, message, type })
    if (toasts.value.length > 3) toasts.value.shift()
    if (duration > 0) {
      setTimeout(() => dismiss(id), duration)
    }
  }

  function dismiss(id) {
    const idx = toasts.value.findIndex(t => t.id === id)
    if (idx !== -1) toasts.value.splice(idx, 1)
  }

  const toast = {
    success: (msg) => add(msg, 'success'),
    error: (msg) => add(msg, 'error', 6000),
    warning: (msg) => add(msg, 'warning', 5000),
    info: (msg) => add(msg, 'info'),
    dismiss,
  }

  provide(TOAST_KEY, toast)

  return { toasts, toast, dismiss }
}

export function useToast() {
  const toast = inject(TOAST_KEY)
  if (!toast) {
    console.warn('useToast() called outside of toast provider')
    return {
      success: () => {},
      error: () => {},
      warning: () => {},
      info: () => {},
      dismiss: () => {},
    }
  }
  return toast
}

// For use outside Vue components (e.g., api.js interceptor)
let _globalToast = null
export function setGlobalToast(toast) { _globalToast = toast }
export function getGlobalToast() { return _globalToast }
