<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { createPost, fetchPost, updatePost } from '../api/posts'
import { useCategoryStore } from '../stores/categories'

const props = defineProps({ id: { type: [String, Number], default: null } })

const router = useRouter()
const categoryStore = useCategoryStore()

const isEdit = computed(() => !!props.id)
const form = reactive({ category_id: null, title: '', content: '', password: '' })
const error = ref('')

onMounted(async () => {
  await categoryStore.ensureLoaded()
  if (isEdit.value) {
    const { data } = await fetchPost(props.id)
    form.title = data.title
    form.content = data.content
  } else {
    form.category_id = categoryStore.categories[0]?.id ?? null
  }
})

const submit = async () => {
  error.value = ''
  try {
    if (isEdit.value) {
      const { data } = await updatePost(props.id, {
        title: form.title,
        content: form.content,
        password: form.password
      })
      router.push(`/board/${data.id}`)
    } else {
      const { data } = await createPost(form)
      router.push(`/board/${data.id}`)
    }
  } catch (err) {
    error.value = err.response?.data?.detail ?? '요청 처리 중 오류가 발생했습니다.'
  }
}
</script>

<template>
  <section class="board-write">
    <h2>{{ isEdit ? '게시글 수정' : '게시글 작성' }}</h2>
    <p v-if="error" class="error">{{ error }}</p>
    <form @submit.prevent="submit">
      <select v-if="!isEdit" v-model="form.category_id" required>
        <option v-for="category in categoryStore.categories" :key="category.id" :value="category.id">
          {{ category.name }}
        </option>
      </select>
      <input v-model="form.title" placeholder="제목" required />
      <textarea v-model="form.content" placeholder="내용" required></textarea>
      <input
        v-model="form.password"
        type="password"
        :placeholder="isEdit ? '작성 시 등록한 비밀번호' : '수정용 비밀번호'"
        required
      />
      <button type="submit">{{ isEdit ? '수정' : '등록' }}</button>
    </form>
  </section>
</template>
