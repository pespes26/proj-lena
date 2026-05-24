import { onBeforeUnmount } from 'vue'

const FOCUSABLE_SELECTORS = [
  'a[href]',
  'button:not([disabled])',
  'input:not([disabled])',
  'select:not([disabled])',
  'textarea:not([disabled])',
  '[tabindex]:not([tabindex="-1"])',
].join(', ')

export function useFocusTrap(containerRef) {
  let previousFocus = null

  function getFocusable() {
    if (!containerRef.value) return []
    return Array.from(containerRef.value.querySelectorAll(FOCUSABLE_SELECTORS))
  }

  function onKeydown(e) {
    if (e.key !== 'Tab') return
    const els = getFocusable()
    if (!els.length) return
    const first = els[0]
    const last = els[els.length - 1]
    if (e.shiftKey) {
      if (document.activeElement === first) {
        e.preventDefault()
        last.focus()
      }
    } else {
      if (document.activeElement === last) {
        e.preventDefault()
        first.focus()
      }
    }
  }

  function activate() {
    previousFocus = document.activeElement
    document.addEventListener('keydown', onKeydown)
    const els = getFocusable()
    if (els.length) els[0].focus()
  }

  function deactivate() {
    document.removeEventListener('keydown', onKeydown)
    if (previousFocus && typeof previousFocus.focus === 'function') {
      previousFocus.focus()
    }
    previousFocus = null
  }

  onBeforeUnmount(deactivate)

  return { activate, deactivate }
}
