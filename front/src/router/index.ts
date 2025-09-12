import { createRouter, createWebHistory } from 'vue-router'
import LandingView from '../views/LandingView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'landing',
      component: LandingView,
      meta: { requiresAuth: false } // 인증 필요 없음
    },
    {
      path: '/template/create',
      name: 'template-create',
      component: () => import('../views/TemplateCreateView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/template/result',
      name: 'template-result',
      component: () => import('../views/TemplateResultView.vue'),
      meta: { requiresAuth: true }
    },

    {
      path: '/success',
      name: 'success',
      component: () => import('../views/SuccessView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/mypage',
      name: 'mypage',
      component: () => import('../views/MyPageView.vue'),
      meta: { requiresAuth: true }
    }
  ]
})

// 라우트 가드
// 토큰이 필요한 페이지 접근 시 로그인 여부 확인
router.beforeEach(async (to, from, next) => {
  // 인증이 필요 없으면 통과
  if (!to.meta.requiresAuth) {
    return next()
  }

  // 토큰 정보 조회
  const token = localStorage.getItem('accessToken')

  // 토큰이 없을 경우 랜딩 페이지로 리다이렉트
  if (to.meta.requiresAuth && !token) {
    window.alert("로그인이 필요한 페이지 입니다.")
    return next({ name: 'landing' })
  }

  // 서버에 검증 시도
  try {
    const res = await fetch('/api/auth/me', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    if (res.ok) {
      return next()
    } else if (res.status === 401) {
      window.alert("로그인이 필요한 페이지 입니다.")
      localStorage.removeItem('accessToken')
      return next({ name: 'landing' })
    } else if (res.status === 403) {
      window.alert("접근 권한이 없습니다.")
      return next({ name: 'landing' })
    } else {
      window.alert("알 수 없는 오류가 발생했습니다.")
      return next({ name: 'landing' })
    }
  } catch (error) {
    console.error("네트워크 오류:", error)
    window.alert("서버와 통신할 수 없습니다.")
    return next({ name: 'landing' })
  }
})

export default router

