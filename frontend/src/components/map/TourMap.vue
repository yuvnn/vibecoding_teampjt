<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { renderPixelIconSVG } from '../../utils/pixelIcons'
import { useThemeStore } from '../../stores/theme'
import i18n from '../../i18n'

// Standard OSM tiles keep their natural, saturated colors (green parks, blue
// water, etc.) instead of the muted CARTO Voyager look. Dark mode reuses the
// same tiles with a CSS filter (invert + hue-rotate) on the tile pane only,
// so the map goes dark while roads/parks/water stay visually distinct —
// unlike a flat "all black" dark basemap.
const TILE_URL = 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
const TILE_ATTRIBUTION = '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'

const props = defineProps({
  tourPins: { type: Array, default: () => [] },
  regionPins: { type: Array, default: () => [] },
  selectedIds: { type: Array, default: () => [] },
  center: { type: Object, default: () => ({ lat: 36.3504, lng: 127.3845 }) }
})
const emit = defineEmits(['pin-click', 'region-click', 'add-route', 'view-change'])

const mapEl = ref(null)
const themeStore = useThemeStore()

let mapInstance = null
let tileLayer = null
let pinOverlays = []
let regionOverlays = []
let polyline = null
const markerById = new Map()

function applyTileLayer() {
  if (!mapInstance || tileLayer) return
  tileLayer = L.tileLayer(TILE_URL, {
    maxZoom: 19,
    subdomains: 'abc',
    attribution: TILE_ATTRIBUTION
  }).addTo(mapInstance)
}

function buildPopupContent(pin, { showRouteButton = true, onImageLoad } = {}) {
  const t = i18n.global.t
  const wrap = document.createElement('div')
  wrap.className = 'pin-popup'

  if (pin.image) {
    const img = document.createElement('img')
    img.src = pin.image
    img.alt = ''
    img.className = 'pin-popup-image'
    // Popup size/tip position is computed before the image has a height;
    // ask Leaflet to recompute once it loads so the bubble doesn't clip.
    img.addEventListener('load', () => onImageLoad?.())
    wrap.appendChild(img)
  }

  const title = document.createElement('div')
  title.className = 'pin-popup-title'
  title.textContent = pin.title
  wrap.appendChild(title)

  if (pin.addr) {
    const addr = document.createElement('div')
    addr.className = 'pin-popup-addr'
    addr.textContent = pin.addr
    wrap.appendChild(addr)
  }

  if (showRouteButton) {
    // Toggle the button's own state immediately instead of closing the
    // popup on click — closing it hid the "added" confirmation entirely,
    // which read as the button silently not working.
    let selected = props.selectedIds.includes(pin.id)
    const btn = document.createElement('button')
    btn.type = 'button'
    const applyState = () => {
      btn.className = `pin-popup-btn${selected ? ' pin-popup-btn--active' : ''}`
      btn.textContent = selected ? t('home.addedToRoute') : t('home.addToRoute')
    }
    applyState()
    btn.addEventListener('click', (event) => {
      event.stopPropagation()
      selected = !selected
      applyState()
      emit('add-route', pin)
    })
    wrap.appendChild(btn)
  }

  return wrap
}

function clearPinOverlays() {
  pinOverlays.forEach((marker) => marker.remove())
  pinOverlays = []
  markerById.clear()
}

function clearRegionOverlays() {
  regionOverlays.forEach((marker) => marker.remove())
  regionOverlays = []
}

function clearPolyline() {
  polyline?.remove()
  polyline = null
}

function renderTourPins() {
  if (!mapInstance) return
  clearPinOverlays()
  props.tourPins.forEach((pin, index) => {
    const selected = props.selectedIds.includes(pin.id)
    const content = document.createElement('div')
    content.className = `map-pin map-pin--${pin.type}${selected ? ' map-pin--selected' : ''}`
    content.innerHTML = renderPixelIconSVG(pin.icon || 'pin', { size: 16, color: '#fff' })
    content.title = pin.title
    content.style.animationDelay = `${(index % 6) * 0.3}s`
    const icon = L.divIcon({ html: content, className: 'map-pin-icon-wrap', iconSize: [30, 30], iconAnchor: [15, 30] })
    const marker = L.marker([pin.lat, pin.lng], { icon })
    marker.bindPopup(
      () => buildPopupContent(pin, { onImageLoad: () => marker.getPopup()?.update() }),
      { className: 'pin-popup-wrap', closeButton: true }
    )
    marker.on('click', () => emit('pin-click', pin))
    marker.addTo(mapInstance)
    pinOverlays.push(marker)
    markerById.set(pin.id, marker)
  })
}

