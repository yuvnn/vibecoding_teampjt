import { defineStore } from 'pinia'

const STORAGE_KEY = 'localhub-calendar-events'

function loadEvents() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    const parsed = raw ? JSON.parse(raw) : []
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

function makeId() {
  return `evt_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`
}

/**
 * Festival/event calendar entries have no backend table, so they're
 * community-authored and stored per-browser in localStorage (see plan doc).
 */
export const useCalendarEventsStore = defineStore('calendarEvents', {
  state: () => ({
    events: loadEvents()
  }),
  actions: {
    persist() {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.events))
    },
    create(event) {
      const record = { id: makeId(), tags: [], imageDataUrl: '', description: '', ...event }
      this.events.push(record)
      this.persist()
      return record
    },
    update(id, patch) {
      const target = this.events.find((event) => event.id === id)
      if (!target) return
      Object.assign(target, patch)
      this.persist()
    },
    remove(id) {
      this.events = this.events.filter((event) => event.id !== id)
      this.persist()
    }
  }
})
