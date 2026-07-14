<script setup>
import { useI18n } from 'vue-i18n'
import { hasKakaoKey, shareToKakao } from '../../utils/kakao'
import { useToastStore } from '../../stores/toast'

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
      💬 {{ t('board.detail.shareKakao') }}
    </button>
    <button type="button" class="btn btn-ghost btn-sm" @click="onCopyLink">
      🔗 {{ t('common.copyLink') }}
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
