<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { fetchPosts } from '../api/posts'
import { groupPostsByRegion } from '../utils/region'
import { TOUR_CONTENT_TYPES } from '../utils/tourContentTypes'
import { useNotificationStore } from '../stores/notifications'
import { useRouteStore } from '../stores/route'
import { useMapFocusStore } from '../stores/mapFocus'
import { useRegionStore } from '../stores/region'
import { useTourPlaces } from '../composables/useTourPlaces'
import TourMap from '../components/map/TourMap.vue'
import PixelIcon from '../components/common/PixelIcon.vue'

const { t } = useI18n()
const notificationStore = useNotificationStore()
const routeStore = useRouteStore()
const mapFocusStore = useMapFocusStore()
const regionStore = useRegionStore()
const { itemsByType, clusters: regionClusters, ensureTourPlacesLoaded } = useTourPlaces()

const posts = ref([])
const mapRef = ref(null)

const activeTypes = reactive(
  Object.fromEntries(TOUR_CONTENT_TYPES.map((type) => [type.key, type.defaultOn]))
)
const showPosts = ref(true)
const activeRegionId = ref(null)
const toolbarCollapsed = ref(false)
// Collapsed by default on narrow screens so the floating panel only shows a
// couple of items at the top; desktop has room to show the full list. Also
// react to viewport changes (resize/rotate), not just the initial load.
const mobileQuery = typeof window !== 'undefined' ? window.matchMedia('(max-width: 860px)') : null
const recommendCollapsed = ref(mobileQuery?.matches ?? false)
const onMobileQueryChange = (event) => {
  recommendCollapsed.value = event.matches
}
onMounted(() => mobileQuery?.addEventListener('change', onMobileQueryChange))
onBeforeUnmount(() => mobileQuery?.removeEventListener('change', onMobileQueryChange))

// On mobile, the recommend/route panels live behind footer tabs instead of
// floating over the map — 'recommend' | 'route' | null.
const mobileSheet = ref(null)
const toggleMobileSheet = (name) => {
  mobileSheet.value = mobileSheet.value === name ? null : name
}

const allTypesSelected = computed({
  get: () => TOUR_CONTENT_TYPES.every((type) => activeTypes[type.key]),
  set: (value) => {
    TOUR_CONTENT_TYPES.forEach((type) => {
      activeTypes[type.key] = value
    })
  }
})

const RECOMMEND_COUNT = 10

const toPins = (items, type, icon) =>
  items
    .filter((item) => item.map_x && item.map_y)
    .map((item) => ({
      id: `${type}-${item.id}`,
      title: item.title,
      addr: item.addr1,
      image: item.first_image || '',
      lat: Number(item.map_y),
      lng: Number(item.map_x),
      type,
      icon
    }))

const recommendedPlaces = computed(() => {
  const withImage = (type) =>
    itemsByType[type.key]
      .filter((item) => item.map_x && item.map_y && item.first_image)
      .map((item) => ({
        id: `${type.key}-${item.id}`,
        title: item.title,
        addr: item.addr1,
        image: item.first_image,
        type: type.key,
        icon: type.icon
      }))

  const tour = withImage(TOUR_CONTENT_TYPES[0])
  const food = withImage(TOUR_CONTENT_TYPES[1])
  const merged = []
  for (let i = 0; i < Math.max(tour.length, food.length) && merged.length < RECOMMEND_COUNT; i += 1) {
    if (tour[i]) merged.push(tour[i])
    if (food[i] && merged.length < RECOMMEND_COUNT) merged.push(food[i])
  }
  return merged
})

const regionGroups = computed(() => groupPostsByRegion(posts.value, regionClusters.value))

const visibleTourPins = computed(() =>
  TOUR_CONTENT_TYPES.filter((type) => activeTypes[type.key]).flatMap((type) =>
    toPins(itemsByType[type.key], type.key, type.icon)
  )
)

// Some regions are missing source data for a given category entirely (e.g.
// no restaurant listings were collected for it) — that's not a filtering
// bug, but a checked-and-empty checkbox looks like one, so flag it instead.
const typeHasData = (key) => itemsByType[key]?.length > 0

