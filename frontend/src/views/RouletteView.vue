<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { fetchRandomTourItems } from '../api/tour'
import { useRegionStore } from '../stores/region'
import { useMapFocusStore } from '../stores/mapFocus'
import PixelIcon from '../components/common/PixelIcon.vue'

const TOUR_CONTENT_TYPE_ID = 12
const CANDIDATE_COUNT = 20
const SPIN_DURATION_MS = 4200
const RIVET_COUNT = 24
// Cycled purely for visual variety between wedges — the data has no
// per-item category, so this just gives each slice a distinct glyph.
const WEDGE_ICONS = ['pin', 'star', 'culture', 'sport', 'shopping', 'stay', 'course', 'heart']
// A varied, saturated palette (rather than near-identical wood tones) so the
// wheel reads as a colorful prize wheel set inside a wooden case.
const WEDGE_PALETTE = [
  '#4f7c4a',
  '#8b5e34',
  '#c9a227',
  '#c1652f',
  '#a13d3d',
  '#2f7f7a',
  '#6b4a8b',
  '#7c8b3a',
  '#d8c398',
  '#5c3d22'
]

const { t } = useI18n()
const router = useRouter()
const regionStore = useRegionStore()
const mapFocusStore = useMapFocusStore()

const items = ref([])
const loading = ref(true)
const spinning = ref(false)
const rotation = ref(0)
const winner = ref(null)
const showResult = ref(false)
const confettiPieces = ref([])
let spinTimer = null

const anglePerSlice = computed(() => (items.value.length ? 360 / items.value.length : 0))

const wedgeColor = (index) => WEDGE_PALETTE[index % WEDGE_PALETTE.length]

const wheelBackground = computed(() => {
  const n = items.value.length
  if (!n) return 'var(--color-surface-alt)'
  const step = 100 / n
  // Dark wood-groove seam between every wedge, drawn from the same
  // --color-shadow used for pixel borders elsewhere, so it reads as a
  // carved divider rather than a flat pie-chart boundary.
  const seam = Math.min(0.5, step * 0.18)
  const stops = items.value.map((_, i) => {
    const start = i * step
    const end = (i + 1) * step
    const color = wedgeColor(i)
    return `var(--color-shadow) ${start.toFixed(3)}% ${(start + seam).toFixed(3)}%, ${color} ${(start + seam).toFixed(3)}% ${(end - seam).toFixed(3)}%`
  })
  return `conic-gradient(${stops.join(', ')})`
})

const rivetStyle = (i) => ({
  '--rangle': `${(360 / RIVET_COUNT) * i}deg`
})

const iconForIndex = (index) => WEDGE_ICONS[index % WEDGE_ICONS.length]

const wheelStyle = computed(() => ({
  background: wheelBackground.value,
  transform: `translate(-50%, -50%) rotate(${rotation.value}deg)`
}))

const labelStyle = (index) => {
  const mid = index * anglePerSlice.value + anglePerSlice.value / 2
  // Labels on the wheel's left half would render upside down/backwards at
  // rest (rotate(90deg..270deg) flips horizontal text) — flip just the
  // inner text span back upright without moving its position on the spoke.
  const flipped = mid > 90 && mid < 270
  return {
    '--angle': `${mid}deg`,
    '--text-flip': flipped ? '180deg' : '0deg'
  }
}

async function loadCandidates() {
  loading.value = true
  winner.value = null
  showResult.value = false
  rotation.value = 0
  try {
    const { data } = await fetchRandomTourItems({
      content_type_id: TOUR_CONTENT_TYPE_ID,
      region: regionStore.selectedRegion,
      count: CANDIDATE_COUNT
    })
    items.value = data
  } catch {
    items.value = []
  } finally {
    loading.value = false
  }
}

function launchConfetti() {
  confettiPieces.value = Array.from({ length: 40 }, (_, i) => ({
    id: i,
    left: Math.random() * 100,
    hue: Math.round(Math.random() * 360),
    delay: Math.random() * 0.3,
    duration: 1.8 + Math.random() * 1.2,
    rotate: Math.round(Math.random() * 360)
  }))
  window.setTimeout(() => {
    confettiPieces.value = []
  }, 3200)
}

