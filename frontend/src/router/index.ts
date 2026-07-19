import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/', name: 'home', component: () => import('@/views/HomeView.vue') },
  { path: '/shop', name: 'shop', component: () => import('@/views/ShopView.vue') },
  {
    path: '/shop/:slug',
    name: 'product',
    component: () => import('@/views/ProductView.vue'),
    props: true,
  },
  { path: '/story', name: 'story', component: () => import('@/views/AboutView.vue') },
  {
    path: '/contact',
    name: 'contact',
    component: () => import('@/views/ContactView.vue'),
  },
  {
    // One view, four documents: /policies/terms, /privacy, /shipping, /refunds
    path: '/policies/:slug',
    name: 'policy',
    component: () => import('@/views/PolicyView.vue'),
    props: true,
  },
  { path: '/cart', name: 'cart', component: () => import('@/views/CartView.vue') },
  {
    path: '/checkout',
    name: 'checkout',
    component: () => import('@/views/CheckoutView.vue'),
  },
  {
    path: '/order/:orderNumber',
    name: 'order',
    component: () => import('@/views/OrderConfirmationView.vue'),
    props: true,
  },
  {
    path: '/admin/login',
    name: 'admin-login',
    component: () => import('@/views/admin/AdminLoginView.vue'),
    meta: { chrome: false },
  },
  {
    path: '/admin',
    name: 'admin-products',
    component: () => import('@/views/admin/AdminProductsView.vue'),
    // `chrome: false` hides the shop header/footer — admin has its own.
    meta: { requiresAdmin: true, chrome: false },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
  },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, saved) {
    if (saved) return saved
    // Changing only the filter query should not yank the page back to the top.
    if (to.path === from.path) return
    return { top: 0 }
  },
})

/**
 * Keeps unauthenticated people out of the admin screens.
 *
 * This is convenience, not security: it only hides UI. Every admin API route
 * enforces the same rule server-side, which is what actually protects the data —
 * a guard in the browser can be stepped around by anyone with devtools.
 */
router.beforeEach(async (to) => {
  if (!to.meta.requiresAdmin) return true

  const auth = useAuthStore()
  // On a hard load into /admin, wait for the stored token to be verified before
  // deciding, or we would bounce a signed-in admin to the login screen.
  if (!auth.ready) await auth.init()

  if (!auth.isSignedIn) {
    return { path: '/admin/login', query: { next: to.fullPath } }
  }
  return true
})
