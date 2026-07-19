<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { BRAND_NAME, logoUrl } from '@/assets/logo'
import { useCartStore } from '@/stores/cart'

const cart = useCartStore()
const route = useRoute()
const mobileOpen = ref(false)

const links = [
  { to: '/shop', label: 'Shop All' },
  { to: '/shop?grind=filter', label: 'Filter Coffee' },
  { to: '/shop?grind=instant', label: 'Instant' },
  { to: '/shop?bean_type=arabica', label: 'Arabica' },
]

watch(() => route.fullPath, () => (mobileOpen.value = false))
</script>

<template>
  <header class="header">
    <div class="container bar">
      <button
        class="menu-btn"
        :aria-expanded="mobileOpen"
        aria-label="Toggle navigation menu"
        @click="mobileOpen = !mobileOpen"
      >
        <span aria-hidden="true">{{ mobileOpen ? '✕' : '☰' }}</span>
      </button>

      <RouterLink to="/" class="brand" :aria-label="`${BRAND_NAME} home`">
        <img :src="logoUrl" :alt="BRAND_NAME" class="logo" />
      </RouterLink>

      <nav class="nav" aria-label="Primary">
        <RouterLink v-for="link in links" :key="link.to" :to="link.to" class="nav-link">
          {{ link.label }}
        </RouterLink>
      </nav>

      <button class="cart-btn" @click="cart.openDrawer()">
        <span aria-hidden="true">🛒</span>
        <span class="visually-hidden">Open cart</span>
        <span v-if="cart.itemCount" class="count" aria-hidden="true">
          {{ cart.itemCount }}
        </span>
        <span v-if="cart.itemCount" class="visually-hidden">
          {{ cart.itemCount }} item(s) in cart
        </span>
      </button>
    </div>

    <nav v-if="mobileOpen" class="mobile-nav" aria-label="Mobile">
      <RouterLink v-for="link in links" :key="link.to" :to="link.to" class="mobile-link">
        {{ link.label }}
      </RouterLink>
    </nav>
  </header>
</template>

<style scoped>
/* Dark header: the gold mark needs a dark ground to read as gold. */
.header {
  position: sticky;
  top: 0;
  z-index: 40;
  background: var(--espresso);
  border-bottom: 1px solid rgba(212, 175, 55, 0.22);
}

.bar {
  height: var(--header-h);
  display: flex;
  align-items: center;
  gap: 20px;
}

.brand {
  display: flex;
  align-items: center;
  min-height: 44px;
}

.logo {
  height: 62px;
  width: auto;
}

.nav {
  display: flex;
  gap: 24px;
  margin-left: auto;
}

.nav-link {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--crema-light);
  padding: 6px 0;
  border-bottom: 2px solid transparent;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: var(--gold-light);
  border-bottom-color: var(--gold);
}

.cart-btn {
  position: relative;
  background: none;
  border: none;
  font-size: 1.25rem;
  line-height: 1;
  color: var(--gold-light);
  /* 44px minimum: comfortable thumb target on touch screens. */
  min-width: 44px;
  min-height: 44px;
  display: grid;
  place-items: center;
}

.count {
  position: absolute;
  top: 0;
  right: 0;
  min-width: 18px;
  height: 18px;
  padding: 0 5px;
  border-radius: 999px;
  background: linear-gradient(180deg, var(--gold) 0%, var(--gold-dark) 100%);
  color: var(--espresso);
  font-size: 0.7rem;
  font-weight: 700;
  display: grid;
  place-items: center;
}

.menu-btn {
  display: none;
  background: none;
  border: none;
  font-size: 1.15rem;
  color: var(--gold-light);
  min-width: 44px;
  min-height: 44px;
}

.mobile-nav {
  display: none;
  flex-direction: column;
  border-top: 1px solid rgba(212, 175, 55, 0.22);
  padding: 8px 20px 16px;
  background: var(--espresso);
}

.mobile-link {
  padding: 14px 0;
  border-bottom: 1px solid rgba(212, 175, 55, 0.14);
  font-weight: 500;
  color: var(--crema-light);
}

.mobile-link:last-child {
  border-bottom: none;
}

@media (max-width: 860px) {
  .nav {
    display: none;
  }
  .menu-btn {
    display: grid;
    place-items: center;
  }
  .mobile-nav {
    display: flex;
  }
  .brand {
    margin: 0 auto;
  }
  .logo {
    height: 50px;
  }
}
</style>