function spin() {
  if (spinning.value || !items.value.length) return
  spinning.value = true
  showResult.value = false
  winner.value = null

  const n = items.value.length
  const winnerIndex = Math.floor(Math.random() * n)
  const targetCenterAngle = winnerIndex * anglePerSlice.value + anglePerSlice.value / 2
  const desired = ((360 - targetCenterAngle) % 360 + 360) % 360
  const current = ((rotation.value % 360) + 360) % 360
  const delta = ((desired - current) % 360 + 360) % 360
  const extraSpins = 6 + Math.floor(Math.random() * 3)

  rotation.value += 360 * extraSpins + delta

  clearTimeout(spinTimer)
  spinTimer = window.setTimeout(() => {
    spinning.value = false
    winner.value = items.value[winnerIndex]
    showResult.value = true
    launchConfetti()
  }, SPIN_DURATION_MS)
}

function closeResult() {
  showResult.value = false
}

function viewOnMap(item) {
  if (!item) return
  mapFocusStore.request({
    id: item.content_id,
    lat: item.map_y,
    lng: item.map_x,
    title: item.title,
    addr: item.addr1,
    image: item.first_image,
    type: 'tour',
    icon: 'pin'
  })
  router.push('/')
}

onMounted(loadCandidates)
watch(() => regionStore.selectedRegion, loadCandidates)
</script>

<template>
  <section class="roulette-view">
    <div class="page-header">
      <div>
        <h1 class="page-title">{{ t('roulette.title') }}</h1>
        <p class="page-subtitle">{{ t('roulette.subtitle', { region: regionStore.selectedLabel }) }}</p>
      </div>
      <button type="button" class="btn btn-outline" :disabled="loading || spinning" @click="loadCandidates">
        {{ t('roulette.reroll') }}
      </button>
    </div>

    <p v-if="loading" class="loading-state">{{ t('roulette.loading') }}</p>
    <p v-else-if="!items.length" class="empty-state">{{ t('roulette.empty') }}</p>

    <div v-else class="roulette-center">
      <div class="roulette-stage">
        <div class="roulette-rim">
          <span
            v-for="i in RIVET_COUNT"
            :key="'rivet-' + i"
            class="rivet"
            :style="rivetStyle(i - 1)"
          ></span>
        </div>

        <div class="roulette-pointer-wrap">
          <span class="roulette-pointer-loop"></span>
          <span class="roulette-pointer-gem"></span>
        </div>

        <div class="roulette-wheel" :style="wheelStyle">
          <div
            v-for="(item, index) in items"
            :key="item.content_id"
            class="wheel-label"
            :style="labelStyle(index)"
          >
            <span class="wheel-label-text">
              <PixelIcon :name="iconForIndex(index)" :size="12" color="#fffdf5" />
              <span class="wheel-label-index">{{ index + 1 }}</span>
              <span class="wheel-label-title">{{ item.title }}</span>
            </span>
          </div>
        </div>

        <button type="button" class="roulette-hub" :disabled="spinning" @click="spin">
          {{ spinning ? t('roulette.spinning') : t('roulette.spin') }}
        </button>
      </div>

      <aside class="panel candidate-panel">
        <h3 class="candidate-panel__title">{{ t('roulette.candidateTitle', { count: items.length }) }}</h3>
        <ul class="candidate-list">
          <li
            v-for="(item, index) in items"
            :key="item.content_id"
            :class="{ 'candidate-item--winner': winner?.content_id === item.content_id }"
          >
            <PixelIcon :name="iconForIndex(index)" :size="14" color="var(--color-primary-dark)" />
            <span class="candidate-index">{{ index + 1 }}</span>
            <span class="candidate-title">{{ item.title }}</span>
          </li>
        </ul>
      </aside>
    </div>

    <div v-if="confettiPieces.length" class="confetti-layer">
      <span
        v-for="piece in confettiPieces"
        :key="piece.id"
        class="confetti-piece"
        :style="{
          left: `${piece.left}%`,
          backgroundColor: `hsl(${piece.hue}, 85%, 60%)`,
          animationDelay: `${piece.delay}s`,
          animationDuration: `${piece.duration}s`,
          '--confetti-rotate': `${piece.rotate}deg`
        }"
      ></span>
    </div>

    <div v-if="showResult && winner" class="result-modal-backdrop" @click.self="closeResult">
      <div class="result-modal">
        <h2 class="result-title">{{ t('roulette.resultTitle') }}</h2>
        <p class="result-hint">{{ t('roulette.resultHint') }}</p>
        <img v-if="winner.first_image" :src="winner.first_image" alt="" class="result-image" />
        <h3 class="result-name">{{ winner.title }}</h3>
        <p v-if="winner.addr1" class="result-addr">{{ winner.addr1 }}</p>
        <p v-if="winner.tel" class="result-tel">{{ winner.tel }}</p>
        <div class="result-actions">
          <button type="button" class="btn btn-ghost" @click="spin">{{ t('roulette.spinAgain') }}</button>
          <button type="button" class="btn btn-primary" @click="viewOnMap(winner)">{{ t('roulette.viewOnMap') }}</button>
        </div>
        <button type="button" class="btn btn-ghost btn-sm result-close" @click="closeResult">{{ t('roulette.close') }}</button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.roulette-view {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.roulette-center {
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 56px;
  min-height: min(70vh, 640px);
}

.candidate-panel {
  width: 320px;
  max-height: 460px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.candidate-panel__title {
  margin: 0;
  font-size: 0.95rem;
}

.candidate-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  overflow-y: auto;
}

.candidate-list li {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 10px;
  border-radius: var(--radius-sm);
  background: var(--color-surface-alt);
  font-size: 0.82rem;
}

.candidate-list li :deep(.pixel-icon) {
  flex-shrink: 0;
}

.candidate-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--color-primary-soft);
  color: var(--color-primary-dark);
  font-weight: 700;
  font-size: 0.72rem;
  flex-shrink: 0;
}

