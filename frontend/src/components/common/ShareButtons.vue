<script setup>
import { useI18n } from 'vue-i18n'
import { hasKakaoKey, shareToKakao } from '../../utils/kakao'
import { useToastStore } from '../../stores/toast'
import PixelIcon from './PixelIcon.vue'

const props = defineProps({
  title: { type: String, required: true },
  description: { type: String, default: '' }
})

const { t } = useI18n()
const toastStore = useToastStore()

const shareUrl = () => window.location.href

const onKakaoShare = async () => {
  if (!hasKakaoKey()) {
    toastStore.push(t('home.kakaoMissingTitle'), { type: 'info' })
    return
  }
  try {
    await shareToKakao({ title: props.title, description: props.description, url: shareUrl() })
  } catch {
    toastStore.push(t('common.errorGeneric'), { type: 'info' })
  }
}

const onCopyLink = async () => {
  try {
    await navigator.clipboard.writeText(shareUrl())
    toastStore.push(t('common.linkCopied'), { type: 'success' })
  } catch {
    toastStore.push(t('common.errorGeneric'), { type: 'info' })
  }
}
</script>

<template>
  <div class="share-buttons">
    <button type="button" class="btn btn-ghost btn-sm" @click="onKakaoShare">
      <PixelIcon name="chat" :size="14" /> {{ t('board.detail.shareKakao') }}
    </button>
    <button type="button" class="btn btn-ghost btn-sm" @click="onCopyLink">
      <PixelIcon name="link" :size="14" /> {{ t('common.copyLink') }}
    </button>
  </div>
</template>

<style scoped>
.share-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
