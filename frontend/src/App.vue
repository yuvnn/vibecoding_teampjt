<script setup>
import AppHeader from './components/common/AppHeader.vue'
import ChatWidget from './components/chatbot/ChatWidget.vue'
</script>

<template>
  <AppHeader />
  <main class="app-main">
    <router-view />
  </main>
  <ChatWidget />
</template>
