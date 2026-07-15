<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { useThemeStore } from '../../stores/theme'
import { usePresenceStore } from '../../stores/presence'
import { useWeatherStore } from '../../stores/weather'
import { useNotificationStore } from '../../stores/notifications'
import { toggleLocale } from '../../i18n'
import PixelIcon from './PixelIcon.vue'

const { t, locale } = useI18n()
const router = useRouter()
const themeStore = useThemeStore()
const presenceStore = usePresenceStore()
const weatherStore = useWeatherStore()
const notificationStore = useNotificationStore()

const dateLabel = ref('')
const notifOpen = ref(false)
const notifRoot = ref(null)

const formatDate = ({ year, month, day }) => {
  const asDate = new Date(year, month - 1, day)
  return new Intl.DateTimeFormat(locale.value === 'ko' ? 'ko-KR' : 'en-US', {
    month: 'long',
    day: 'numeric',
    weekday: 'short'
  }).format(asDate)
}

const toggleNotif = () => {
  notifOpen.value = !notifOpen.value
  if (notifOpen.value) notificationStore.markAllRead()
}

const openNotifItem = (item) => {
  notifOpen.value = false
  router.push(`/board/${item.id}`)
}

const onDocumentClick = (event) => {
  if (notifOpen.value && notifRoot.value && !notifRoot.value.contains(event.target)) {
    notifOpen.value = false
  }
}

onMounted(async () => {
  document.addEventListener('click', onDocumentClick)
  try {
    const res = await fetch('https://www.timeapi.io/api/time/current/zone?timeZone=Asia/Seoul')
    if (!res.ok) throw new Error('time api failed')
    const data = await res.json()
    dateLabel.value = formatDate(data)
  } catch {
    dateLabel.value = ''
  }
})

onBeforeUnmount(() => {
  document.removeEventListener('click', onDocumentClick)
})
</script>

<template>
  <header class="app-header">
    <router-link to="/" class="logo">
      <span class="logo-mark">L</span>
      {{ t('common.appName') }}
    </router-link>

    <nav class="app-nav">
      <router-link to="/board" class="nav-link">{{ t('nav.board') }}</router-link>
      <router-link to="/calendar" class="nav-link">{{ t('nav.calendar') }}</router-link>
    </nav>

    <div class="header-info">
      <span class="header-presence" :title="t('common.presenceTitle')">
        <span class="presence-dot"></span>
        {{ t('common.presenceCount', { count: presenceStore.count }) }}
      </span>
      <span v-if="dateLabel" class="header-date">{{ dateLabel }}</span>
      <span v-if="weatherStore.temperature !== null" class="header-weather">
        <PixelIcon :name="weatherStore.icon" :size="13" color="var(--color-primary-dark)" />
        {{ weatherStore.temperature }}&deg;C
      </span>
      <span class="header-region"><PixelIcon name="pin" :size="12" /> {{ t('common.regionLabel') }}</span>
    </div>

    <div class="app-actions">
      <div ref="notifRoot" class="notif-wrap">
        <button
          type="button"
          class="btn btn-icon btn-ghost"
          :title="t('common.notifications')"
          @click.stop="toggleNotif"
        >
          <PixelIcon name="bell" :size="16" />
          <span v-if="notificationStore.unreadCount" class="notif-badge">{{ notificationStore.unreadCount }}</span>
        </button>
        <div v-if="notifOpen" class="notif-dropdown panel">
          <p class="notif-title">{{ t('common.notifications') }}</p>
          <ul v-if="notificationStore.items.length" class="notif-list">
            <li v-for="item in notificationStore.items" :key="item.id">
              <button type="button" class="notif-item" @click="openNotifItem(item)">
                {{ item.title }}
              </button>
            </li>
          </ul>
          <p v-else class="notif-empty">{{ t('common.notificationsEmpty') }}</p>
        </div>
      </div>

      <button type="button" class="btn btn-icon btn-ghost" :title="t('locale.toggle')" @click="toggleLocale">
        {{ locale === 'ko' ? 'EN' : '한글' }}
      </button>
      <button
        type="button"
        class="btn btn-icon btn-ghost"
        :title="themeStore.mode === 'dark' ? t('theme.toggleToLight') : t('theme.toggleToDark')"
        @click="themeStore.toggle"
      >
        <PixelIcon :name="themeStore.mode === 'dark' ? 'sun' : 'moon'" :size="16" />
      </button>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 50;
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 0 20px;
  height: var(--header-height);
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  backdrop-filter: saturate(180%) blur(8px);
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 800;
  font-size: 1.15rem;
  color: var(--color-primary-dark);
  white-space: nowrap;
}

.logo-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border-radius: 9px;
  background: linear-gradient(135deg, var(--color-primary), var(--color-primary-dark));
  color: #fff;
  font-size: 0.95rem;
}

.app-nav {
  display: flex;
  gap: 4px;
  flex: 1;
}

.nav-link {
  padding: 8px 14px;
  border-radius: var(--radius-sm);
  font-weight: 600;
  font-size: 0.92rem;
  color: var(--color-text-muted);
}

.nav-link:hover {
  background: var(--color-surface-alt);
  color: var(--color-text);
}

.nav-link.router-link-active {
  color: var(--color-primary-dark);
  background: var(--color-primary-soft);
}

.header-info {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-shrink: 0;
}

.header-date {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-text-muted);
  white-space: nowrap;
}

.header-weather {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--color-text-muted);
  white-space: nowrap;
}

.header-presence {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--color-text-muted);
  white-space: nowrap;
}

.presence-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--color-success);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--color-success) 30%, transparent);
  animation: presence-pulse 1.8s ease-in-out infinite;
}

@keyframes presence-pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
}

.header-region {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 700;
  color: var(--color-primary-dark);
  background: var(--color-primary-soft);
  border: 1px solid var(--color-primary-light);
  white-space: nowrap;
}

.app-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.app-actions .btn-icon {
  font-size: 0.85rem;
  font-weight: 700;
  min-width: 40px;
  position: relative;
}

.notif-wrap {
  position: relative;
}

.notif-badge {
  position: absolute;
  top: -2px;
  right: -2px;
  min-width: 16px;
  height: 16px;
  padding: 0 3px;
  border-radius: 999px;
  background: var(--color-danger);
  color: #fff;
  font-size: 0.62rem;
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--color-surface);
}

.notif-dropdown {
  position: absolute;
  top: calc(100% + 10px);
  right: 0;
  width: 280px;
  max-height: 360px;
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  z-index: 55;
}

.notif-title {
  margin: 0;
  font-size: 0.85rem;
  font-weight: 700;
}

.notif-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
  overflow-y: auto;
}

.notif-item {
  width: 100%;
  text-align: left;
  padding: 8px 10px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface-alt);
  color: var(--color-text);
  font-size: 0.82rem;
  cursor: pointer;
}

.notif-item:hover {
  border-color: var(--color-primary);
  color: var(--color-primary-dark);
}

.notif-empty {
  margin: 0;
  font-size: 0.82rem;
  color: var(--color-text-muted);
}

@media (max-width: 640px) {
  .app-header {
    padding: 0 12px;
    gap: 10px;
  }

  .logo span:not(.logo-mark) {
    display: none;
  }

  .nav-link {
    padding: 8px 10px;
    font-size: 0.85rem;
  }

  .header-date,
  .header-weather {
    display: none;
  }

  .notif-dropdown {
    width: 240px;
  }
}
</style>