function renderRegionPins() {
  if (!mapInstance) return
  clearRegionOverlays()
  props.regionPins.forEach((region, index) => {
    const content = document.createElement('div')
    content.className = 'map-region-badge'
    const strong = document.createElement('strong')
    strong.textContent = region.label
    const span = document.createElement('span')
    span.textContent = String(region.count)
    content.append(strong, span)
    content.style.animationDelay = `${(index % 5) * 0.4}s`
    const icon = L.divIcon({ html: content, className: 'map-region-icon-wrap', iconAnchor: [0, 0] })
    // Leaflet auto z-orders markers by latitude, so a region badge can end
    // up buried under nearby tour pins in a dense cluster — force it above
    // regular pins so it's always clickable.
    const marker = L.marker([region.lat, region.lng], { icon, zIndexOffset: 1000 })
    marker.on('click', () => emit('region-click', region))
    marker.addTo(mapInstance)
    regionOverlays.push(marker)
  })
}

function renderRoute() {
  if (!mapInstance) return
  clearPolyline()
  const points = props.selectedIds
    .map((id) => props.tourPins.find((pin) => pin.id === id))
    .filter(Boolean)
  if (points.length < 2) return

  polyline = L.polyline(
    points.map((p) => [p.lat, p.lng]),
    { weight: 4, color: '#8b7256', opacity: 0.9, dashArray: '2, 6' }
  ).addTo(mapInstance)
  mapInstance.fitBounds(polyline.getBounds(), { padding: [40, 40] })
}

onMounted(() => {
  mapInstance = L.map(mapEl.value).setView([props.center.lat, props.center.lng], 8)
  applyTileLayer()
  renderTourPins()
  renderRegionPins()
  renderRoute()
  // Popovers anchored to a pin's screen position (e.g. the posts-per-region
  // panel) go stale once the user pans/zooms — let listeners know to close
  // or reposition them.
  mapInstance.on('move zoom', () => emit('view-change'))
})

watch(() => props.tourPins, renderTourPins)
watch(() => props.regionPins, renderRegionPins)
watch(
  () => props.selectedIds,
  () => {
    renderTourPins()
    renderRoute()
  },
  { deep: true }
)

onBeforeUnmount(() => {
  clearPinOverlays()
  clearRegionOverlays()
  clearPolyline()
  mapInstance?.remove()
  mapInstance = null
})

let adhocPopup = null

defineExpose({
  // Zooms/pans to fit a set of region clusters — used when the header's
  // region selector changes so the map actually shows the newly picked area.
  fitToClusters(clusters) {
    if (!mapInstance || !clusters?.length) return
    if (clusters.length === 1) {
      mapInstance.flyTo([clusters[0].lat, clusters[0].lng], 12, { duration: 0.8 })
      return
    }
    const bounds = L.latLngBounds(clusters.map((c) => [c.lat, c.lng]))
    mapInstance.flyToBounds(bounds, { padding: [60, 60], duration: 0.8, maxZoom: 12 })
  },
  // Pixel position (relative to the map container) of a lat/lng — used to
  // anchor Vue-rendered overlays (like the posts-per-region panel) directly
  // above the marker that was clicked, instead of a fixed screen corner.
  screenPoint(lat, lng) {
    if (!mapInstance || lat == null || lng == null) return null
    const point = mapInstance.latLngToContainerPoint([lat, lng])
    return { x: point.x, y: point.y }
  },
  flyTo(pinId) {
    const marker = markerById.get(pinId)
    if (!marker || !mapInstance) return
    mapInstance.flyTo(marker.getLatLng(), Math.max(mapInstance.getZoom(), 13), { duration: 0.6 })
    marker.openPopup()
  },
  // Fly to an arbitrary lat/lng and show an info bubble — used by the
  // chatbot, which may reference places that aren't among the currently
  // rendered/toggled-on pins. Shows an add-route button when an id is given
  // (chat place refs carry one; freeform post-attached places don't).
  focusAdhoc({ lat, lng, title, addr, image, id, type = 'tour', icon }) {
    if (!mapInstance || lat == null || lng == null) return
    mapInstance.flyTo([lat, lng], Math.max(mapInstance.getZoom(), 14), { duration: 0.6 })
    adhocPopup?.remove()
    adhocPopup = L.popup({ className: 'pin-popup-wrap', closeButton: true }).setLatLng([lat, lng])
    const pin = { id, title, addr, image, lat, lng, type, icon }
    const content = buildPopupContent(pin, {
      showRouteButton: Boolean(id),
      onImageLoad: () => adhocPopup?.update()
    })
    adhocPopup.setContent(content).openOn(mapInstance)
  }
})
</script>

<template>
  <div class="tour-map-wrap">
    <div ref="mapEl" class="tour-map" :class="{ 'tour-map--dark': themeStore.mode === 'dark' }"></div>
  </div>
