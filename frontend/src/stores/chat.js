import { defineStore } from 'pinia'
import { createChatRoom, sendChatMessage } from '../api/chat'
import { useRegionStore } from './region'

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [],
    sessionId: crypto.randomUUID(),
    roomId: null,
    loading: false
  }),
  actions: {
    async ensureRoom() {
      if (this.roomId) return this.roomId
      const { data } = await createChatRoom(this.sessionId)
      this.roomId = data.room_id
      return this.roomId
    },
    async sendMessage(text) {
      this.messages.push({ role: 'user', content: text, places: [] })
      this.loading = true
      try {
        const roomId = await this.ensureRoom()
        const regionStore = useRegionStore()
        const { data } = await sendChatMessage(roomId, text, regionStore.selectedRegion)
        this.messages.push({
          role: 'assistant',
          content: data.bot_response.message,
          places: data.referenced_places ?? []
        })
      } catch {
        this.messages.push({
          role: 'assistant',
          content: '메시지를 보내지 못했어요. 잠시 후 다시 시도해주세요.',
          places: []
        })
      } finally {
        this.loading = false
      }
    }
  }
})
