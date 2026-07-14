<script setup>
import AppHeader from './components/common/AppHeader.vue'
import ChatWidget from './components/chatbot/ChatWidget.vue'
import ToastHost from './components/common/ToastHost.vue'
</script>

<template>
  <AppHeader />
  <main class="app-main">
    <router-view />
  </main>
  <ChatWidget />
  <ToastHost />
</template>
