<script setup>
import { nextTick, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter, useRoute } from 'vue-router'
import { useChatStore } from '../../stores/chat'
import { useMapFocusStore } from '../../stores/mapFocus'
import PixelIcon from '../common/PixelIcon.vue'

const { t } = useI18n()
const router = useRouter()
const route = useRoute()
const chatStore = useChatStore()
const mapFocusStore = useMapFocusStore()
const isOpen = ref(false)
const draft = ref('')
const historyEl = ref(null)

const scrollToBottom = () => {
  nextTick(() => {
    if (historyEl.value) historyEl.value.scrollTop = historyEl.value.scrollHeight
  })
}

watch(() => [chatStore.messages.length, chatStore.loading], scrollToBottom)

const submit = async () => {
  if (!draft.value.trim()) return
  const text = draft.value
  draft.value = ''
  await chatStore.sendMessage(text)
}

// Clicking a place chip jumps the map to it and opens its info bubble, which
// carries its own add-route button (matching the id scheme HomeView uses for
// its own tour pins so the two stay in sync).
const focusPlaceOnMap = (place) => {
  mapFocusStore.request({
    id: `${place.place_type}-${place.content_id}`,
    lat: place.map_y,
    lng: place.map_x,
    title: place.title,
    addr: place.addr1,
    type: place.place_type,
    icon: place.place_type === 'food' ? 'apple' : 'pin'
  })
  if (route.path !== '/') router.push('/')
}
</script>

<template>
  <div class="chat-widget">
    <button v-if="!isOpen" class="chat-toggle" :title="t('chat.toggle')" @click="isOpen = true">
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
        <div ref="historyEl" class="chat-history">
          <div v-for="(message, index) in chatStore.messages" :key="index" class="chat-turn">
            <p :class="message.role">{{ message.content }}</p>
            <div v-if="message.places?.length" class="chat-places">
              <button
                v-for="place in message.places"
                :key="place.content_id"
                type="button"
                class="chat-place-chip"
                :title="t('chat.viewOnMap')"
                @click="focusPlaceOnMap(place)"
              >
                <PixelIcon :name="place.place_type === 'food' ? 'apple' : 'pin'" :size="11" />
                {{ place.title }}
              </button>
            </div>
          </div>
          <div v-if="chatStore.loading" class="chat-turn">
            <p class="assistant chat-loading" aria-label="응답 기다리는 중">
              <span class="chat-loading-dot"></span>
              <span class="chat-loading-dot"></span>
              <span class="chat-loading-dot"></span>
            </p>
          </div>
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
  left: auto;
  right: 20px;
  bottom: 20px;
  z-index: 90;
  width: clamp(380px, 32vw, 480px);
  min-width: 380px;
  max-width: min(480px, calc(100vw - 40px));
  min-height: 460px;
  max-height: min(75vh, 640px);
  display: flex;
  flex-direction: column;
  background: color-mix(in srgb, var(--color-surface) 94%, transparent);
  backdrop-filter: blur(10px);
  resize: both;
  overflow: hidden;
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
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 14px;
}

.chat-loading {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 12px 14px;
}

.chat-loading-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-text-muted);
  animation: chat-loading-bounce 1s ease-in-out infinite;
}

.chat-loading-dot:nth-child(2) {
  animation-delay: 0.15s;
}

.chat-loading-dot:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes chat-loading-bounce {
  0%,
  80%,
  100% {
    transform: translateY(0);
    opacity: 0.4;
  }
  40% {
    transform: translateY(-4px);
    opacity: 1;
  }
}

.chat-turn {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.chat-turn:has(.user) {
  align-items: flex-end;
}

.chat-turn:has(.assistant) {
  align-items: flex-start;
}

.chat-places {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  max-width: 78%;
}

.chat-place-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border: 2px solid var(--color-shadow);
  border-radius: 999px;
  background: var(--color-surface);
  color: var(--color-text);
  font-size: 0.74rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 2px 2px 0 var(--color-shadow);
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

@media (max-width: 860px) {
  .chat-dock {
    bottom: 76px;
    width: calc(100vw - 24px);
    min-width: 0;
    max-width: none;
    min-height: 0;
    max-height: min(65vh, 520px);
    resize: none;
  }
}

@media (max-width: 480px) {
  .chat-dock {
    right: 12px;
    bottom: 76px;
  }
}
</style>
