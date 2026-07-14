<script setup>
import { useI18n } from 'vue-i18n'
import { useThemeStore } from '../../stores/theme'
import { toggleLocale } from '../../i18n'

const { t, locale } = useI18n()
const themeStore = useThemeStore()
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

    <div class="app-actions">
      <button type="button" class="btn btn-icon btn-ghost" :title="t('locale.toggle')" @click="toggleLocale">
        {{ locale === 'ko' ? 'EN' : '한글' }}
      </button>
      <button
        type="button"
        class="btn btn-icon btn-ghost"
        :title="themeStore.mode === 'dark' ? t('theme.toggleToLight') : t('theme.toggleToDark')"
        @click="themeStore.toggle"
      >
        {{ themeStore.mode === 'dark' ? '☀️' : '🌙' }}
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

.app-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.app-actions .btn-icon {
  font-size: 0.85rem;
  font-weight: 700;
  min-width: 40px;
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
}
</style>
