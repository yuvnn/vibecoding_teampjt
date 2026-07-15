<script setup>
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import FullCalendar from '@fullcalendar/vue3'
import dayGridPlugin from '@fullcalendar/daygrid'
import listPlugin from '@fullcalendar/list'
import interactionPlugin from '@fullcalendar/interaction'
import koLocale from '@fullcalendar/core/locales/ko'
import { fetchTourItems } from '../api/tour'
import { useCalendarEventsStore } from '../stores/calendarEvents'
import EventFormModal from '../components/calendar/EventFormModal.vue'
import PixelIcon from '../components/common/PixelIcon.vue'
import { renderPixelIconSVG } from '../utils/pixelIcons'

const FESTIVAL_CONTENT_TYPE_ID = 15

const { t, locale } = useI18n()
const calendarStore = useCalendarEventsStore()

const modalOpen = ref(false)
const editingEvent = ref(null)
const festivalPrefill = ref(null)
const initialDate = ref('')

const festivalItems = ref([])
const festivalLoading = ref(true)
const selectedFestival = ref(null)
const selectedFestivalStartDate = ref('')
const selectedFestivalEndDate = ref('')

const normalizeFestivalDate = (value) => {
  if (!value) return ''
  const text = String(value).trim()
  if (!text) return ''
  if (/^\d{8}$/.test(text)) {
    return `${text.slice(0, 4)}-${text.slice(4, 6)}-${text.slice(6, 8)}`
  }
  const date = new Date(text)
  if (Number.isNaN(date.getTime())) return ''
  return date.toISOString().slice(0, 10)
}

const addOneDay = (dateStr) => {
  const date = new Date(dateStr)
  date.setDate(date.getDate() + 1)
  return date.toISOString().slice(0, 10)
}

const fcEvents = computed(() =>
  calendarStore.events.map((event) => {
    const isFestival = event.tags?.includes('축제') ?? false
    return {
      id: event.id,
      title: event.title,
      start: event.start,
      end: addOneDay(event.end || event.start),
      allDay: true,
      backgroundColor: isFestival ? 'var(--color-warning)' : 'var(--color-primary)',
      borderColor: isFestival ? 'var(--color-warning)' : 'var(--color-primary-dark)',
      extendedProps: { isFestival }
    }
  })
)

const renderEventContent = (arg) => {
  const wrap = document.createElement('span')
  wrap.className = 'fc-event-pixel-inner'
  if (arg.event.extendedProps?.isFestival) {
    const icon = document.createElement('span')
    icon.className = 'fc-event-pixel-icon'
    icon.innerHTML = renderPixelIconSVG('star', { size: 11, color: '#fff' })
    wrap.appendChild(icon)
  }
  const title = document.createElement('span')
  title.textContent = arg.event.title
  wrap.appendChild(title)
  return { domNodes: [wrap] }
}

