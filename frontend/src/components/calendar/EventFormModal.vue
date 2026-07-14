<script setup>
import { reactive, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import TagInput from '../common/TagInput.vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  event: { type: Object, default: null },
  prefill: { type: Object, default: null },
  initialDate: { type: String, default: '' }
})
const emit = defineEmits(['submit', 'delete', 'close'])

const { t } = useI18n()

const form = reactive({ title: '', start: '', end: '', description: '', imageDataUrl: '', tags: [] })

const resetForm = () => {
  const source = props.event ?? props.prefill
  form.title = source?.title ?? ''
  form.start = props.event?.start ?? props.initialDate ?? ''
  form.end = props.event?.end ?? form.start
  form.description = source?.description ?? ''
  form.imageDataUrl = source?.imageDataUrl ?? ''
  form.tags = source?.tags ?? []
}

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) resetForm()
  }
)

const onImageChange = (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  const reader = new FileReader()
  reader.onload = () => {
    form.imageDataUrl = reader.result
  }
  reader.readAsDataURL(file)
}

const submit = () => {
  if (!form.title.trim() || !form.start) return
  emit('submit', {
    id: props.event?.id,
    title: form.title.trim(),
    start: form.start,
    end: form.end || form.start,
    description: form.description,
    imageDataUrl: form.imageDataUrl,
    tags: form.tags
  })
}
</script>

<template>
  <div v-if="open" class="modal-overlay" @click.self="emit('close')">
    <div class="modal-panel panel">
      <div class="modal-header">
        <h3>{{ event ? t('calendar.modalTitleEdit') : t('calendar.modalTitleNew') }}</h3>
        <button type="button" class="btn-icon" @click="emit('close')">×</button>
      </div>

      <form class="modal-form" @submit.prevent="submit">
        <div class="field">
          <label>{{ t('calendar.fieldEventTitle') }}</label>
          <input v-model="form.title" required />
        </div>
        <div class="field-row">
          <div class="field">
            <label>{{ t('calendar.fieldStart') }}</label>
            <input v-model="form.start" type="date" required />
          </div>
          <div class="field">
            <label>{{ t('calendar.fieldEnd') }}</label>
            <input v-model="form.end" type="date" :min="form.start" />
          </div>
        </div>
        <div class="field">
          <label>{{ t('calendar.fieldDescription') }}</label>
          <textarea v-model="form.description" rows="3"></textarea>
        </div>
        <div class="field">
          <label>{{ t('calendar.fieldImage') }}</label>
          <input type="file" accept="image/*" @change="onImageChange" />
          <img v-if="form.imageDataUrl" :src="form.imageDataUrl" class="image-preview" alt="" />
        </div>
        <div class="field">
          <label>{{ t('calendar.fieldTags') }}</label>
          <TagInput v-model="form.tags" />
        </div>
        <p class="field-hint">{{ t('calendar.localNotice') }}</p>

        <div class="modal-footer">
          <button
            v-if="event"
            type="button"
            class="btn btn-danger btn-sm"
            @click="emit('delete', event.id)"
          >
            {{ t('common.delete') }}
          </button>
          <div class="modal-footer-right">
            <button type="button" class="btn btn-outline btn-sm" @click="emit('close')">
              {{ t('common.cancel') }}
            </button>
            <button type="submit" class="btn btn-primary btn-sm">{{ t('common.save') }}</button>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  padding: 16px;
}

.modal-panel {
  width: 100%;
  max-width: 440px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.modal-header h3 {
  margin: 0;
}

.modal-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.field-row {
  display: flex;
  gap: 10px;
}

.field-row .field {
  flex: 1;
}

.field-hint {
  margin: 0;
  font-size: 0.78rem;
  color: var(--color-text-muted);
}

.image-preview {
  margin-top: 8px;
  max-width: 100%;
  max-height: 140px;
  border-radius: var(--radius-sm);
  object-fit: cover;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 6px;
}

.modal-footer-right {
  display: flex;
  gap: 8px;
  margin-left: auto;
}
</style>
