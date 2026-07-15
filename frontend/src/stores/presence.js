import { defineStore } from 'pinia'

const RECONNECT_DELAY_MS = 3000

function wsUrl() {
  const base = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'
  return `${base.replace(/^http/, 'ws')}/api/presence/ws`
}

let socket = null

export const usePresenceStore = defineStore('presence', {
  state: () => ({
    count: 0,
    started: false
  }),
  actions: {
    connect() {
      if (this.started) return
      this.started = true
      this._open()
    },
    _open() {
      socket = new WebSocket(wsUrl())

      socket.onmessage = (event) => {
        try {
          this.count = JSON.parse(event.data).count
        } catch {
          // ignore malformed frame
        }
      }

      socket.onclose = () => {
        setTimeout(() => this._open(), RECONNECT_DELAY_MS)
      }

      socket.onerror = () => socket.close()
    }
  }
})
