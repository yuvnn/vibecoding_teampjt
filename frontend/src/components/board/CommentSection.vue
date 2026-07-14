<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { createComment, deleteComment, fetchComments } from '../../api/comments'

const props = defineProps({ postId: { type: [String, Number], required: true } })

const { t } = useI18n()
const comments = ref([])
const form = reactive({ content: '', password: '' })
const error = ref('')
const openDeleteId = ref(null)
const deletePassword = ref('')
const deleteError = ref('')

const load = async () => {
  const { data } = await fetchComments(props.postId)
  comments.value = data
}

const submit = async () => {
  error.value = ''
  if (!form.content.trim() || !form.password) return
  try {
    await createComment(props.postId, { content: form.content, password: form.password })
    form.content = ''
    form.password = ''
    await load()
  } catch (err) {
    error.value = err.response?.data?.detail ?? t('common.errorGeneric')
  }
}

const openDelete = (commentId) => {
  openDeleteId.value = openDeleteId.value === commentId ? null : commentId
  deletePassword.value = ''
  deleteError.value = ''
}

const confirmDelete = async (commentId) => {
  deleteError.value = ''
  try {
    await deleteComment(commentId, deletePassword.value)
    openDeleteId.value = null
    await load()
  } catch (err) {
    deleteError.value = err.response?.data?.detail ?? t('board.detail.commentDeleteError')
  }
}

onMounted(load)
</script>

<template>
  <section class="comment-section">
    <h3 class="comment-heading">{{ t('board.detail.commentsTitle', { count: comments.length }) }}</h3>

    <form class="comment-form" @submit.prevent="submit">
      <textarea v-model="form.content" :placeholder="t('board.detail.commentPlaceholder')" rows="2" />
      <div class="comment-form-row">
        <input
          v-model="form.password"
          type="password"
          :placeholder="t('board.detail.commentPasswordPlaceholder')"
        />
        <button type="submit" class="btn btn-primary btn-sm">{{ t('board.detail.commentSubmit') }}</button>
      </div>
      <p v-if="error" class="error">{{ error }}</p>
    </form>

    <ul class="comment-list">
      <li v-for="comment in comments" :key="comment.id" class="comment-item">
        <div class="comment-item-body">
          <p class="comment-content">{{ comment.content }}</p>
          <span class="comment-date">{{ comment.created_at?.slice(0, 16).replace('T', ' ') }}</span>
        </div>
        <button type="button" class="btn btn-ghost btn-sm" @click="openDelete(comment.id)">
          {{ t('board.detail.commentDelete') }}
        </button>

        <div v-if="openDeleteId === comment.id" class="password-confirm">
          <input
            v-model="deletePassword"
            type="password"
            :placeholder="t('board.detail.deleteConfirmPlaceholder')"
          />
          <button type="button" class="btn btn-danger btn-sm" @click="confirmDelete(comment.id)">
            {{ t('board.detail.deleteConfirmButton') }}
          </button>
          <p v-if="deleteError" class="error">{{ deleteError }}</p>
        </div>
      </li>
      <li v-if="!comments.length" class="empty-state">{{ t('board.detail.commentEmpty') }}</li>
    </ul>
  </section>
</template>

<style scoped>
.comment-section {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.comment-heading {
  margin: 0;
  font-size: 1rem;
}

.comment-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.comment-form textarea {
  min-height: 64px;
}

.comment-form-row {
  display: flex;
  gap: 8px;
}

.comment-form-row input {
  flex: 1;
  max-width: 220px;
}

.comment-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.comment-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
  padding: 12px 0;
  border-bottom: 1px solid var(--color-border);
  flex-wrap: wrap;
}

.comment-item:last-child {
  border-bottom: none;
}

.comment-item-body {
  flex: 1;
  min-width: 200px;
}

.comment-content {
  margin: 0 0 4px;
  font-size: 0.9rem;
  white-space: pre-wrap;
}

.comment-date {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.password-confirm {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.password-confirm input {
  max-width: 180px;
}
</style>
