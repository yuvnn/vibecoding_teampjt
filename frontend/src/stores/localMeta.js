import { defineStore } from 'pinia'
import { hashCode } from '../utils/hash'

const STORAGE_KEY = 'localhub-post-meta'

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) throw new Error('empty')
    const parsed = JSON.parse(raw)
    return {
      likedIds: Array.isArray(parsed.likedIds) ? parsed.likedIds : [],
      bookmarkedIds: Array.isArray(parsed.bookmarkedIds) ? parsed.bookmarkedIds : [],
      tagsByPost: typeof parsed.tagsByPost === 'object' && parsed.tagsByPost ? parsed.tagsByPost : {}
    }
  } catch {
    return { likedIds: [], bookmarkedIds: [], tagsByPost: {} }
  }
}

/**
 * Likes/bookmarks/tags have no backend table yet, so they live in this
 * browser's localStorage only (per team decision — see plan doc). Like
 * counts add a small deterministic "base" derived from the post id so the
 * UI doesn't always show 0/1, while staying obviously client-side.
 */
export const useLocalMetaStore = defineStore('localMeta', {
  state: () => loadState(),
  getters: {
    isLiked: (state) => (postId) => state.likedIds.includes(String(postId)),
    isBookmarked: (state) => (postId) => state.bookmarkedIds.includes(String(postId)),
    tagsFor: (state) => (postId) => state.tagsByPost[String(postId)] ?? [],
    likeCount: (state) => (postId) => {
      const base = hashCode(`like:${postId}`) % 24
      return base + (state.likedIds.includes(String(postId)) ? 1 : 0)
    },
    allTags: (state) => {
      const set = new Set()
      Object.values(state.tagsByPost).forEach((tags) => tags.forEach((tag) => set.add(tag)))
      return [...set].sort((a, b) => a.localeCompare(b))
    },
    postIdsWithTag: (state) => (tag) =>
      Object.entries(state.tagsByPost)
        .filter(([, tags]) => tags.includes(tag))
        .map(([postId]) => postId)
  },
  actions: {
    persist() {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({
          likedIds: this.likedIds,
          bookmarkedIds: this.bookmarkedIds,
          tagsByPost: this.tagsByPost
        })
      )
    },
    toggleLike(postId) {
      const id = String(postId)
      const index = this.likedIds.indexOf(id)
      if (index === -1) this.likedIds.push(id)
      else this.likedIds.splice(index, 1)
      this.persist()
    },
    toggleBookmark(postId) {
      const id = String(postId)
      const index = this.bookmarkedIds.indexOf(id)
      if (index === -1) this.bookmarkedIds.push(id)
      else this.bookmarkedIds.splice(index, 1)
      this.persist()
    },
    setTags(postId, tags) {
      const id = String(postId)
      const clean = [...new Set(tags.map((tag) => tag.trim()).filter(Boolean))]
      this.tagsByPost[id] = clean
      this.persist()
    },
    addTag(postId, tag) {
      const trimmed = tag.trim()
      if (!trimmed) return
      const current = this.tagsFor(postId)
      if (current.includes(trimmed)) return
      this.setTags(postId, [...current, trimmed])
    },
    removeTag(postId, tag) {
      this.setTags(postId, this.tagsFor(postId).filter((t) => t !== tag))
    }
  }
})
