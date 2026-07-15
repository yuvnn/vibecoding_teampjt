import { defineStore } from 'pinia'
import { fetchPosts } from '../api/posts'
import { useToastStore } from './toast'
import i18n from '../i18n'

const POLL_INTERVAL_MS = 20000
const MAX_ITEMS = 20

export const useNotificationStore = defineStore('notifications', {
  state: () => ({
    items: [],
    lastSeenPostId: null,
    started: false
  }),
  getters: {
    unreadCount: (state) => state.items.filter((item) => !item.read).length
  },
  actions: {
    markAllRead() {
      this.items.forEach((item) => {
        item.read = true
      })
    },
    async poll() {
      try {
        const { data } = await fetchPosts({ limit: 5 })
        const latest = data.posts[0]
        if (!latest) return
        if (this.lastSeenPostId === null) {
          this.lastSeenPostId = latest.id
          return
        }
        const newPosts = data.posts.filter((post) => post.id > this.lastSeenPostId)
        if (!newPosts.length) return

        this.lastSeenPostId = Math.max(this.lastSeenPostId, ...newPosts.map((post) => post.id))
        this.items = [
          ...newPosts.map((post) => ({ id: post.id, title: post.title, read: false })),
          ...this.items
        ].slice(0, MAX_ITEMS)

        const toastStore = useToastStore()
        toastStore.push(i18n.global.t('home.newPostToast', { title: newPosts[0].title }), {
          type: 'success'
        })
      } catch {
        // silent: polling is a soft real-time nicety, not critical path
      }
    },
    startPolling() {
      if (this.started) return
      this.started = true
      this.poll()
      setInterval(() => this.poll(), POLL_INTERVAL_MS)
    }
  }
})
