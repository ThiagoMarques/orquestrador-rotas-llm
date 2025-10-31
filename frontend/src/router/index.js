import { createRouter, createWebHistory } from 'vue-router'

import LoginView from '../views/LoginView.vue'

const HomeView = () => import('../views/HomeView.vue')
const RegisterView = () => import('../views/RegisterView.vue')

const routes = [
  {
    path: '/',
    name: 'Login',
    component: LoginView,
  },
  {
    path: '/home',
    name: 'Home',
    component: HomeView,
    meta: {
      requiresAuth: true,
    },
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterView,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('accessToken')

  if (to.meta.requiresAuth && !token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

  if ((to.name === 'Login' || to.name === 'Register') && token) {
    next({ name: 'Home' })
    return
  }

  next()
})

export default router

