<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { deletePost } from '../api/posts'
import { useBoardStore } from '../stores/board'
import { useLocalMetaStore } from '../stores/localMeta'
import { useMapFocusStore } from '../stores/mapFocus'
import { useTourPlaces } from '../composables/useTourPlaces'
import { regionLabelForPost } from '../utils/region'
import { resetPageHead, setPageHead } from '../utils/head'
import LikeBookmarkBar from '../components/common/LikeBookmarkBar.vue'
import ShareButtons from '../components/common/ShareButtons.vue'
import TagInput from '../components/common/TagInput.vue'
import PixelIcon from '../components/common/PixelIcon.vue'
import CommentSection from '../components/board/CommentSection.vue'

const props = defineProps({ id: { type: [String, Number], required: true } })
const router = useRouter()
const { t } = useI18n()
const boardStore = useBoardStore()
const metaStore = useLocalMetaStore()
const mapFocusStore = useMapFocusStore()
const { clusters: regionClusters, ensureTourPlacesLoaded } = useTourPlaces()

const showDeleteConfirm = ref(false)
const deletePassword = ref('')
const deleteError = ref('')

const regionLabel = computed(() => {
  if (!boardStore.currentPost) return ''
  return regionLabelForPost(boardStore.currentPost, regionClusters.value)
})

const tags = computed({
  get: () => metaStore.tagsFor(props.id),
  set: (value) => metaStore.setTags(props.id, value)
})

const viewPlaceOnMap = (place) => {
  if (!place?.map_x || !place?.map_y) return
  mapFocusStore.request({
    // PostPlace rows have their own real, stable id — using it here (rather
    // than leaving id unset) is what makes the speech bubble's "add to
    // route" button show up and work for a post's attached place too, not
    // just chat-referenced ones.
    id: `post-place-${place.id}`,
    lat: place.map_y,
    lng: place.map_x,
    title: place.place_name || boardStore.currentPost?.title,
    addr: place.address,
    type: 'tour',
    icon: 'pin'
  })
  router.push('/')
}

const load = async () => {
  await boardStore.loadPost(props.id)
  if (boardStore.currentPost) {
    setPageHead({
      title: boardStore.currentPost.title,
      description: boardStore.currentPost.content?.slice(0, 100)
    })
  }
}

const goBack = () => {
  router.back()
}

const openDeleteConfirm = () => {
  deleteError.value = ''
  deletePassword.value = ''
  showDeleteConfirm.value = true
}

const cancelDelete = () => {
  deleteError.value = ''
  deletePassword.value = ''
  showDeleteConfirm.value = false
}

