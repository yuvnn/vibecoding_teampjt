import { defineStore } from 'pinia'

// Lets components outside the Home page (e.g. the global ChatWidget) ask the
// map to fly to a place and pop its info bubble, without holding a direct
// ref to HomeView's TourMap instance across route navigations.
export const useMapFocusStore = defineStore('mapFocus', {
  state: () => ({
    pending: null
  }),
  actions: {
    request(place) {
      this.pending = { ...place, requestedAt: Date.now() }
    },
    clear() {
      this.pending = null
    }
  }
})
