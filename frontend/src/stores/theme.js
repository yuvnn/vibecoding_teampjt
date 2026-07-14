import { defineStore } from 'pinia'

const STORAGE_KEY = 'localhub-theme'

function detectInitialMode() {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved === 'light' || saved === 'dark') return saved
  return window.matchMedia?.('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function applyMode(mode) {
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
      localStorage.setItem(STORAGE_KEY, this.mode)
      applyMode(this.mode)
    }
  }
})
