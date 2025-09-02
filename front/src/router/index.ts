import { createRouter, createWebHistory } from 'vue-router'
import LandingView from '../views/LandingView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
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
    },
    {
      path: '/template/create',
      name: 'template-create',
      component: () => import('../views/TemplateCreateView.vue')
    },
    {
      path: '/template/result',
      name: 'template-result',
      component: () => import('../views/TemplateResultView.vue')
    },
    {
      path: '/chat',
      name: 'chat',
      component: () => import('../views/ChatView.vue')
    },
    {
      path: '/success',
      name: 'success',
      component: () => import('../views/SuccessView.vue')

    }
  ]
})

export default router

