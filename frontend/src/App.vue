<script setup>
import { onMounted } from 'vue'
import AppHeader from './components/common/AppHeader.vue'
import ChatWidget from './components/chatbot/ChatWidget.vue'
import ToastHost from './components/common/ToastHost.vue'
import { useNotificationStore } from './stores/notifications'
import { usePresenceStore } from './stores/presence'
import { useWeatherStore } from './stores/weather'

onMounted(() => {
  useNotificationStore().startPolling()
  usePresenceStore().connect()
  useWeatherStore().startPolling()
})
</script>

<template>
  <AppHeader />
  <main class="app-main">
    <router-view />
  </main>
  <ChatWidget />
  <ToastHost />
</template>
