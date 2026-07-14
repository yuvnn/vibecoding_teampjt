<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { fetchPosts } from '../api/posts'
import { groupPostsByRegion } from '../utils/region'
import { useToastStore } from '../stores/toast'
import { useTourPlaces } from '../composables/useTourPlaces'
import TourMap from '../components/map/TourMap.vue'
import LikeBookmarkBar from '../components/common/LikeBookmarkBar.vue'

const MAX_ROUTE_SELECTION = 6
const POLL_INTERVAL_MS = 20000

const { t } = useI18n()
const toastStore = useToastStore()
const { tourItems, foodItems, clusters: regionClusters, ensureTourPlacesLoaded } = useTourPlaces()

const posts = ref([])
const loading = ref(true)

const showTour = ref(true)
const showFood = ref(true)
const showPosts = ref(true)
const selectedIds = ref([])
const activeRegionId = ref(null)

let pollTimer = null
let lastSeenPostId = null

const toPins = (items, type) =>
  items
    .filter((item) => item.map_x && item.map_y)
    .map((item) => ({
      id: `${type}-${item.id}`,
      title: item.title,
      addr: item.addr1,
      lat: Number(item.map_y),
      lng: Number(item.map_x),
      type
    }))

const tourPins = computed(() => toPins(tourItems.value, 'tour'))
const foodPins = computed(() => toPins(foodItems.value, 'food'))
const allPlacePins = computed(() => [...tourPins.value, ...foodPins.value])

const regionGroups = computed(() => groupPostsByRegion(posts.value, regionClusters.value))

const visibleTourPins = computed(() => [
  ...(showTour.value ? tourPins.value : []),
  ...(showFood.value ? foodPins.value : [])
])

const visibleRegionPins = computed(() =>
  showPosts.value
    ? regionGroups.value.map((group) => ({
        id: group.cluster.id,
        label: group.cluster.label,
        lat: group.cluster.lat,
        lng: group.cluster.lng,
        count: group.posts.length
      }))
    : []
)

const selectedPins = computed(() =>
  selectedIds.value.map((id) => allPlacePins.value.find((pin) => pin.id === id)).filter(Boolean)
)

const activeRegion = computed(() =>
  regionGroups.value.find((group) => group.cluster.id === activeRegionId.value) ?? null
)

const recentPosts = computed(() => posts.value.slice(0, 5))

const onPinClick = (pin) => {
  const index = selectedIds.value.indexOf(pin.id)
  if (index !== -1) {
    selectedIds.value = selectedIds.value.filter((id) => id !== pin.id)
    return
  }
  if (selectedIds.value.length >= MAX_ROUTE_SELECTION) return
  selectedIds.value = [...selectedIds.value, pin.id]
}

const onRegionClick = (region) => {
  activeRegionId.value = activeRegionId.value === region.id ? null : region.id
}

const clearRoute = () => {
  selectedIds.value = []
}

const loadPosts = async () => {
  const { data } = await fetchPosts({ limit: 100 })
  posts.value = data.posts
  if (data.posts.length) {
    lastSeenPostId = Math.max(lastSeenPostId ?? 0, ...data.posts.map((post) => post.id))
  }
}

const pollForNewPosts = async () => {
  try {
    const { data } = await fetchPosts({ limit: 1 })
    const latest = data.posts[0]
    if (latest && lastSeenPostId !== null && latest.id > lastSeenPostId) {
      lastSeenPostId = latest.id
      toastStore.push(t('home.newPostToast', { title: latest.title }), { type: 'success' })
      loadPosts()
    }
  } catch {
    // silent: polling is a soft real-time nicety, not critical path
  }
}

onMounted(async () => {
  try {
    await Promise.all([ensureTourPlacesLoaded(), loadPosts()])
  } finally {
    loading.value = false
  }
  pollTimer = setInterval(pollForNewPosts, POLL_INTERVAL_MS)
})

