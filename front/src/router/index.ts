import { createRouter, createWebHistory } from 'vue-router'
import LandingView from '../views/LandingView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'landing',
      component: LandingView
    },
    {
      path: '/home',
      name: 'home',
      component: () => import('../views/HomeView.vue')
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

