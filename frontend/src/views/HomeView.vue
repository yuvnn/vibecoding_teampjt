<script setup>
import { onMounted, ref } from 'vue'
import { useBoardStore } from '../stores/board'
import { useCategoryStore } from '../stores/categories'

const categoryStore = useCategoryStore()
const boardStore = useBoardStore()
const selectedCategoryId = ref(null)

const load = () => {
  boardStore.loadPosts({ category_id: selectedCategoryId.value ?? undefined, limit: 50 })
}

const selectCategory = (categoryId) => {
  selectedCategoryId.value = categoryId
  load()
}

onMounted(async () => {
  await categoryStore.ensureLoaded()
  load()
})
</script>

<template>
  <section class="home">
    <div class="home-banner">
      <h1>지역 정보 공유 커뮤니티 LocalHub</h1>
      <p>대전/충청권 지역 정보를 한눈에 만나보세요</p>
    </div>

    <nav class="home-categories">
      <button
        type="button"
        :class="{ active: selectedCategoryId === null }"
        @click="selectCategory(null)"
      >
        전체
      </button>
      <button
        v-for="category in categoryStore.categories"
        :key="category.id"
        type="button"
        :class="{ active: selectedCategoryId === category.id }"
        @click="selectCategory(category.id)"
      >
        {{ category.name }}
      </button>
    </nav>

    <table>
      <thead>
        <tr>
          <th>번호</th>
          <th>카테고리</th>
          <th>제목</th>
          <th>작성일</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="post in boardStore.posts" :key="post.id">
          <td>{{ post.id }}</td>
          <td>{{ categoryStore.nameOf(post.category_id) }}</td>
          <td>
            <router-link :to="`/board/${post.id}`">{{ post.title }}</router-link>
          </td>
          <td>{{ post.created_at }}</td>
        </tr>
        <tr v-if="!boardStore.loading && boardStore.posts.length === 0">
          <td colspan="4" class="board-list-empty">게시글이 없습니다.</td>
        </tr>
      </tbody>
    </table>
  </section>
</template>
