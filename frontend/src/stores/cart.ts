import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { ApiError, api } from '@/api/client'
import type { Cart } from '@/api/types'

const TOKEN_KEY = 'manero.cart_token'

export const useCartStore = defineStore('cart', () => {
  const cart = ref<Cart | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const drawerOpen = ref(false)

  const items = computed(() => cart.value?.items ?? [])
  const itemCount = computed(() => cart.value?.item_count ?? 0)
  const isEmpty = computed(() => items.value.length === 0)
  const token = computed(() => cart.value?.token ?? null)

  /** How much more to spend to unlock free shipping; 0 once unlocked. */
  const amountToFreeShipping = computed(() => {
    if (!cart.value) return 0
    const gap = cart.value.free_shipping_threshold_paise - cart.value.subtotal_paise
    return gap > 0 ? gap : 0
  })

  function storedToken(): string | null {
    try {
      return localStorage.getItem(TOKEN_KEY)
    } catch {
      return null // private browsing / storage disabled
    }
  }

  function persistToken(value: string) {
    try {
      localStorage.setItem(TOKEN_KEY, value)
    } catch {
      /* cart still works for this session, it just won't survive a reload */
    }
  }

  function clearToken() {
    try {
      localStorage.removeItem(TOKEN_KEY)
    } catch {
      /* nothing to clean up */
    }
  }

  /** Resolve a usable cart: reuse the stored one, or mint a fresh one. */
  async function ensureCart(): Promise<Cart> {
    if (cart.value) return cart.value

    const existing = storedToken()
    if (existing) {
      try {
        cart.value = await api.getCart(existing)
        return cart.value
      } catch (err) {
        // A 404 means the cart was pruned server-side; fall through and re-create.
        if (!(err instanceof ApiError) || err.status !== 404) throw err
        clearToken()
      }
    }

    cart.value = await api.createCart()
    persistToken(cart.value.token)
    return cart.value
  }

  /** Called once on app start so the header badge is correct after a reload. */
  async function init() {
    if (!storedToken()) return
    loading.value = true
    try {
      await ensureCart()
    } catch {
      // Never block first paint on a cart fetch.
    } finally {
      loading.value = false
    }
  }

  async function run(action: (token: string) => Promise<Cart>) {
    loading.value = true
    error.value = null
    try {
      const active = await ensureCart()
      cart.value = await action(active.token)
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Something went wrong'
      return false
    } finally {
      loading.value = false
    }
  }

  const addItem = (variantId: number, quantity = 1) =>
    run((t) => api.addToCart(t, variantId, quantity))

  const updateQuantity = (itemId: number, quantity: number) =>
    run((t) => api.updateCartItem(t, itemId, quantity))

  const removeItem = (itemId: number) => run((t) => api.removeCartItem(t, itemId))

  async function refresh() {
    if (!cart.value) return
    try {
      cart.value = await api.getCart(cart.value.token)
    } catch {
      /* keep showing the last good state */
    }
  }

  /** After a successful payment the server has already emptied this cart. */
  function reset() {
    cart.value = null
    clearToken()
  }

  function openDrawer() {
    drawerOpen.value = true
  }

  function closeDrawer() {
    drawerOpen.value = false
  }

  return {
    cart,
    items,
    itemCount,
    isEmpty,
    token,
    loading,
    error,
    drawerOpen,
    amountToFreeShipping,
    init,
    ensureCart,
    addItem,
    updateQuantity,
    removeItem,
    refresh,
    reset,
    openDrawer,
    closeDrawer,
  }
})
