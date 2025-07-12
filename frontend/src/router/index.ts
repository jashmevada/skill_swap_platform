import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/auth/LoginView.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/auth/RegisterView.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/user/ProfileView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/skills',
      name: 'skills',
      component: () => import('../views/skills/SkillsView.vue'),
    },
    {
      path: '/my-skills',
      name: 'my-skills',
      component: () => import('../views/skills/MySkillsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/swaps',
      name: 'swaps',
      component: () => import('../views/swaps/SwapsView.vue'),
    },
    {
      path: '/my-swaps',
      name: 'my-swaps',
      component: () => import('../views/swaps/MySwapsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/admin/AdminDashboard.vue'),
      meta: { requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/users/:id',
      name: 'user-profile',
      component: () => import('../views/user/UserProfileView.vue'),
      props: true
    },
    // Catch all route - 404
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('../views/NotFoundView.vue'),
    },
  ],
})

// Navigation guards
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Check if route requires authentication
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
    return
  }

  // Check if route requires guest (non-authenticated) user
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    next('/')
    return
  }

  // Check if route requires admin privileges
  if (to.meta.requiresAdmin) {
    if (!authStore.user) {
      // Try to fetch current user if not already loaded
      await authStore.fetchCurrentUser()
    }
    
    if (!authStore.user?.is_admin) {
      next('/')
      return
    }
  }

  next()
})

export default router
