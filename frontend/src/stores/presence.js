import { defineStore } from 'pinia'
import apiClient from '../api/client'

const SESSION_KEY = 'localhub-session-id'
const HEARTBEAT_INTERVAL_MS = 20000

function getSessionId() {
  let id = sessionStorage.getItem(SESSION_KEY)
  if (!id) {
    id = crypto.randomUUID()
    sessionStorage.setItem(SESSION_KEY, id)
  }
  return id
}

export const usePresenceStore = defineStore('presence', {
  state: () => ({
    count: 0,
    started: false
  }),
  actions: {
    async beat() {
      try {
        const { data } = await apiClient.post('/api/presence/heartbeat', {
          session_id: getSessionId()
        })
        this.count = data.count
      } catch {
        // silent: presence is a nicety, not critical path
      }
    },
    startHeartbeat() {
      if (this.started) return
      this.started = true
      this.beat()
      setInterval(() => this.beat(), HEARTBEAT_INTERVAL_MS)
    }
  }
})