const calendarOptions = computed(() => ({
  plugins: [dayGridPlugin, listPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  locale: locale.value === 'ko' ? koLocale : 'en',
  headerToolbar: { left: 'prev,next today', center: 'title', right: 'dayGridMonth,listMonth' },
  height: 'auto',
  events: fcEvents.value,
  eventContent: renderEventContent,
  dateClick: (info) => {
    editingEvent.value = null
    festivalPrefill.value = null
    initialDate.value = info.dateStr
    modalOpen.value = true
  },
  eventClick: (info) => {
    editingEvent.value = calendarStore.events.find((event) => event.id === info.event.id) ?? null
    festivalPrefill.value = null
    initialDate.value = ''
    modalOpen.value = true
  }
}))

const openNewEventModal = () => {
  editingEvent.value = null
  festivalPrefill.value = null
  initialDate.value = ''
  modalOpen.value = true
}

const closeModal = () => {
  modalOpen.value = false
}

const handleSubmit = (payload) => {
  if (payload.id) {
    calendarStore.update(payload.id, payload)
  } else {
    calendarStore.create(payload)
  }
  closeModal()
}

const handleDelete = (id) => {
  if (window.confirm(t('calendar.deleteConfirm'))) {
    calendarStore.remove(id)
    closeModal()
  }
}

const openFestivalModal = (item) => {
  selectedFestival.value = item
  selectedFestivalStartDate.value = normalizeFestivalDate(item.eventstartdate || item.start_date)
  selectedFestivalEndDate.value = normalizeFestivalDate(item.eventenddate || item.end_date || item.eventstartdate || item.start_date)
}

const closeFestivalModal = () => {
  selectedFestival.value = null
  selectedFestivalStartDate.value = ''
  selectedFestivalEndDate.value = ''
}

const addFestivalToCalendar = () => {
  if (!selectedFestival.value) return

  const item = selectedFestival.value
  const start = normalizeFestivalDate(selectedFestivalStartDate.value) || normalizeFestivalDate(item.eventstartdate || item.start_date)
  const end = normalizeFestivalDate(selectedFestivalEndDate.value) || start || normalizeFestivalDate(item.eventenddate || item.end_date || item.eventstartdate || item.start_date)
  const payload = {
    id: `festival-${item.contentid || item.id}`,
    title: item.title,
    start: start || new Date().toISOString().slice(0, 10),
    end: end || start || new Date().toISOString().slice(0, 10),
    description: [item.addr1, item.tel].filter(Boolean).join(' · '),
    imageDataUrl: item.first_image || '',
    tags: ['축제']
  }

  const existing = calendarStore.events.find((event) => event.id === payload.id)
  if (!existing) {
    calendarStore.create(payload)
  }

  closeFestivalModal()
}

onMounted(async () => {
  try {
    const { data } = await fetchTourItems({ content_type_id: FESTIVAL_CONTENT_TYPE_ID })
    festivalItems.value = data.slice(0, 9)
  } catch {
    festivalItems.value = []
  } finally {
    festivalLoading.value = false
  }
})
</script>

<template>
  <section class="calendar-view">
    <div class="page-header">
      <div>
        <h1 class="page-title">{{ t('calendar.title') }}</h1>
        <p class="page-subtitle">{{ t('calendar.subtitle') }}</p>
      </div>
      <button type="button" class="btn btn-primary" @click="openNewEventModal">
        {{ t('calendar.addEvent') }}
      </button>
    </div>

    <div class="calendar-layout">
      <div class="panel calendar-panel">
        <FullCalendar :options="calendarOptions" />
      </div>

      <aside class="panel festival-panel">
        <div class="festival-panel__header">
          <h3>{{ t('calendar.referenceTitle') }}</h3>
          <span class="festival-panel__count">{{ festivalItems.length }}</span>
        </div>

        <p v-if="festivalLoading" class="loading-state">{{ t('common.loading') }}</p>
        <div v-else-if="festivalItems.length" class="festival-list">
          <button
            v-for="item in festivalItems"
            :key="item.id"
            type="button"
            class="festival-card"
            :title="t('calendar.quickAddHint')"
            @click="openFestivalModal(item)"
          >
            <img v-if="item.first_image" :src="item.first_image" alt="" />
            <span v-else class="festival-card-placeholder"><PixelIcon name="star" :size="18" color="var(--color-warning)" /></span>
            <div class="festival-card__body">
              <strong>{{ item.title }}</strong>
              <span>{{ item.addr1 || t('calendar.referenceEmpty') }}</span>
            </div>
          </button>
        </div>
        <p v-else class="empty-state">{{ t('calendar.referenceEmpty') }}</p>
      </aside>
    </div>

    <div v-if="selectedFestival" class="festival-modal-backdrop" @click.self="closeFestivalModal">
      <div class="festival-modal">
        <div class="festival-modal__header">
          <h3>{{ selectedFestival.title }}</h3>
          <button type="button" class="btn btn-ghost btn-sm" @click="closeFestivalModal">닫기</button>
        </div>
        <div class="festival-modal__body">
          <img v-if="selectedFestival.first_image" :src="selectedFestival.first_image" alt="" />
          <div class="festival-modal__info">
            <p v-if="selectedFestival.addr1"><strong>장소</strong> {{ selectedFestival.addr1 }}</p>
            <p v-if="selectedFestival.tel"><strong>연락처</strong> {{ selectedFestival.tel }}</p>
          </div>
          <div class="festival-modal__date-fields">
            <label>
              <span>일정 시작일</span>
              <input v-model="selectedFestivalStartDate" type="date" />
            </label>
            <label>
              <span>일정 종료일</span>
              <input v-model="selectedFestivalEndDate" type="date" />
            </label>
          </div>
        </div>
        <div class="festival-modal__actions">
          <button type="button" class="btn btn-primary" @click="addFestivalToCalendar">일정 추가</button>
        </div>
      </div>
    </div>

    <EventFormModal
      :open="modalOpen"
      :event="editingEvent"
      :prefill="festivalPrefill"
      :initial-date="initialDate"
      @submit="handleSubmit"
      @delete="handleDelete"
      @close="closeModal"
    />
  </section>
</template>

<style scoped>
.calendar-view {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.calendar-panel :deep(.fc) {
  --fc-border-color: var(--color-border);
  --fc-page-bg-color: transparent;
  --fc-neutral-bg-color: var(--color-surface-alt);
  --fc-list-event-hover-bg-color: var(--color-surface-alt);
  --fc-today-bg-color: color-mix(in srgb, var(--color-primary) 12%, transparent);
  color: var(--color-text);
}

.calendar-panel :deep(.fc-button) {
  background: var(--color-surface-alt);
  border: 1px solid var(--color-border);
  color: var(--color-text);
  text-transform: capitalize;
  box-shadow: none;
}

.calendar-panel :deep(.fc-button:hover) {
  background: var(--color-border);
}

.calendar-panel :deep(.fc-button-active) {
  background: var(--color-primary) !important;
  border-color: var(--color-primary) !important;
  color: #fff !important;
}

.calendar-panel :deep(.fc-event-pixel-inner) {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.calendar-panel :deep(.fc-event-pixel-icon) {
  display: inline-flex;
  flex-shrink: 0;
}

.calendar-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) minmax(280px, 0.8fr);
  gap: 16px;
  align-items: start;
}

.calendar-panel {
  min-width: 0;
}

.festival-panel {
  display: flex;
  flex-direction: column;
  gap: 10px;
  min-height: 420px;
}

.festival-panel__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}

