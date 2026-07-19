<script setup lang="ts">
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { BRAND_NAME, markUrl } from '@/assets/logo'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const email = ref('')
const password = ref('')

async function submit() {
  if (await auth.login(email.value.trim(), password.value)) {
    // Send them where they were headed before the guard intervened.
    const next = typeof route.query.next === 'string' ? route.query.next : '/admin'
    router.replace(next)
  }
  password.value = ''
}
</script>

<template>
  <div class="wrap">
    <div class="card">
      <div class="brand">
        <img :src="markUrl" alt="" aria-hidden="true" />
        <span>{{ BRAND_NAME }}</span>
      </div>

      <h1>Staff sign in</h1>
      <p class="sub">Manage the coffee catalog.</p>

      <p v-if="auth.error" class="notice notice-error">{{ auth.error }}</p>

      <form novalidate @submit.prevent="submit">
        <div class="field">
          <label for="a-email">Email</label>
          <input
            id="a-email"
            v-model="email"
            type="email"
            autocomplete="username"
            required
          />
        </div>
        <div class="field">
          <label for="a-password">Password</label>
          <input
            id="a-password"
            v-model="password"
            type="password"
            autocomplete="current-password"
            required
          />
        </div>

        <button type="submit" class="btn btn-primary btn-block" :disabled="auth.loading">
          {{ auth.loading ? 'Signing in…' : 'Sign in' }}
        </button>
      </form>

      <p class="hint">
        No account yet? Create one on the server with
        <code>python -m app.cli create-admin</code>
      </p>

      <RouterLink to="/" class="back">← Back to the shop</RouterLink>
    </div>
  </div>
</template>

<style scoped>
.wrap {
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 40px 20px;
  background: linear-gradient(165deg, #0d0b09 0%, #1c1713 60%, #241d16 100%);
}

.card {
  width: min(420px, 100%);
  background: var(--paper);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-lg);
  padding: 36px 32px 28px;
}

.brand {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-bottom: 26px;
}

.brand img {
  height: 38px;
  width: auto;
}

.brand span {
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 1.2rem;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: var(--gold-dark);
  margin-right: -0.22em;
}

h1 {
  font-size: 1.35rem;
  text-align: center;
  margin-bottom: 4px;
}

.sub {
  text-align: center;
  color: var(--ink-soft);
  font-size: 0.9rem;
  margin: 0 0 26px;
}

form .btn {
  margin-top: 8px;
}

.hint {
  margin: 22px 0 0;
  font-size: 0.78rem;
  color: var(--ink-soft);
  line-height: 1.7;
  text-align: center;
}

.hint code {
  background: var(--foam);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.95em;
}

.back {
  display: block;
  text-align: center;
  margin-top: 18px;
  font-size: 0.85rem;
  color: var(--ink-soft);
}

.back:hover {
  color: var(--accent);
}
</style>
