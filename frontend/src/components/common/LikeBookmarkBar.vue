<script setup>
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useLocalMetaStore } from '../../stores/localMeta'

const props = defineProps({
  postId: { type: [String, Number], required: true },
  compact: { type: Boolean, default: false }
})

const { t } = useI18n()
const metaStore = useLocalMetaStore()

const liked = computed(() => metaStore.isLiked(props.postId))
const bookmarked = computed(() => metaStore.isBookmarked(props.postId))
const likeCount = computed(() => metaStore.likeCount(props.postId))

const toggleLike = (event) => {
  event.stopPropagation()
  event.preventDefault()
  metaStore.toggleLike(props.postId)
}

const toggleBookmark = (event) => {
  event.stopPropagation()
  event.preventDefault()
  metaStore.toggleBookmark(props.postId)
}
</script>

<template>
  <div class="like-bookmark-bar" :class="{ 'like-bookmark-bar--compact': compact }">
    <button
      type="button"
      class="lb-btn"
      :class="{ 'lb-btn--active': liked }"
      :aria-pressed="liked"
      :title="t('board.likes')"
      @click="toggleLike"
    >
      <span>{{ liked ? '❤️' : '🤍' }}</span>
      <span>{{ likeCount }}</span>
    </button>
    <button
      type="button"
      class="lb-btn"
      :class="{ 'lb-btn--active': bookmarked }"
      :aria-pressed="bookmarked"
      :title="bookmarked ? t('board.bookmarkRemove') : t('board.bookmarkAdd')"
      @click="toggleBookmark"
    >
      <span>{{ bookmarked ? '🔖' : '📑' }}</span>
    </button>
  </div>
</template>

<style scoped>
.like-bookmark-bar {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.lb-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 5px 10px;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  color: var(--color-text-muted);
  font-size: 0.82rem;
  cursor: pointer;
  transition: border-color 0.12s ease, color 0.12s ease, transform 0.12s ease;
}

.lb-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary-dark);
}

.lb-btn:active {
  transform: scale(0.94);
}

.lb-btn--active {
  border-color: var(--color-primary);
  color: var(--color-primary-dark);
  background: var(--color-primary-soft);
}

.like-bookmark-bar--compact .lb-btn {
  padding: 3px 8px;
  font-size: 0.76rem;
}
</style>
