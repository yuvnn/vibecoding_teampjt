import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import BoardListView from '../views/BoardListView.vue'
import BoardDetailView from '../views/BoardDetailView.vue'
import BoardWriteView from '../views/BoardWriteView.vue'
import CalendarView from '../views/CalendarView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/board', name: 'board-list', component: BoardListView },
    { path: '/board/new', name: 'board-write', component: BoardWriteView },
    { path: '/board/:id', name: 'board-detail', component: BoardDetailView, props: true },
    { path: '/board/:id/edit', name: 'board-edit', component: BoardWriteView, props: true },
    { path: '/calendar', name: 'calendar', component: CalendarView }
  ],
  scrollBehavior() {
    return { top: 0 }
  }
})

export default router