onBeforeUnmount(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<template>
  <section class="home">
    <div class="home-banner">
      <h1>{{ t('home.title') }}</h1>
      <p>{{ t('home.subtitle') }}</p>
    </div>

    <div class="map-section">
      <div class="map-area">
        <TourMap
          :tour-pins="visibleTourPins"
          :region-pins="visibleRegionPins"
          :selected-ids="selectedIds"
          @pin-click="onPinClick"
          @region-click="onRegionClick"
        />

        <div class="map-toolbar">
          <span class="map-toolbar-title">{{ t('home.mapTitle') }}</span>
          <label class="layer-toggle">
            <input v-model="showTour" type="checkbox" />
            📍 {{ t('home.layerTour') }}
          </label>
          <label class="layer-toggle">
            <input v-model="showFood" type="checkbox" />
            🍽 {{ t('home.layerFood') }}
          </label>
          <label class="layer-toggle">
            <input v-model="showPosts" type="checkbox" />
            💬 {{ t('home.layerPosts') }}
          </label>
        </div>

        <aside class="route-panel">
          <h3>{{ t('home.routeTitle') }}</h3>
          <p class="route-hint">{{ t('home.routeHint') }}</p>
          <ol v-if="selectedPins.length" class="route-list">
            <li v-for="(pin, index) in selectedPins" :key="pin.id">
              <span class="route-index">{{ index + 1 }}</span>
              {{ pin.title }}
            </li>
          </ol>
          <p v-else class="route-empty">{{ t('home.routeEmpty') }}</p>
          <div class="route-footer">
            <span v-if="selectedPins.length" class="badge">
              {{ t('home.routeSelected', { count: selectedPins.length }) }}
            </span>
            <button
              v-if="selectedPins.length"
              type="button"
              class="btn btn-outline btn-sm"
              @click="clearRoute"
            >
              {{ t('home.routeClear') }}
            </button>
          </div>
        </aside>

        <div v-if="activeRegion" class="region-popover">
          <div class="region-popover-header">
            <strong>{{ activeRegion.cluster.label }}</strong>
            <button type="button" class="btn-icon" @click="activeRegionId = null">×</button>
          </div>
          <ul v-if="activeRegion.posts.length" class="region-popover-list">
            <li v-for="post in activeRegion.posts.slice(0, 5)" :key="post.id">
              <router-link :to="`/board/${post.id}`">{{ post.title }}</router-link>
            </li>
          </ul>
          <router-link to="/board" class="btn btn-primary btn-sm">
            {{ t('home.viewOnBoard') }}
          </router-link>
        </div>
      </div>
    </div>

    <div v-if="!loading" class="recent-section">
      <h2 class="panel-title">{{ t('home.recentPosts') }}</h2>
      <div class="recent-float-list">
        <div
          v-for="(post, index) in recentPosts"
          :key="post.id"
          class="recent-float-card"
          :style="{ animationDelay: `${index * 0.35}s` }"
        >
          <router-link :to="`/board/${post.id}`" class="recent-title">{{ post.title }}</router-link>
          <LikeBookmarkBar :post-id="post.id" compact />
        </div>
        <p v-if="!recentPosts.length" class="empty-state">{{ t('board.empty') }}</p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.home-banner {
  padding: 36px 32px;
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: #fff;
  box-shadow: var(--shadow-md);
}

.home-banner h1 {
  margin: 0 0 8px;
  font-size: 1.6rem;
}

.home-banner p {
  margin: 0;
  opacity: 0.9;
}

.panel-title {
  margin: 0;
  font-size: 1.1rem;
}

.map-section {
  width: 100%;
}

.map-area {
  position: relative;
  min-height: 520px;
  height: 60vh;
  max-height: 640px;
}

.map-toolbar {
  position: absolute;
  top: 16px;
  left: 16px;
  right: 16px;
  z-index: 6;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 14px;
  padding: 10px 16px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--color-surface) 78%, transparent);
  backdrop-filter: blur(10px);
  box-shadow: var(--shadow-md);
}

.map-toolbar-title {
  font-weight: 700;
  font-size: 0.92rem;
  margin-right: 4px;
}

.layer-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  color: var(--color-text-muted);
  cursor: pointer;
}

.layer-toggle input {
  width: auto;
  padding: 0;
}

.region-popover {
  position: absolute;
  left: 16px;
  bottom: 16px;
  width: 240px;
  background: color-mix(in srgb, var(--color-surface) 92%, transparent);
  backdrop-filter: blur(10px);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  padding: 14px;
  z-index: 5;
}

.region-popover-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.region-popover-header button {
  border: none;
  background: transparent;
  font-size: 1.1rem;
  cursor: pointer;
  color: var(--color-text-muted);
}

.region-popover-list {
  list-style: none;
  margin: 0 0 10px;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  max-height: 140px;
  overflow-y: auto;
}

.region-popover-list a {
  font-size: 0.85rem;
  color: var(--color-primary-dark);
}

.route-panel {
  position: absolute;
  top: 70px;
  right: 16px;
  width: 220px;
  z-index: 6;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: color-mix(in srgb, var(--color-surface) 88%, transparent);
  backdrop-filter: blur(10px);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
}

.route-panel h3 {
  margin: 0;
  font-size: 0.95rem;
}

.route-hint {
  margin: 0;
  font-size: 0.78rem;
  color: var(--color-text-muted);
}

.route-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 0.85rem;
}

.route-list li {
  display: flex;
  align-items: center;
  gap: 8px;
}

.route-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--color-primary-soft);
  color: var(--color-primary-dark);
  font-size: 0.7rem;
  font-weight: 700;
}

.route-empty {
  margin: 0;
  font-size: 0.82rem;
  color: var(--color-text-muted);
}

.route-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-top: auto;
}

.recent-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.recent-float-list {
  display: flex;
  flex-wrap: wrap;
  gap: 18px;
  padding: 8px 4px 24px;
}

.recent-float-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 18px;
  border-radius: 999px;
  background: var(--color-surface);
  box-shadow: var(--shadow-md);
  animation: floaty 4s ease-in-out infinite;
}

.recent-title {
  font-size: 0.92rem;
  font-weight: 500;
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recent-title:hover {
  color: var(--color-primary-dark);
}

@media (max-width: 860px) {
  .map-area {
    height: auto;
    min-height: 0;
  }

  .map-toolbar {
    position: static;
    margin-bottom: 12px;
    border-radius: var(--radius-lg);
    backdrop-filter: none;
  }

  .route-panel {
    position: static;
    width: auto;
    margin-top: 12px;
    backdrop-filter: none;
  }

  .region-popover {
    position: static;
    width: auto;
    margin-top: 12px;
    backdrop-filter: none;
  }
}
</style>