// Fly the map to the newly selected region once its data has loaded, so
// switching regions actually shows that area instead of leaving the view
// wherever it was.
let isFirstClusterLoad = true
watch(
  () => regionClusters.value,
  (clusters) => {
    if (isFirstClusterLoad) {
      isFirstClusterLoad = false
      return
    }
    if (clusters.length) mapRef.value?.fitToClusters(clusters)
  }
)

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

const selectedIds = computed(() => routeStore.ids)
const selectedPins = computed(() => routeStore.items)

const activeRegion = computed(() =>
  regionGroups.value.find((group) => group.cluster.id === activeRegionId.value) ?? null
)

// Screen position of the clicked region pin, so its post-list panel opens
// right above the pin instead of a fixed corner of the map.
const activeRegionPoint = ref(null)

const onPinClick = () => {
  activeRegionId.value = null
}

const onAddRoute = (pin) => {
  routeStore.toggle({
    ...pin,
    lat: pin.lat ?? (pin.map_y != null ? Number(pin.map_y) : undefined),
    lng: pin.lng ?? (pin.map_x != null ? Number(pin.map_x) : undefined)
  })
}

const onRegionClick = (region) => {
  if (activeRegionId.value === region.id) {
    activeRegionId.value = null
    activeRegionPoint.value = null
    return
  }
  activeRegionId.value = region.id
  activeRegionPoint.value = mapRef.value?.screenPoint(region.lat, region.lng) ?? null
}

// Panning/zooming invalidates the anchored screen position — just close the
// panel rather than showing it in the wrong place.
const onMapViewChange = () => {
  if (activeRegionId.value) {
    activeRegionId.value = null
    activeRegionPoint.value = null
  }
}

const clearRoute = () => {
  routeStore.clear()
}

const focusPlace = (place) => {
  mapRef.value?.flyTo(place.id)
}

const loadPosts = async () => {
  const { data } = await fetchPosts({ limit: 100 })
  posts.value = data.posts
}

onMounted(async () => {
  await Promise.all([ensureTourPlacesLoaded(), loadPosts()])
  // The chat widget (or another page) may have requested a map focus before
  // this view/TourMap existed — honor it now that the map is mounted.
  if (mapFocusStore.pending) {
    mapRef.value?.focusAdhoc(mapFocusStore.pending)
    mapFocusStore.clear()
  }
})

// The notification store polls for new posts globally (see App.vue); when it
// notices one, refresh this view's full post list so the map regions update too.
watch(
  () => notificationStore.lastSeenPostId,
  (_current, previous) => {
    if (previous !== null) loadPosts()
  }
)

