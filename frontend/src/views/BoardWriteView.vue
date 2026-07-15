<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { createPost, fetchPost, updatePost } from '../api/posts'
import { useCategoryStore } from '../stores/categories'
import { useLocalMetaStore } from '../stores/localMeta'
import TagInput from '../components/common/TagInput.vue'
import PixelIcon from '../components/common/PixelIcon.vue'

const props = defineProps({ id: { type: [String, Number], default: null } })

const router = useRouter()
const { t } = useI18n()
const categoryStore = useCategoryStore()
const metaStore = useLocalMetaStore()

const isEdit = computed(() => !!props.id)
const form = reactive({ category_id: null, title: '', content: '', password: '', tags: [] })
const error = ref('')
const submitting = ref(false)

onMounted(async () => {
  await categoryStore.ensureLoaded()
  if (isEdit.value) {
    const { data } = await fetchPost(props.id)
    form.title = data.title
    form.content = data.content
    form.tags = metaStore.tagsFor(props.id)
  } else {
    form.category_id = categoryStore.categories[0]?.id ?? null
  }
})

const submit = async () => {
  error.value = ''
  submitting.value = true
  try {
    if (isEdit.value) {
      const { data } = await updatePost(props.id, {
        title: form.title,
        content: form.content,
        password: form.password
      })
      metaStore.setTags(props.id, form.tags)
      router.push(`/board/${data.id}`)
    } else {
      const { data } = await createPost({
        category_id: form.category_id,
        title: form.title,
        content: form.content,
        password: form.password
      })
      metaStore.setTags(data.id, form.tags)
      router.push(`/board/${data.id}`)
    }
  } catch (err) {
    error.value = err.response?.data?.detail ?? t('common.errorGeneric')
  } finally {
    submitting.value = false
  }
}

const goBack = () => {
  router.back()
}
</script>

<template>
  <section class="board-write">
    <div class="write-card panel">
      <div class="write-card-header">
        <button type="button" class="btn btn-ghost btn-icon" :title="t('common.back')" @click="goBack">
          <PixelIcon name="arrowLeft" :size="16" />
        </button>
        <h1 class="page-title">{{ isEdit ? t('board.write.titleEdit') : t('board.write.titleNew') }}</h1>
      </div>
      <p v-if="error" class="error">{{ error }}</p>

      <form class="write-form" @submit.prevent="submit">
      <div v-if="!isEdit" class="field">
        <label>{{ t('board.category') }}</label>
        <select v-model="form.category_id" required>
          <option v-for="category in categoryStore.categories" :key="category.id" :value="category.id">
            {{ category.name }}
          </option>
        </select>
      </div>

      <div class="field">
        <label>{{ t('board.write.fieldTitle') }}</label>
        <input v-model="form.title" required maxlength="255" />
      </div>

      <div class="field">
        <label>{{ t('board.write.fieldContent') }}</label>
        <textarea v-model="form.content" required></textarea>
      </div>

      <div class="field">
        <label>{{ t('board.write.fieldTags') }}</label>
        <TagInput v-model="form.tags" :placeholder="t('board.detail.addTagPlaceholder')" />
        <p class="field-hint">{{ t('board.write.tagsHint') }}</p>
      </div>

      <div class="field">
        <label>{{ isEdit ? t('board.write.fieldPasswordEdit') : t('board.write.fieldPassword') }}</label>
        <input v-model="form.password" type="password" required />
      </div>

      <button type="submit" class="btn btn-primary" :disabled="submitting">
        {{ isEdit ? t('board.write.submitEdit') : t('board.write.submitNew') }}
      </button>
      </form>
    </div>
  </section>
</template>

<style scoped>
.board-write {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - var(--header-height) - 120px);
}

.write-card {
  width: 100%;
  max-width: 640px;
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.write-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.write-card-header .page-title {
  margin: 0;
}

.write-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.field-hint {
  margin: 0;
  font-size: 0.78rem;
  color: var(--color-text-muted);
}

.write-form button {
  align-self: flex-start;
}
</style>
