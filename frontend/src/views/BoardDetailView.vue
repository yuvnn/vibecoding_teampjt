<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { deletePost } from '../api/posts'
import { useBoardStore } from '../stores/board'

const props = defineProps({ id: { type: [String, Number], required: true } })
const router = useRouter()
const boardStore = useBoardStore()

const showDeleteConfirm = ref(false)
const deletePassword = ref('')
const deleteError = ref('')

onMounted(() => {
  boardStore.loadPost(props.id)
})

const confirmDelete = async () => {
  deleteError.value = ''
  try {
    await deletePost(props.id, deletePassword.value)
    router.push('/')
  } catch (err) {
    deleteError.value = err.response?.data?.detail ?? '삭제에 실패했습니다.'
  }
}
</script>

<template>
  <section v-if="boardStore.currentPost" class="board-detail">
    <p class="meta">{{ boardStore.currentPost.category_name }}</p>
    <h2>{{ boardStore.currentPost.title }}</h2>
    <p class="meta">
      작성일 {{ boardStore.currentPost.created_at }} · 조회수 {{ boardStore.currentPost.view_count }}
    </p>
    <div class="content">{{ boardStore.currentPost.content }}</div>
    <div class="actions">
      <router-link :to="`/board/${id}/edit`">
        <button type="button">수정</button>
      </router-link>
      <button type="button" @click="showDeleteConfirm = true">삭제</button>
    </div>

    <div v-if="showDeleteConfirm" class="password-confirm">
      <input v-model="deletePassword" type="password" placeholder="비밀번호 확인" />
      <button type="button" @click="confirmDelete">확인</button>
      <p v-if="deleteError" class="error">{{ deleteError }}</p>
    </div>
  </section>
</template>
