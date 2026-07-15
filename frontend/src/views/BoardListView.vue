<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useBoardStore } from '../stores/board'
import { useCategoryStore } from '../stores/categories'
import { useLocalMetaStore } from '../stores/localMeta'
import { useRegionStore } from '../stores/region'
import { useTourPlaces } from '../composables/useTourPlaces'
import { regionLabelForPost } from '../utils/region'
import { fetchComments } from '../api/comments'
import LikeBookmarkBar from '../components/common/LikeBookmarkBar.vue'
import PixelIcon from '../components/common/PixelIcon.vue'

const PAGE_SIZE = 10

const { t } = useI18n()
const boardStore = useBoardStore()
const categoryStore = useCategoryStore()
const metaStore = useLocalMetaStore()
const regionStore = useRegionStore()
const { clusters: regionClusters, ensureTourPlacesLoaded } = useTourPlaces()

const selectedCategoryId = ref(null)
const keywordDraft = ref('')
const activeKeyword = ref('')
const page = ref(1)
const sortMode = ref('latest')
const activeTag = ref(null)
const commentCounts = reactive({})

const totalPages = computed(() => Math.max(1, Math.ceil(boardStore.total / PAGE_SIZE)))

const load = async () => {
  await boardStore.loadPosts({
    category_id: selectedCategoryId.value ?? undefined,
    region: regionStore.selectedRegion,
    keyword: activeKeyword.value || undefined,
    page: page.value,
    limit: PAGE_SIZE
  })
  loadCommentCounts()
}

const loadCommentCounts = async () => {
  const results = await Promise.all(
    boardStore.posts.map(async (post) => {
      try {
        const { data } = await fetchComments(post.id)
        return [post.id, data.length]
      } catch {
        return [post.id, 0]
      }
    })
  )
  results.forEach(([id, count]) => {
    commentCounts[id] = count
  })
}

const regionLabel = (post) => regionLabelForPost(post, regionClusters.value)

const visiblePosts = computed(() => {
  let list = boardStore.posts
  if (activeTag.value) {
    const idsWithTag = metaStore.postIdsWithTag(activeTag.value)
    list = list.filter((post) => idsWithTag.includes(String(post.id)))
  }
  if (sortMode.value === 'popular') {
    list = [...list].sort((a, b) => b.view_count - a.view_count)
  }
  return list
})

const selectCategory = (categoryId) => {
  selectedCategoryId.value = categoryId
  page.value = 1
}

const submitSearch = () => {
  activeKeyword.value = keywordDraft.value.trim()
  page.value = 1
}

const toggleTag = (tag) => {
  activeTag.value = activeTag.value === tag ? null : tag
}

const clearFilters = () => {
  selectedCategoryId.value = null
  keywordDraft.value = ''
  activeKeyword.value = ''
  activeTag.value = null
  sortMode.value = 'latest'
  page.value = 1
}

const goToPage = (next) => {
  if (next < 1 || next > totalPages.value) return
  page.value = next
}

watch([selectedCategoryId, activeKeyword, page], load)
watch(
  () => regionStore.selectedRegion,
  () => {
    page.value = 1
    load()
  }
)

onMounted(async () => {
  ensureTourPlacesLoaded()
  await Promise.all([categoryStore.ensureLoaded(), load()])
})
</script>

