import { defineStore } from 'pinia'
import { fetchPost, fetchPosts } from '../api/posts'

export const useBoardStore = defineStore('board', {
  state: () => ({
    posts: [],
    total: 0,
    currentPost: null,
    loading: false
  }),
  actions: {
    async loadPosts(params) {
      this.loading = true
      try {
        const { data } = await fetchPosts(params)
        this.posts = data.posts
        this.total = data.total_count
      } finally {
        this.loading = false
      }
    },
    async loadPost(postId) {
      const { data } = await fetchPost(postId)
      this.currentPost = data
    }
  }
})