const confirmDelete = async () => {
  const password = deletePassword.value.trim()
  if (!password) {
    deleteError.value = t('board.detail.deletePasswordRequired')
    return
  }

  deleteError.value = ''
  try {
    await deletePost(props.id, password)
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
      <button type="button" class="btn btn-ghost btn-icon detail-back-btn" :title="t('common.back')" @click="goBack">
        <PixelIcon name="arrowLeft" :size="16" />
      </button>
      <div class="detail-badges">
        <span v-for="name in boardStore.currentPost.category_names" :key="name" class="badge">{{ name }}</span>
        <span v-if="regionLabel" class="badge badge-muted">{{ regionLabel }}</span>
      </div>
      <div class="detail-title-row">
        <div>
          <h1 class="detail-title">{{ boardStore.currentPost.title }}</h1>
          <p class="detail-meta">
            {{ t('common.createdAt') }} {{ boardStore.currentPost.created_at?.slice(0, 16).replace('T', ' ') }}
            · {{ t('common.viewCount') }} {{ boardStore.currentPost.view_count }}
          </p>
        </div>
        <div class="detail-action-buttons">
          <router-link :to="`/board/${id}/edit`" class="btn btn-outline btn-sm">
            {{ t('board.detail.editButton') }}
          </router-link>
          <button type="button" class="btn btn-danger btn-sm delete-action-button" @click="openDeleteConfirm">
            {{ t('board.detail.deleteButton') }}
          </button>
        </div>
      </div>

      <Teleport to="body">
        <div v-if="showDeleteConfirm" class="delete-modal-backdrop" @click.self="cancelDelete">
          <div class="delete-modal" role="dialog" aria-modal="true" aria-label="Delete confirmation" @click.stop>
            <div class="delete-modal__header">
              <strong>{{ t('board.detail.deletePanelTitle') }}</strong>
              <button type="button" class="btn btn-ghost btn-sm" @click="cancelDelete">×</button>
            </div>
            <p class="delete-modal__description">{{ t('board.detail.deletePanelDescription') }}</p>
            <input
              v-model="deletePassword"
              type="password"
              :placeholder="t('board.detail.deleteConfirmPlaceholder')"
            />
            <div class="delete-modal__actions">
              <button type="button" class="btn btn-ghost btn-sm" @click="cancelDelete">
                {{ t('common.cancel') }}
              </button>
              <button type="button" class="btn btn-danger btn-sm" @click="confirmDelete">
                {{ t('board.detail.deleteConfirmButton') }}
              </button>
            </div>
            <p v-if="deleteError" class="error">{{ deleteError }}</p>
          </div>
        </div>
      </Teleport>
      <div class="detail-actions-row">
        <LikeBookmarkBar :post-id="id" />
        <ShareButtons :title="boardStore.currentPost.title" :description="boardStore.currentPost.content" />
      </div>
    </header>

    <div v-if="boardStore.currentPost.places?.length" class="detail-places">
      <div v-for="place in boardStore.currentPost.places" :key="place.id" class="detail-address">
        <PixelIcon name="pin" :size="14" />
        <div class="detail-address-body">
          <strong v-if="place.place_name">{{ place.place_name }}</strong>
          <span v-if="place.address">{{ place.address }}</span>
        </div>
        <button
          v-if="place.map_x && place.map_y"
          type="button"
          class="btn btn-outline btn-sm"
          @click="viewPlaceOnMap(place)"
        >
          {{ t('board.detail.viewOnMap') }}
        </button>
      </div>
    </div>

    <div v-if="boardStore.currentPost.image_url" class="detail-image-wrap">
      <img :src="boardStore.currentPost.image_url" alt="" />
    </div>

    <div class="detail-content">{{ boardStore.currentPost.content }}</div>

    <div class="detail-tags">
      <h4>{{ t('board.detail.tagsTitle') }}</h4>
      <TagInput v-model="tags" :placeholder="t('board.detail.addTagPlaceholder')" />
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

.detail-back-btn {
  align-self: flex-start;
}

.detail-badges {
  display: flex;
  gap: 6px;
}

.detail-title-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
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

.detail-action-buttons {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
  align-items: center;
}

.delete-action-button {
  font-weight: 800;
  letter-spacing: 0.01em;
  border: 2px solid #b33a2d !important;
  box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.7) inset;
  background: #d6452d !important;
  color: #ffffff !important;
  min-width: 72px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.delete-action-button:hover {
  background: #b93623 !important;
  color: #ffffff !important;
}

.detail-places {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-address {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: 2px solid var(--color-shadow, #4a3728);
  border-radius: 4px;
  background: var(--color-primary-soft);
}

.detail-address-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
  font-size: 0.85rem;
}

.detail-address-body span {
  font-size: 0.78rem;
  color: var(--color-text-muted);
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

.delete-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 2147483647;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(2, 6, 23, 0.72);
  backdrop-filter: blur(2px);
}

.delete-modal {
  width: min(420px, 100%);
  padding: 18px;
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-lg);
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.delete-modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.delete-modal__description {
  margin: 0;
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

.delete-modal input {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface-alt);
  color: var(--color-text);
}

.delete-modal__actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.detail-divider {
  border: none;
  border-top: 1px solid var(--color-border);
  margin: 0;
}
</style>
