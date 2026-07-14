import { defineStore } from 'pinia'
import { sendChatMessage } from '../api/chat'

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [],
    sessionId: crypto.randomUUID(),
    loading: false
  }),
  actions: {
    async sendMessage(text) {
      this.messages.push({ role: 'user', content: text })
      this.loading = true
      try {
        const { data } = await sendChatMessage(text, this.sessionId)
        this.messages.push({ role: 'assistant', content: data.reply })
      } finally {
        this.loading = false
      }
    }
  }
})
