import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/about',
      name: 'about',
      // 라우트 레벨에서 코드 분할
      // 이렇게 하면 이 라우트에 대한 코드가 별도의 청크로 분할되어
      // 라우트가 방문될 때만 로드됩니다.
      component: () => import('../views/AboutView.vue')
    }
  ]
})

export default router

