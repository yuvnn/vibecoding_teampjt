<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { deletePost } from '../api/posts'
import { useBoardStore } from '../stores/board'
import { useLocalMetaStore } from '../stores/localMeta'
import { useTourPlaces } from '../composables/useTourPlaces'
import { inferPostRegion } from '../utils/region'
import { resetPageHead, setPageHead } from '../utils/head'
import LikeBookmarkBar from '../components/common/LikeBookmarkBar.vue'
import ShareButtons from '../components/common/ShareButtons.vue'
import TagInput from '../components/common/TagInput.vue'
import CommentSection from '../components/board/CommentSection.vue'

const props = defineProps({ id: { type: [String, Number], required: true } })
const router = useRouter()
const { t } = useI18n()
const boardStore = useBoardStore()
const metaStore = useLocalMetaStore()
const { clusters: regionClusters, ensureTourPlacesLoaded } = useTourPlaces()

const showDeleteConfirm = ref(false)
const deletePassword = ref('')
const deleteError = ref('')

const regionLabel = computed(() => {
  if (!boardStore.currentPost) return ''
  return inferPostRegion(boardStore.currentPost, regionClusters.value)?.label ?? ''
})

const tags = computed({
  get: () => metaStore.tagsFor(props.id),
  set: (value) => metaStore.setTags(props.id, value)
})

const load = async () => {
  await boardStore.loadPost(props.id)
  if (boardStore.currentPost) {
    setPageHead({
      title: boardStore.currentPost.title,
      description: boardStore.currentPost.content?.slice(0, 100)
    })
  }
}

const confirmDelete = async () => {
  deleteError.value = ''
  try {
    await deletePost(props.id, deletePassword.value)
    router.push('/board')
  } catch (err) {
    deleteError.value = err.response?.data?.detail ?? t('board.detail.deleteError')
  }
}

watch(() => props.id, load)

onMounted(async () => {
  ensureTourPlacesLoaded()
  await load()
})

onBeforeUnmount(resetPageHead)
</script>

<template>
  <section v-if="boardStore.currentPost" class="board-detail panel">
    <header class="detail-header">
      <div class="detail-badges">
        <span class="badge">{{ boardStore.currentPost.category_name }}</span>
        <span v-if="regionLabel" class="badge badge-muted">{{ regionLabel }}</span>
      </div>
      <h1 class="detail-title">{{ boardStore.currentPost.title }}</h1>
      <p class="detail-meta">
        {{ t('common.createdAt') }} {{ boardStore.currentPost.created_at?.slice(0, 16).replace('T', ' ') }}
        · {{ t('common.viewCount') }} {{ boardStore.currentPost.view_count }}
      </p>
      <div class="detail-actions-row">
        <LikeBookmarkBar :post-id="id" />
        <ShareButtons :title="boardStore.currentPost.title" :description="boardStore.currentPost.content" />
      </div>
    </header>

    <div class="detail-content">{{ boardStore.currentPost.content }}</div>

    <div class="detail-tags">
      <h4>{{ t('board.detail.tagsTitle') }}</h4>
      <TagInput v-model="tags" :placeholder="t('board.detail.addTagPlaceholder')" />
    </div>

    <div class="actions">
      <router-link :to="`/board/${id}/edit`" class="btn btn-outline btn-sm">
        {{ t('board.detail.editButton') }}
      </router-link>
      <button type="button" class="btn btn-danger btn-sm" @click="showDeleteConfirm = !showDeleteConfirm">
        {{ t('board.detail.deleteButton') }}
      </button>
    </div>

    <div v-if="showDeleteConfirm" class="password-confirm">
      <input
        v-model="deletePassword"
        type="password"
        :placeholder="t('board.detail.deleteConfirmPlaceholder')"
      />
      <button type="button" class="btn btn-danger btn-sm" @click="confirmDelete">
        {{ t('board.detail.deleteConfirmButton') }}
      </button>
      <p v-if="deleteError" class="error">{{ deleteError }}</p>
    </div>

    <hr class="detail-divider" />

    <CommentSection :post-id="id" />
  </section>
</template>

<style scoped>
.board-detail {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.detail-header {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-badges {
  display: flex;
  gap: 6px;
}

.detail-title {
  margin: 0;
  font-size: 1.4rem;
}

.detail-meta {
  margin: 0;
  color: var(--color-text-muted);
  font-size: 0.85rem;
}

.detail-actions-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 4px;
}

.detail-content {
  white-space: pre-wrap;
  line-height: 1.7;
  font-size: 0.98rem;
}

.detail-tags h4 {
  margin: 0 0 8px;
  font-size: 0.85rem;
  color: var(--color-text-muted);
}

.actions {
  display: flex;
  gap: 8px;
}

.password-confirm {
  display: flex;
  align-items: center;
  gap: 8px;
}

.password-confirm input {
  max-width: 220px;
}

.detail-divider {
  border: none;
  border-top: 1px solid var(--color-border);
  margin: 0;
}
</style>
