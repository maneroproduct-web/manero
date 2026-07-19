import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { ApiError, api, setAuthToken } from '@/api/client'
import type { Admin } from '@/api/types'

const TOKEN_KEY = 'manero.admin_token'

export const useAuthStore = defineStore('auth', () => {
  const admin = ref<Admin | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  /** True until the stored token has been checked, so guards don't act early. */
  const ready = ref(false)

  const isSignedIn = computed(() => admin.value !== null)

  function readToken(): string | null {
    try {
      return localStorage.getItem(TOKEN_KEY)
    } catch {
      return null
    }
  }

  function storeToken(token: string | null) {
    try {
      if (token) localStorage.setItem(TOKEN_KEY, token)
      else localStorage.removeItem(TOKEN_KEY)
    } catch {
      /* session-only login is still better than failing outright */
    }
  }

  /**
   * Restore a session from a stored token, verifying it with the server.
   *
   * The token is never trusted on its face: /auth/me confirms the account still
   * exists and is active, so a revoked admin cannot keep a usable UI just
   * because their token has not expired yet.
   */
  async function init() {
    const token = readToken()
    if (!token) {
      ready.value = true
      return
    }

    setAuthToken(token)
    try {
      admin.value = await api.me()
    } catch {
      admin.value = null
      setAuthToken(null)
      storeToken(null)
    } finally {
      ready.value = true
    }
  }

  async function login(email: string, password: string): Promise<boolean> {
    loading.value = true
    error.value = null
    try {
      const result = await api.login(email, password)
      setAuthToken(result.access_token)
      storeToken(result.access_token)
      admin.value = result.admin
      return true
    } catch (err) {
      error.value =
        err instanceof ApiError && err.status === 401
          ? err.message
          : 'Could not sign in just now. Is the API running?'
      return false
    } finally {
      loading.value = false
    }
  }

  function logout() {
    admin.value = null
    error.value = null
    setAuthToken(null)
    storeToken(null)
  }

  return { admin, loading, error, ready, isSignedIn, init, login, logout }
})