// Covers the case where the chat widget requests a focus while already on
// this page (TourMap is already mounted, so react immediately).
watch(
  () => mapFocusStore.pending,
  (place) => {
    if (!place) return
    mapRef.value?.focusAdhoc(place)
    mapFocusStore.clear()
  }
)
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
          ref="mapRef"
          :tour-pins="visibleTourPins"
          :region-pins="visibleRegionPins"
          :selected-ids="selectedIds"
          @pin-click="onPinClick"
          @region-click="onRegionClick"
          @add-route="onAddRoute"
          @view-change="onMapViewChange"
        />

        <div class="map-left-stack">
          <!-- Posts are a core feature, not just another filterable layer —
               kept out of the collapsible toolbar so it's always reachable. -->
          <button
            type="button"
            class="posts-toggle-chip"
            :class="{ 'posts-toggle-chip--active': showPosts }"
            @click="showPosts = !showPosts"
          >
            <PixelIcon name="chat" :size="14" :color="showPosts ? '#fff' : undefined" />
            {{ t('home.layerPosts') }}
          </button>

          <div class="map-toolbar" :class="{ 'map-toolbar--collapsed': toolbarCollapsed }">
            <span class="map-toolbar-title">{{ t('home.mapTitle') }}</span>
            <template v-if="!toolbarCollapsed">
              <label class="layer-toggle layer-toggle--all">
                <input v-model="allTypesSelected" type="checkbox" />
                {{ t('home.selectAll') }}
              </label>
              <label
                v-for="type in TOUR_CONTENT_TYPES"
                :key="type.key"
                class="layer-toggle"
                :class="{ 'layer-toggle--empty': !typeHasData(type.key) }"
                :title="!typeHasData(type.key) ? t('home.layerNoData') : undefined"
              >
                <input v-model="activeTypes[type.key]" type="checkbox" :disabled="!typeHasData(type.key)" />
                <PixelIcon :name="type.icon" :size="14" /> {{ t(type.labelKey) }}
              </label>
            </template>
            <button
              type="button"
              class="toolbar-collapse-btn"
              :title="toolbarCollapsed ? t('home.expandFilters') : t('home.collapseFilters')"
              @click="toolbarCollapsed = !toolbarCollapsed"
            >
              {{ toolbarCollapsed ? '▸' : '◂' }}
            </button>
          </div>

          <aside
            class="recommend-panel"
            :class="{
              'recommend-panel--collapsed': recommendCollapsed,
              'mobile-sheet--open': mobileSheet === 'recommend'
            }"
          >
            <div class="recommend-panel-header">
              <h3>{{ t('home.recommendTitle') }}</h3>
              <button
                type="button"
                class="toolbar-collapse-btn desktop-only"
                :title="recommendCollapsed ? t('home.recommendExpand') : t('home.recommendCollapse')"
                @click="recommendCollapsed = !recommendCollapsed"
              >
                {{ recommendCollapsed ? '▾' : '▴' }}
              </button>
              <button type="button" class="toolbar-collapse-btn mobile-only" @click="mobileSheet = null">×</button>
            </div>
            <ul v-if="recommendedPlaces.length" class="recommend-list">
              <li
                v-for="place in recommendedPlaces"
                :key="place.id"
                class="recommend-item"
                @click="focusPlace(place)"
              >
                <img :src="place.image" :alt="place.title" class="recommend-thumb" />
                <div class="recommend-body">
                  <span class="recommend-title">
                    <PixelIcon :name="place.icon" :size="11" />
                    {{ place.title }}
                  </span>
                  <span v-if="place.addr" class="recommend-addr">{{ place.addr }}</span>
                </div>
                <button
                  type="button"
                  class="recommend-add-btn"
                  :class="{ 'recommend-add-btn--active': selectedIds.includes(place.id) }"
                  @click.stop="onAddRoute(place)"
                >
                  {{ selectedIds.includes(place.id) ? '✓' : '+' }}
                </button>
              </li>
            </ul>
            <p v-else-if="!recommendCollapsed" class="route-empty">{{ t('home.recommendEmpty') }}</p>
          </aside>
        </div>

        <aside class="route-panel" :class="{ 'mobile-sheet--open': mobileSheet === 'route' }">
          <div class="route-panel-header">
            <h3>{{ t('home.routeTitle') }}</h3>
            <button type="button" class="toolbar-collapse-btn mobile-only" @click="mobileSheet = null">×</button>
          </div>
          <p class="route-hint">{{ t('home.routeHint') }}</p>
          <ol v-if="selectedPins.length" class="route-list">
            <li v-for="(pin, index) in selectedPins" :key="pin.id">
              <span class="route-index">{{ index + 1 }}</span>
              <PixelIcon v-if="pin.icon" :name="pin.icon" :size="12" />
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

        <div
          v-if="activeRegion && activeRegionPoint"
          class="region-popover"
          :style="{ left: `${activeRegionPoint.x}px`, top: `${activeRegionPoint.y}px` }"
        >
          <div class="region-popover-header">
            <strong>{{ activeRegion.cluster.label }}</strong>
            <button type="button" class="btn-icon" @click="activeRegionId = null; activeRegionPoint = null">×</button>
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

    <!-- Mobile only: recommend/route panels live behind these footer tabs
         instead of floating over the map (see .mobile-sheet--open above). -->
    <div class="mobile-footer">
      <button
        type="button"
        class="mobile-footer-btn"
        :class="{ 'mobile-footer-btn--active': mobileSheet === 'recommend' }"
        @click="toggleMobileSheet('recommend')"
      >
        <PixelIcon name="pin" :size="15" />
        {{ t('home.recommendTitle') }}
      </button>
      <button
        type="button"
        class="mobile-footer-btn"
        :class="{ 'mobile-footer-btn--active': mobileSheet === 'route' }"
        @click="toggleMobileSheet('route')"
      >
        <PixelIcon name="pin" :size="15" />
        {{ t('home.routeTitle') }}
        <span v-if="selectedPins.length" class="mobile-footer-badge">{{ selectedPins.length }}</span>
      </button>
    </div>
  </section>
</template>

<style scoped>
.home {
  position: fixed;
  top: var(--header-height);
  left: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
}

