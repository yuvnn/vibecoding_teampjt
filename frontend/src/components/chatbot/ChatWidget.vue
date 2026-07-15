<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useChatStore } from '../../stores/chat'
import PixelIcon from '../common/PixelIcon.vue'

const { t } = useI18n()
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
  <div class="chat-widget">
    <button class="chat-toggle" :title="t('chat.toggle')" @click="isOpen = !isOpen">
      <PixelIcon name="chat" :size="20" color="#fff" />
    </button>
    <Teleport to="body">
      <div v-if="isOpen" class="chat-panel chat-dock">
        <div class="chat-dock-header">
          <span class="chat-dock-title">
            <PixelIcon name="chat" :size="15" color="var(--color-primary-dark)" />
            {{ t('chat.toggle') }}
          </span>
          <button type="button" class="btn-icon" @click="isOpen = false">×</button>
        </div>
        <div class="chat-history">
          <p v-for="(message, index) in chatStore.messages" :key="index" :class="message.role">
            {{ message.content }}
          </p>
        </div>
        <form @submit.prevent="submit">
          <input v-model="draft" :placeholder="t('chat.placeholder')" />
          <button type="submit">{{ t('chat.send') }}</button>
        </form>
      </div>
    </Teleport>
  </div>
</template>

<style scoped>
.chat-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.chat-dock {
  position: fixed;
  left: 50%;
  right: auto;
  bottom: 92px;
  transform: translateX(-50%);
  z-index: 90;
  width: 100%;
  max-width: 500px;
  max-height: min(60vh, 460px);
  background: color-mix(in srgb, var(--color-surface) 94%, transparent);
  backdrop-filter: blur(10px);
}

.chat-dock-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-bottom: 2px solid var(--color-border);
  font-weight: 700;
  flex-shrink: 0;
}

.chat-dock-title {
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.chat-history {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.chat-history p {
  margin: 0;
  max-width: 78%;
  padding: 8px 12px;
  font-size: 0.85rem;
  line-height: 1.45;
  border: 2px solid var(--color-shadow);
  box-shadow: 2px 2px 0 var(--color-shadow);
  word-break: break-word;
  white-space: pre-wrap;
}

.chat-history .user {
  align-self: flex-end;
  background: var(--color-primary);
  color: #fff;
  border-radius: 12px 12px 2px 12px;
}

.chat-history .assistant {
  align-self: flex-start;
  background: var(--color-surface-alt);
  color: var(--color-text);
  border-radius: 12px 12px 12px 2px;
}

@media (max-width: 480px) {
  .chat-dock {
    width: calc(100vw - 24px);
    bottom: 84px;
  }
}
</style>