.candidate-title {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.candidate-item--winner {
  background: var(--color-primary-soft);
  outline: 2px solid var(--color-primary);
}

.candidate-item--winner .candidate-index {
  background: var(--color-primary);
  color: #fff;
}

.roulette-stage {
  position: relative;
  width: 460px;
  height: 460px;
}

/* Static wooden case ring the colored disc spins inside — flat fill color
   plus a solid pixel-style outline, no gradients. Rivets sit on this
   non-rotating layer, like screws on a real wheel-of-fortune cabinet. */
.roulette-rim {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  background: #8b5e34;
  border: 6px solid var(--color-shadow);
  z-index: 1;
}

.rivet {
  --rivet-radius: 212px;
  position: absolute;
  top: 50%;
  left: 50%;
  width: 11px;
  height: 11px;
  margin: -5.5px 0 0 -5.5px;
  border-radius: 50%;
  background: #d8b689;
  border: 2px solid var(--color-shadow);
  transform: rotate(var(--rangle)) translateY(calc(-1 * var(--rivet-radius)));
}

.roulette-wheel {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  border: 6px solid var(--color-shadow);
  transition: transform 4.2s cubic-bezier(0.12, 0.67, 0.15, 1);
  z-index: 2;
}

.wheel-label {
  --wheel-radius: 200px;
  --hub-gap: 68px;
  position: absolute;
  top: 50%;
  left: 50%;
  box-sizing: border-box;
  width: calc(var(--wheel-radius) - 16px);
  height: 20px;
  margin-top: -10px;
  padding-left: var(--hub-gap);
  display: flex;
  align-items: center;
  transform-origin: 0% 50%;
  transform: rotate(var(--angle));
  pointer-events: none;
}

.wheel-label-text {
  display: flex;
  align-items: center;
  gap: 4px;
  max-width: 100%;
  min-width: 0;
  transform: rotate(var(--text-flip));
  color: #fffdf5;
  text-shadow: 1px 1px 0 var(--color-shadow), -1px -1px 0 var(--color-shadow), 1px -1px 0 var(--color-shadow),
    -1px 1px 0 var(--color-shadow);
}

.wheel-label-text :deep(.pixel-icon) {
  flex-shrink: 0;
}

.wheel-label-index {
  flex-shrink: 0;
  font-weight: 800;
  font-size: 0.74rem;
}

.wheel-label-title {
  min-width: 0;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  font-weight: 800;
  font-size: 0.74rem;
}

/* Teardrop "gem" pointer with a small metal loop above it, like the pin
   perched on top of a real prize wheel's cabinet. */
.roulette-pointer-wrap {
  position: absolute;
  top: -14px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 3;
  filter: drop-shadow(0 2px 1px rgba(0, 0, 0, 0.35));
}

.roulette-pointer-loop {
  width: 11px;
  height: 11px;
  margin-bottom: -4px;
  border-radius: 50%;
  border: 3px solid var(--color-shadow);
  background: transparent;
}

.roulette-pointer-gem {
  width: 24px;
  height: 24px;
  border: 3px solid var(--color-shadow);
  border-radius: 50% 50% 50% 0;
  transform: rotate(-45deg);
  background: var(--color-warning);
}

.roulette-hub {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 104px;
  height: 104px;
  border-radius: 50%;
  border: 4px solid var(--color-shadow);
  background: #a9773f;
  color: #fffdf5;
  font-weight: 800;
  font-size: 0.78rem;
  line-height: 1.15;
  cursor: pointer;
  z-index: 4;
  text-shadow: 1px 1px 0 rgba(0, 0, 0, 0.4);
}

.roulette-hub:hover:not(:disabled) {
  background: #b98a52;
}

.roulette-hub:disabled {
  cursor: not-allowed;
  opacity: 0.85;
}

.confetti-layer {
  position: fixed;
  inset: 0;
  pointer-events: none;
  overflow: hidden;
  z-index: 1200;
}

.confetti-piece {
  position: absolute;
  top: -10px;
  width: 8px;
  height: 8px;
  animation-name: confetti-fall;
  animation-timing-function: ease-in;
  animation-fill-mode: forwards;
}

@keyframes confetti-fall {
  0% {
    transform: translateY(0) rotate(0deg);
    opacity: 1;
  }
  100% {
    transform: translateY(105vh) rotate(var(--confetti-rotate));
    opacity: 0.2;
  }
}

.result-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(15, 23, 42, 0.5);
}

