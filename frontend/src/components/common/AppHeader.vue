<template>
  <header class="app-header">
    <router-link to="/" class="logo">LocalHub</router-link>
    <nav class="app-nav">
      <router-link to="/board/new">글쓰기</router-link>
    </nav>
  </header>
</template>

<style scoped>
.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
}

.logo {
  font-weight: 700;
  font-size: 1.25rem;
  color: #2563eb;
}

.app-nav {
  display: flex;
  gap: 16px;
}
</style>