.festival-panel__header h3 {
  margin: 0;
  font-size: 0.95rem;
}

.festival-panel__count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 28px;
  padding: 0 8px;
  border-radius: 999px;
  background: var(--color-primary-soft);
  color: var(--color-primary-dark);
  font-size: 0.78rem;
  font-weight: 700;
}

.festival-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  overflow-y: auto;
  padding-right: 2px;
}

.festival-card {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  width: 100%;
  padding: 10px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface-alt);
  color: var(--color-text);
  cursor: pointer;
  text-align: left;
  font-family: inherit;
}

.festival-card:hover {
  background: var(--color-primary-soft);
}

.festival-card img,
.festival-card-placeholder {
  width: 44px;
  height: 44px;
  border-radius: var(--radius-sm);
  object-fit: cover;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  background: var(--color-surface);
}

.festival-card__body {
  display: flex;
  flex-direction: column;
  gap: 3px;
  min-width: 0;
}

.festival-card__body strong {
  font-size: 0.84rem;
  line-height: 1.35;
}

.festival-card__body span {
  font-size: 0.74rem;
  color: var(--color-text-muted);
  line-height: 1.4;
}

.festival-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(15, 23, 42, 0.45);
}

.festival-modal {
  width: min(520px, 100%);
  max-height: min(80vh, 760px);
  overflow: auto;
  padding: 18px;
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-lg);
}

.festival-modal__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 12px;
}

.festival-modal__header h3 {
  margin: 0;
  font-size: 1rem;
}

.festival-modal__body {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.festival-modal__body img {
  width: 100%;
  max-height: 220px;
  object-fit: cover;
  border-radius: var(--radius-md);
}

.festival-modal__info {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.festival-modal__info p {
  margin: 0;
  font-size: 0.9rem;
  color: var(--color-text);
}

.festival-modal__date-fields {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.festival-modal__date-fields label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 0.85rem;
  color: var(--color-text);
}

.festival-modal__date-fields input {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface-alt);
  color: var(--color-text);
}

.festival-modal__actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 14px;
}
</style>
