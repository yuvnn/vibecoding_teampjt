import { defineStore } from 'pinia'

const MAX_ROUTE_SELECTION = 6

// Shared across the map (pin clicks / popup button) and the chat widget
// (place chips under bot replies), so both can add to the same route list
// regardless of which page is currently active.
export const useRouteStore = defineStore('route', {
  state: () => ({
    items: []
  }),
  getters: {
    ids: (state) => state.items.map((item) => item.id),
    isSelected: (state) => (id) => state.items.some((item) => item.id === id)
  },
  actions: {
    toggle(place) {
      const index = this.items.findIndex((item) => item.id === place.id)
      if (index !== -1) {
        this.items = this.items.filter((item) => item.id !== place.id)
        return
      }
      if (this.items.length >= MAX_ROUTE_SELECTION) return
      this.items = [...this.items, place]
    },
    remove(id) {
      this.items = this.items.filter((item) => item.id !== id)
    },
    clear() {
      this.items = []
    }
  }
})