.home-banner {
  position: absolute;
  top: 16px;
  left: 16px;
  z-index: 8;
  max-width: 300px;
  padding: 16px 20px;
  border-radius: var(--radius-lg);
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: #fff;
  box-shadow: var(--shadow-md);
  /* Purely decorative, nothing inside is interactive — let every click
     pass straight through to the map. */
  pointer-events: none;
}

.home-banner h1 {
  margin: 0 0 6px;
  font-size: 1.15rem;
}

.home-banner p {
  margin: 0;
  font-size: 0.8rem;
  opacity: 0.9;
}

.map-section {
  position: absolute;
  inset: 0;
}

.map-area {
  position: relative;
  width: 100%;
  height: 100%;
}

.map-left-stack {
  position: absolute;
  top: 154px;
  left: 16px;
  z-index: 6;
  display: flex;
  flex-direction: column;
  gap: 12px;
  /* A concrete width (rather than the default shrink-to-fit-over-children
     sizing a bare max-width leaves you with) — that auto sizing based itself
     on whichever child currently had the most intrinsic content, so the
     toolbar and recommend panel could end up different widths depending on
     collapse state and viewport. This makes both always match exactly. */
  width: clamp(312px, 46vw, 660px);
  max-width: calc(100% - 32px);
  max-height: calc(100% - 170px);
  /* This flex container's own box is as wide as its widest child (the
     toolbar row), which leaves an invisible strip over the map below the
     shorter recommend panel — pointer-events:none lets clicks/popups on the
     map pass through that empty strip, while auto on the actual panels
     keeps them clickable. */
  pointer-events: none;
}

.map-toolbar,
.recommend-panel,
.posts-toggle-chip {
  pointer-events: auto;
}

.posts-toggle-chip {
  align-self: flex-start;
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: var(--radius-lg);
  border: 2px solid var(--color-shadow, #4a3728);
  background: color-mix(in srgb, var(--color-surface) 88%, transparent);
  backdrop-filter: blur(10px);
  box-shadow: var(--shadow-sm);
  color: var(--color-text);
  font-weight: 700;
  font-size: 0.85rem;
  cursor: pointer;
}

.posts-toggle-chip--active {
  background: var(--color-primary);
  color: #fff;
}

.map-toolbar {
  width: 100%;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px 14px;
  padding: 10px 16px;
  border-radius: var(--radius-lg);
  background: color-mix(in srgb, var(--color-surface) 78%, transparent);
  backdrop-filter: blur(10px);
  box-shadow: var(--shadow-md);
  /* Leaflet's own transform-based stacking context on its map pane bundles
     tiles/markers/popups together as one z-index unit — there is no pure
     z-index trick that lets a popup escape above this panel while a marker
     stays under it. So instead of claiming this panel's whole rectangle for
     clicks (which silently ate clicks on any popup/pin rendering underneath
     its padding or gaps), only the actual controls inside it are clickable;
     empty background passes clicks through to the map. */
  pointer-events: none;
}

.map-toolbar > * {
  pointer-events: auto;
}

/* Collapsed, there's nothing but the title and the arrow — no reason to
   stay stretched to the full (checkbox-driven) expanded width. */
.map-toolbar--collapsed {
  width: fit-content;
}

.map-toolbar-title {
  font-weight: 700;
  font-size: 0.92rem;
  flex-shrink: 0;
}

.layer-toggle--all {
  font-weight: 700;
  color: var(--color-primary-dark);
  flex-shrink: 0;
}

.toolbar-collapse-btn {
  flex-shrink: 0;
  margin-left: auto;
  border: none;
  background: transparent;
  color: var(--color-text-muted);
  font-size: 0.85rem;
  line-height: 1;
  padding: 4px 6px;
  cursor: pointer;
}

.toolbar-collapse-btn:hover {
  color: var(--color-primary-dark);
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

.layer-toggle--empty {
  opacity: 0.45;
  cursor: not-allowed;
}

.region-popover {
  position: absolute;
  width: 240px;
  /* Anchored to the clicked pin's screen point (top-left of its icon) —
     shift up and over so the panel sits centered directly above the pin,
     with a little clearance instead of covering it. */
  transform: translate(-40%, calc(-100% - 14px));
  background: color-mix(in srgb, var(--color-surface) 92%, transparent);
  backdrop-filter: blur(10px);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-lg);
  padding: 14px;
  z-index: 7;
  pointer-events: none;
}

.region-popover > * {
  pointer-events: auto;
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

.recommend-panel {
  /* Deliberately narrower than the toolbar (and fixed regardless of
     collapsed/expanded state) rather than stretching to match it. */
  width: 250px;
  flex: 1;
  min-height: 0;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background: color-mix(in srgb, var(--color-surface) 88%, transparent);
  backdrop-filter: blur(10px);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-md);
  overflow: hidden;
  /* See .map-toolbar's comment — only actual controls should intercept
     clicks, not this panel's whole background/padding. */
  pointer-events: none;
}

.recommend-panel > * {
  pointer-events: auto;
}

.recommend-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.recommend-panel-header h3 {
  margin: 0;
  font-size: 0.95rem;
}

.recommend-list {
  list-style: none;
  margin: 0;
  padding: 0 2px 0 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  transition: max-height 0.18s ease;
}

.recommend-panel--collapsed .recommend-list {
  max-height: 0;
  overflow: hidden;
}

.recommend-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background-color 0.12s ease;
}