.result-modal {
  width: min(420px, 100%);
  max-height: min(85vh, 640px);
  overflow: auto;
  padding: 24px;
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  border: 2px solid var(--color-border);
  box-shadow: var(--shadow-lg);
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.result-title {
  margin: 0;
  font-size: 1.3rem;
}

.result-hint {
  margin: 0 0 4px;
  color: var(--color-text-muted);
  font-size: 0.88rem;
}

.result-image {
  width: 100%;
  height: 180px;
  object-fit: cover;
  border-radius: var(--radius-md);
  margin-bottom: 4px;
}

.result-name {
  margin: 4px 0 0;
  font-size: 1.1rem;
}

.result-addr,
.result-tel {
  margin: 0;
  font-size: 0.88rem;
  color: var(--color-text-muted);
}

.result-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-top: 14px;
}

.result-close {
  margin: 8px auto 0;
}

@media (max-width: 860px) {
  .roulette-center {
    flex-direction: column;
    min-height: 0;
  }

  .candidate-panel {
    width: min(320px, 100%);
    max-height: 240px;
  }

  .roulette-stage {
    width: 320px;
    height: 320px;
  }

  .rivet {
    --rivet-radius: 147px;
    width: 8px;
    height: 8px;
    margin: -4px 0 0 -4px;
  }

  .roulette-wheel {
    width: 276px;
    height: 276px;
  }

  .wheel-label {
    --wheel-radius: 138px;
    --hub-gap: 48px;
  }

  .wheel-label-index,
  .wheel-label-title {
    font-size: 0.6rem;
  }

  .roulette-hub {
    width: 74px;
    height: 74px;
    font-size: 0.62rem;
  }

  .roulette-pointer-gem {
    width: 18px;
    height: 18px;
  }
}
</style>
