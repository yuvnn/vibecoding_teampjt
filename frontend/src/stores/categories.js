import { defineStore } from 'pinia'
import { fetchCategories } from '../api/categories'

export const useCategoryStore = defineStore('categories', {
  state: () => ({
    categories: [],
    loaded: false
  }),
  getters: {
    nameOf: (state) => (categoryId) =>
      state.categories.find((category) => category.id === categoryId)?.name ?? categoryId
  },
  actions: {
    async ensureLoaded() {
      if (this.loaded) return
      const { data } = await fetchCategories()
      this.categories = data
      this.loaded = true
    }
  }
})
