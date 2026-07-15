import { defineStore } from 'pinia'

const STORAGE_KEY = 'localhub-theme'

function readStoredMode() {
  try {
    return localStorage.getItem(STORAGE_KEY)
  } catch {
    return null
  }
}

function detectInitialMode() {
  const saved = readStoredMode()
  if (saved === 'light' || saved === 'dark') return saved
  return typeof window !== 'undefined' && window.matchMedia?.('(prefers-color-scheme: dark)').matches
    ? 'dark'
    : 'light'
}

function applyMode(mode) {
  if (typeof document === 'undefined') return
  document.documentElement.setAttribute('data-theme', mode)
}

export const useThemeStore = defineStore('theme', {
  state: () => ({
    mode: detectInitialMode()
  }),
  actions: {
    init() {
      applyMode(this.mode)
    },
    toggle() {
      this.mode = this.mode === 'dark' ? 'light' : 'dark'
      try {
        localStorage.setItem(STORAGE_KEY, this.mode)
      } catch {
        // Theme still updates in memory even if persistence is unavailable.
      }
      applyMode(this.mode)
    }
  }
})
