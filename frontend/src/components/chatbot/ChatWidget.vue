<script setup>
import { ref } from 'vue'
import { useChatStore } from '../../stores/chat'

const chatStore = useChatStore()
const isOpen = ref(false)
const draft = ref('')

const submit = async () => {
  if (!draft.value.trim()) return
  const text = draft.value
  draft.value = ''
  await chatStore.sendMessage(text)
}
</script>

<template>
  <div class="chat-widget" :class="{ open: isOpen }">
    <button class="chat-toggle" @click="isOpen = !isOpen">챗봇</button>
    <div v-if="isOpen" class="chat-panel">
      <div class="chat-history">
        <p v-for="(message, index) in chatStore.messages" :key="index" :class="message.role">
          {{ message.content }}
        </p>
      </div>
      <form @submit.prevent="submit">
        <input v-model="draft" placeholder="메시지를 입력하세요" />
        <button type="submit">전송</button>
      </form>
    </div>
  </div>
</template>
