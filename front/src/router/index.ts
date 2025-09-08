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
      path: '/success',
      name: 'success',
      component: () => import('../views/SuccessView.vue')
    },
    {
      path: '/mypage',
      name: 'mypage',
      component: () => import('../views/MyPageView.vue')
    }
  ]
})

export default router