</template>

<style scoped>
.tour-map-wrap {
  position: relative;
  z-index: 0;
  width: 100%;
  height: 100%;
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.tour-map {
  width: 100%;
  height: 100%;
  min-height: 440px;
}
</style>

<style>
/* Leaflet overlay content is plain DOM created outside Vue's render tree, so
   these rules intentionally live in an unscoped block. */

/* Dark mode: invert + hue-rotate the tile pane only (not markers/popups) so
   the map goes dark while roads/parks/water keep distinguishable hues,
   instead of rendering as a flat black basemap. */
.tour-map--dark .leaflet-tile-pane {
  filter: invert(1) hue-rotate(180deg) brightness(0.95) contrast(0.85) saturate(0.75);
}

.map-pin-icon-wrap,
.map-region-icon-wrap {
  background: transparent;
  border: none;
}

.map-pin {
  width: 30px;
  height: 30px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  color: #fff;
  cursor: pointer;
  border: 2px solid var(--color-shadow, #4a3728);
  box-shadow: 2px 2px 0 var(--color-shadow, #4a3728);
  transition: transform 0.12s ease;
  animation: floaty 3.2s ease-in-out infinite;
}

.map-pin:hover {
  animation-play-state: paused;
  transform: scale(1.12);
}

.map-pin--tour {
  background: var(--color-primary, #6fae68);
}

.map-pin--food {
  background: var(--color-warning, #e8b84b);
}

.map-pin--leports {
  background: #5a8fd6;
}

.map-pin--culture {
  background: #a875c9;
}

.map-pin--shopping {
  background: #e07bb0;
}

.map-pin--stay {
  background: #4fb0a5;
}

.map-pin--course {
  background: #c98a4b;
}

.map-pin--festival {
  background: #e0567a;
}

.map-pin--selected {
  outline: 3px solid var(--color-danger, #e0654b);
  animation-play-state: paused;
  transform: scale(1.15);
}

.map-region-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
  padding: 6px 10px;
  border-radius: 4px;
  background: var(--color-primary-dark, #4f8a4f);
  color: #fff;
  font-size: 11px;
  cursor: pointer;
  white-space: nowrap;
  border: 2px solid var(--color-shadow, #4a3728);
  box-shadow: 2px 2px 0 var(--color-shadow, #4a3728);
  animation: floaty 3.6s ease-in-out infinite;
}

.map-region-badge:hover {
  animation-play-state: paused;
}

.map-region-badge strong {
  font-size: 11px;
  font-weight: 700;
}

.map-region-badge span {
  font-size: 13px;
  font-weight: 800;
}

/* Speech-bubble info window shown when a pin is clicked (Leaflet popup,
   restyled to match the app's pixel-art tone). */
.pin-popup-wrap .leaflet-popup-content-wrapper {
  background: var(--color-surface);
  color: var(--color-text);
  border: 2px solid var(--color-shadow, #4a3728);
  border-radius: 4px;
  box-shadow: 3px 3px 0 var(--color-shadow, #4a3728);
  padding: 0;
}

.pin-popup-wrap .leaflet-popup-content {
  margin: 10px 12px;
  min-width: 190px;
}

.pin-popup-wrap .leaflet-popup-tip-container {
  filter: none;
}

.pin-popup-wrap .leaflet-popup-tip {
  background: var(--color-surface);
  border: 2px solid var(--color-shadow, #4a3728);
  box-shadow: none;
}

.pin-popup-wrap .leaflet-popup-close-button {
  color: var(--color-text-muted) !important;
}

.pin-popup-image {
  display: block;
  width: 100%;
  height: 96px;
  object-fit: cover;
  border-radius: 2px;
  border: 2px solid var(--color-shadow, #4a3728);
  margin-bottom: 8px;
}

.pin-popup-title {
  font-weight: 800;
  font-size: 0.88rem;
  margin-bottom: 4px;
}

.pin-popup-addr {
  font-size: 0.74rem;
  color: var(--color-text-muted);
  margin-bottom: 8px;
}

.pin-popup-btn {
  width: 100%;
  padding: 6px 10px;
  border: 2px solid var(--color-shadow, #4a3728);
  border-radius: 4px;
  background: var(--color-primary);
  color: #fff;
  font-weight: 700;
  font-size: 0.78rem;
  cursor: pointer;
  box-shadow: 2px 2px 0 var(--color-shadow, #4a3728);
  transition: transform 0.08s ease, box-shadow 0.08s ease;
}

.pin-popup-btn:active {
  transform: translate(1px, 1px);
  box-shadow: 1px 1px 0 var(--color-shadow, #4a3728);
}

.pin-popup-btn--active {
  background: var(--color-surface-alt);
  color: var(--color-primary-dark);
}
</style>
