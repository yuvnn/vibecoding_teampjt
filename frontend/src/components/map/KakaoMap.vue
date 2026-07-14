<script setup>
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { hasKakaoKey, loadKakaoMaps } from '../../utils/kakao'

const props = defineProps({
  tourPins: { type: Array, default: () => [] },
  regionPins: { type: Array, default: () => [] },
  selectedIds: { type: Array, default: () => [] },
  center: { type: Object, default: () => ({ lat: 36.3504, lng: 127.3845 }) }
})
const emit = defineEmits(['pin-click', 'region-click'])

const { t } = useI18n()
const mapEl = ref(null)
const ready = ref(false)
const loadError = ref(false)

let mapInstance = null
let kakaoRef = null
let pinOverlays = []
let regionOverlays = []
let polyline = null

function clearPinOverlays() {
  pinOverlays.forEach((overlay) => overlay.setMap(null))
  pinOverlays = []
}

function clearRegionOverlays() {
  regionOverlays.forEach((overlay) => overlay.setMap(null))
  regionOverlays = []
}

function clearPolyline() {
  polyline?.setMap(null)
  polyline = null
}

function renderTourPins() {
  if (!kakaoRef) return
  clearPinOverlays()
  props.tourPins.forEach((pin, index) => {
    const selected = props.selectedIds.includes(pin.id)
    const content = document.createElement('div')
    content.className = `map-pin map-pin--${pin.type}${selected ? ' map-pin--selected' : ''}`
    content.textContent = pin.type === 'food' ? '🍽' : '📍'
    content.title = pin.title
    content.style.animationDelay = `${(index % 6) * 0.3}s`
    content.addEventListener('click', () => emit('pin-click', pin))
    const overlay = new kakaoRef.maps.CustomOverlay({
      position: new kakaoRef.maps.LatLng(pin.lat, pin.lng),
      content,
      yAnchor: 1
    })
    overlay.setMap(mapInstance)
    pinOverlays.push(overlay)
  })
}

function renderRegionPins() {
  if (!kakaoRef) return
  clearRegionOverlays()
  props.regionPins.forEach((region, index) => {
    const content = document.createElement('div')
    content.className = 'map-region-badge'
    content.innerHTML = `<strong>${region.label}</strong><span>${region.count}</span>`
    content.style.animationDelay = `${(index % 5) * 0.4}s`
    content.addEventListener('click', () => emit('region-click', region))
    const overlay = new kakaoRef.maps.CustomOverlay({
      position: new kakaoRef.maps.LatLng(region.lat, region.lng),
      content,
      yAnchor: 1.1
    })
    overlay.setMap(mapInstance)
    regionOverlays.push(overlay)
  })
}

function renderRoute() {
  if (!kakaoRef) return
  clearPolyline()
  const points = props.selectedIds
    .map((id) => props.tourPins.find((pin) => pin.id === id))
    .filter(Boolean)
  if (points.length < 2) return

  polyline = new kakaoRef.maps.Polyline({
    path: points.map((p) => new kakaoRef.maps.LatLng(p.lat, p.lng)),
    strokeWeight: 4,
    strokeColor: '#2563eb',
    strokeOpacity: 0.85,
    strokeStyle: 'solid'
  })
  polyline.setMap(mapInstance)

  const bounds = new kakaoRef.maps.LatLngBounds()
  points.forEach((p) => bounds.extend(new kakaoRef.maps.LatLng(p.lat, p.lng)))
  mapInstance.setBounds(bounds)
}

onMounted(async () => {
  if (!hasKakaoKey()) {
    loadError.value = true
    return
  }
  try {
    kakaoRef = await loadKakaoMaps()
    mapInstance = new kakaoRef.maps.Map(mapEl.value, {
      center: new kakaoRef.maps.LatLng(props.center.lat, props.center.lng),
      level: 9
    })
    ready.value = true
    renderTourPins()
    renderRegionPins()
    renderRoute()
  } catch {
    loadError.value = true
  }
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
})
</script>

<template>
  <div class="kakao-map-wrap">
    <div v-if="loadError" class="map-fallback">
      <p class="map-fallback-title">🗺️ {{ t('home.kakaoMissingTitle') }}</p>
      <p class="map-fallback-body">{{ t('home.kakaoMissingBody') }}</p>
    </div>
    <div v-else ref="mapEl" class="kakao-map"></div>
  </div>
</template>

<style scoped>
.kakao-map-wrap {
  width: 100%;
  height: 100%;
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.kakao-map {
  width: 100%;
  height: 100%;
  min-height: 440px;
}

.map-fallback {
  height: 100%;
  min-height: 440px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
  color: var(--color-text-muted);
  text-align: center;
  padding: 24px;
  background: radial-gradient(
    circle at center,
    color-mix(in srgb, var(--color-primary) 8%, transparent),
    transparent 70%
  );
}

.map-fallback-title {
  font-weight: 700;
  color: var(--color-text);
  margin: 0;
}

.map-fallback-body {
  font-size: 0.85rem;
  max-width: 360px;
  margin: 0;
}
</style>

<style>
/* Kakao overlay content is plain DOM created outside Vue's render tree, so
   these rules intentionally live in an unscoped block. */
.map-pin {
  width: 30px;
  height: 30px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  color: #fff;
  cursor: pointer;
  border: 2px solid #fff;
  box-shadow: 0 2px 6px rgba(15, 23, 42, 0.35);
  transition: transform 0.12s ease;
  animation: floaty 3.2s ease-in-out infinite;
}

.map-pin:hover {
  animation-play-state: paused;
  transform: scale(1.12);
}

.map-pin--tour {
  background: var(--color-primary, #2563eb);
}

.map-pin--food {
  background: #f97316;
}

.map-pin--selected {
  outline: 3px solid #facc15;
  animation-play-state: paused;
  transform: scale(1.15);
}

.map-region-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1px;
  padding: 6px 10px;
  border-radius: 12px;
  background: var(--color-primary-dark, #1d4ed8);
  color: #fff;
  font-size: 11px;
  cursor: pointer;
  white-space: nowrap;
  box-shadow: 0 4px 10px rgba(15, 23, 42, 0.3);
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
