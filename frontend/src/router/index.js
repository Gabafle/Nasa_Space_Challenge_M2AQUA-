import { createRouter, createWebHistory } from 'vue-router'
import { useAuth } from '../stores/auth'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/login', component: () => import('../views/Login.vue'), meta: { guestOnly: true } },
  { path: '/signup', component: () => import('../views/Signup.vue'), meta: { guestOnly: true } },
  { path: '/dashboard', component: () => import('../views/Dashboard.vue'), meta: { requiresAuth: true } },
  { path: '/upload', component: () => import('../views/Upload.vue'), meta: { requiresAuth: true } },
  { path: '/datasets', component: () => import('../views/Datasets.vue'), meta: { requiresAuth: true } },
  { path: '/wizard', component: () => import('../views/Wizard.vue'), meta: { requiresAuth: true } },
  { path: '/analyze', component: () => import('../views/Analyze.vue'), meta: { requiresAuth: true } },
  { path: '/analyses', component: () => import('../views/Analyses.vue'), meta: { requiresAuth: true } },
  { path: '/viz/:runId', component: () => import('../views/Viz.vue'), meta: { requiresAuth: true } },
  { path: '/labels', component: () => import('../views/Labels.vue'), meta: { requiresAuth: true, roles: ['researcher', 'admin'] } },
  { path: '/models', component: () => import('../views/Models.vue'), meta: { requiresAuth: true } },
  { path: '/leaderboard', component: () => import('../views/Leaderboard.vue'), meta: { requiresAuth: true } },
  { path: '/graphs', component: () => import('../views/Graphs.vue'), meta: { requiresAuth: true } }, // NEW ROUTE
  { path: '/account', component: () => import('../views/Account.vue'), meta: { requiresAuth: true } }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const auth = useAuth()
  auth.load()

  if (to.meta.requiresAuth && !auth.accessToken) {
    next({ path: '/login', query: { r: to.fullPath } })
  } else if (to.meta.guestOnly && auth.accessToken) {
    next('/dashboard')
  } else if (to.meta.roles && !to.meta.roles.includes(auth.user?.role)) {
    next('/dashboard')
  } else {
    next()
  }
})

export default router
