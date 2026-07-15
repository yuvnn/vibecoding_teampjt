<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { renderPixelIconSVG } from '../../utils/pixelIcons'

const props = defineProps({
  tourPins: { type: Array, default: () => [] },
  regionPins: { type: Array, default: () => [] },
  selectedIds: { type: Array, default: () => [] },
  center: { type: Object, default: () => ({ lat: 36.3504, lng: 127.3845 }) }
})
const emit = defineEmits(['pin-click', 'region-click'])

const mapEl = ref(null)

let mapInstance = null
let pinOverlays = []
let regionOverlays = []
let polyline = null

function clearPinOverlays() {
  pinOverlays.forEach((marker) => marker.remove())
  pinOverlays = []
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
    content.innerHTML = renderPixelIconSVG(pin.type === 'food' ? 'apple' : 'pin', { size: 16, color: '#fff' })
    content.title = pin.title
    content.style.animationDelay = `${(index % 6) * 0.3}s`
    const icon = L.divIcon({ html: content, className: 'map-pin-icon-wrap', iconSize: [30, 30], iconAnchor: [15, 30] })
    const marker = L.marker([pin.lat, pin.lng], { icon })
    marker.on('click', () => emit('pin-click', pin))
    marker.addTo(mapInstance)
    pinOverlays.push(marker)
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
    const marker = L.marker([region.lat, region.lng], { icon })
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
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(mapInstance)
  renderTourPins()
  renderRegionPins()
  renderRoute()
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
</script>

<template>
  <div class="tour-map-wrap">
    <div ref="mapEl" class="tour-map"></div>
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
</style>
