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

const openFestivalQuickAdd = (item) => {
  editingEvent.value = null
  festivalPrefill.value = {
    title: item.title,
    description: [item.addr1, item.tel].filter(Boolean).join(' · '),
    imageDataUrl: item.first_image || '',
    tags: ['축제']
  }
  initialDate.value = new Date().toISOString().slice(0, 10)
  modalOpen.value = true
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

    <div class="panel calendar-panel">
      <div class="festival-strip">
        <span class="festival-strip-label"><PixelIcon name="star" :size="14" color="var(--color-warning)" /> {{ t('calendar.referenceTitle') }}</span>
        <div class="festival-strip-scroll">
          <p v-if="festivalLoading" class="loading-state">{{ t('common.loading') }}</p>
          <button
            v-for="item in festivalItems"
            :key="item.id"
            type="button"
            class="festival-chip"
            :title="t('calendar.quickAddHint')"
            @click="openFestivalQuickAdd(item)"
          >
            <img v-if="item.first_image" :src="item.first_image" alt="" />
            <span v-else class="festival-chip-placeholder"><PixelIcon name="star" :size="18" color="var(--color-warning)" /></span>
            <span class="festival-chip-title">{{ item.title }}</span>
          </button>
          <span v-if="!festivalLoading && !festivalItems.length" class="empty-state">
            {{ t('calendar.referenceEmpty') }}
          </span>
        </div>
      </div>

      <FullCalendar :options="calendarOptions" />
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

.panel-title {
  margin: 0 0 12px;
  font-size: 1.05rem;
}

.festival-strip {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 14px;
  margin-bottom: 14px;
  border-bottom: 1px dashed var(--color-border);
}

.festival-strip-label {
  flex-shrink: 0;
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--color-text-muted);
}

.festival-strip-scroll {
  display: flex;
  align-items: center;
  gap: 10px;
  overflow-x: auto;
  padding: 4px 2px;
  scrollbar-width: thin;
}

.festival-chip {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px 14px 6px 6px;
  border: none;
  border-radius: 999px;
  background: var(--color-surface-alt);
  color: var(--color-text);
  cursor: pointer;
  font-family: inherit;
  font-size: 0.82rem;
  white-space: nowrap;
  transition: background-color 0.12s ease, transform 0.12s ease;
}

.festival-chip:hover {
  background: var(--color-primary-soft);
  transform: translateY(-1px);
}

.festival-chip img,
.festival-chip-placeholder {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-surface);
  font-size: 0.9rem;
}

.festival-chip-title {
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>
