import { defineStore } from 'pinia'

let seq = 0

export const useToastStore = defineStore('toast', {
  state: () => ({
    items: []
  }),
  actions: {
    push(message, { type = 'info', timeout = 4000, onClick } = {}) {
      seq += 1
      const id = seq
      this.items.push({ id, message, type, onClick })
      if (timeout > 0) {
        setTimeout(() => this.dismiss(id), timeout)
      }
      return id
    },
    dismiss(id) {
      this.items = this.items.filter((item) => item.id !== id)
    }
  }
})