<template>
  <section class="board-list">
    <div class="page-header">
      <div>
        <h1 class="page-title">{{ t('board.listTitle') }}</h1>
      </div>
      <router-link to="/board/new" class="btn btn-primary">{{ t('board.writeCta') }}</router-link>
    </div>

    <div class="panel filters">
      <nav class="category-filter">
        <button
          type="button"
          class="btn btn-sm"
          :class="selectedCategoryId === null ? 'btn-primary' : 'btn-outline'"
          @click="selectCategory(null)"
        >
          {{ t('common.all') }}
        </button>
        <button
          v-for="category in categoryStore.categories"
          :key="category.id"
          type="button"
          class="btn btn-sm"
          :class="selectedCategoryId === category.id ? 'btn-primary' : 'btn-outline'"
          @click="selectCategory(category.id)"
        >
          {{ category.name }}
        </button>
      </nav>

      <form class="search-form" @submit.prevent="submitSearch">
        <input v-model="keywordDraft" type="search" :placeholder="t('board.searchPlaceholder')" />
        <button type="submit" class="btn btn-outline btn-sm">{{ t('common.search') }}</button>
      </form>

      <div class="sort-toggle">
        <button
          type="button"
          class="btn btn-sm"
          :class="sortMode === 'latest' ? 'btn-primary' : 'btn-outline'"
          @click="sortMode = 'latest'"
        >
          {{ t('board.sortLatest') }}
        </button>
        <button
          type="button"
          class="btn btn-sm"
          :class="sortMode === 'popular' ? 'btn-primary' : 'btn-outline'"
          @click="sortMode = 'popular'"
        >
          {{ t('board.sortPopular') }}
        </button>
      </div>

      <div v-if="metaStore.allTags.length" class="tag-filter">
        <span class="tag-filter-label">{{ t('board.tagFilterLabel') }}</span>
        <button
          v-for="tag in metaStore.allTags"
          :key="tag"
          type="button"
          class="tag-chip"
          :class="{ 'tag-chip--active': activeTag === tag }"
          @click="toggleTag(tag)"
        >
          {{ tag }}
        </button>
      </div>

      <button type="button" class="btn btn-ghost btn-sm clear-filters" @click="clearFilters">
        {{ t('board.clearFilters') }}
      </button>
    </div>

    <p v-if="boardStore.loading" class="loading-state">{{ t('common.loading') }}</p>

    <div v-else class="post-grid">
      <router-link
        v-for="post in visiblePosts"
        :key="post.id"
        :to="`/board/${post.id}`"
        class="post-card card"
      >
        <div class="post-card-top">
          <span v-for="categoryId in post.category_ids" :key="categoryId" class="badge">
            {{ categoryStore.nameOf(categoryId) }}
          </span>
          <span v-if="regionLabel(post)" class="badge badge-muted">{{ regionLabel(post) }}</span>
        </div>
        <h3 class="post-card-title">{{ post.title }}</h3>
        <div class="post-card-tags" v-if="metaStore.tagsFor(post.id).length">
          <span v-for="tag in metaStore.tagsFor(post.id)" :key="tag" class="tag-chip">{{ tag }}</span>
        </div>
        <div class="post-card-footer">
          <span class="post-card-meta">{{ post.created_at?.slice(0, 10) }}</span>
          <span class="post-card-meta"><PixelIcon name="eye" :size="12" /> {{ post.view_count }}</span>
          <span class="post-card-meta"><PixelIcon name="chat" :size="12" /> {{ commentCounts[post.id] ?? 0 }}</span>
          <LikeBookmarkBar :post-id="post.id" compact />
        </div>
      </router-link>

      <p v-if="!visiblePosts.length" class="empty-state">{{ t('board.empty') }}</p>
    </div>

    <div v-if="!boardStore.loading && boardStore.total > 0" class="pagination">
      <button type="button" class="btn btn-outline btn-sm" :disabled="page <= 1" @click="goToPage(page - 1)">
        {{ t('board.prev') }}
      </button>
      <span class="page-info">
        {{ t('board.pageInfo', { page, totalPages, total: boardStore.total }) }}
      </span>
      <button
        type="button"
        class="btn btn-outline btn-sm"
        :disabled="page >= totalPages"
        @click="goToPage(page + 1)"
      >
        {{ t('board.next') }}
      </button>
    </div>
  </section>
</template>

<style scoped>
.board-list {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.filters {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.category-filter {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.search-form {
  display: flex;
  gap: 8px;
}

.search-form input {
  flex: 1;
}

.sort-toggle {
  display: flex;
  gap: 8px;
}

.tag-filter {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-filter-label {
  font-size: 0.8rem;
  color: var(--color-text-muted);
  margin-right: 4px;
}

.tag-chip {
  cursor: pointer;
  background: none;
  font-family: inherit;
}

.tag-chip--active {
  background: var(--color-primary-soft);
  border-color: var(--color-primary);
  color: var(--color-primary-dark);
}

.clear-filters {
  align-self: flex-start;
}

.post-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 14px;
}

.post-card {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 16px;
  color: var(--color-text);
  transition: transform 0.12s ease, box-shadow 0.12s ease, border-color 0.12s ease;
}

.post-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--color-primary-light);
}

.post-card-top {
  display: flex;
  gap: 6px;
}

.post-card-title {
  margin: 0;
  font-size: 1.02rem;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.post-card-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.post-card-footer {
  margin-top: auto;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

.post-card-meta {
  white-space: nowrap;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.page-info {
  font-size: 0.85rem;
  color: var(--color-text-muted);
}
</style>