.recommend-item:hover {
  background: var(--color-surface-alt);
}

.recommend-thumb {
  width: 42px;
  height: 42px;
  border-radius: 4px;
  object-fit: cover;
  flex-shrink: 0;
  border: 2px solid var(--color-shadow, transparent);
}

.recommend-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.recommend-title {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.82rem;
  font-weight: 600;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recommend-addr {
  font-size: 0.7rem;
  color: var(--color-text-muted);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recommend-add-btn {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid var(--color-shadow, #4a3728);
  background: var(--color-primary);
  color: #fff;
  font-weight: 800;
  font-size: 0.8rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.recommend-add-btn--active {
  background: var(--color-surface-alt);
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
  pointer-events: none;
}

.route-panel > * {
  pointer-events: auto;
}

.route-panel h3 {
  margin: 0;
  font-size: 0.95rem;
}

.route-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.mobile-only {
  display: none;
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

.mobile-footer {
  display: none;
}

@media (max-width: 860px) {
  /* The banner just repeats the page's own context on a screen where every
     pixel of map real estate matters — drop it entirely on mobile. */
  .home-banner {
    display: none;
  }

  .map-left-stack {
    top: 16px;
    max-height: calc(100% - 32px);
  }

  .map-toolbar {
    gap: 8px;
    padding: 8px 12px;
    font-size: 0.8rem;
  }

  /* Recommend/route panels become bottom sheets driven by the footer tabs
     below, instead of floating over the map — pulled fully offscreen until
     their tab is active. */
  .recommend-panel,
  .route-panel {
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    top: auto;
    width: 100%;
    max-width: 100%;
    max-height: 55vh;
    border-radius: var(--radius-lg) var(--radius-lg) 0 0;
    transform: translateY(100%);
    transition: transform 0.22s ease;
    z-index: 45;
    box-shadow: 0 -4px 16px rgba(0, 0, 0, 0.18);
  }

  .recommend-panel.mobile-sheet--open,
  .route-panel.mobile-sheet--open {
    transform: translateY(0);
  }

  /* The footer tab is the open/close control on mobile — the inline chevron
     duplicates it, so hide that and use a plain close (×) instead. */
  .desktop-only {
    display: none;
  }

  .mobile-only {
    display: inline-flex;
  }

  .recommend-panel--collapsed.mobile-sheet--open .recommend-list {
    max-height: none;
  }

  .mobile-footer {
    display: flex;
    position: fixed;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 46;
    background: var(--color-surface);
    border-top: 2px solid var(--color-shadow, #4a3728);
  }

  .mobile-footer-btn {
    flex: 1;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 12px 8px;
    border: none;
    background: transparent;
    color: var(--color-text-muted);
    font-weight: 700;
    font-size: 0.82rem;
    cursor: pointer;
  }

  .mobile-footer-btn--active {
    color: var(--color-primary-dark);
    background: var(--color-primary-soft);
  }

  .mobile-footer-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 18px;
    height: 18px;
    padding: 0 4px;
    border-radius: 999px;
    background: var(--color-primary);
    color: #fff;
    font-size: 0.68rem;
    font-weight: 800;
  }
}
</style>
