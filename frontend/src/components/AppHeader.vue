<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { BRAND_NAME, markUrl } from '@/assets/logo'
import { useCartStore } from '@/stores/cart'

const cart = useCartStore()
const route = useRoute()
const mobileOpen = ref(false)

const links = [
  { to: '/shop', label: 'Shop All' },
  { to: '/shop?grind=filter', label: 'Filter Coffee' },
  { to: '/shop?grind=instant', label: 'Instant' },
  { to: '/story', label: 'Our Story' },
  { to: '/contact', label: 'Contact' },
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

      <!-- Monogram as image, wordmark as live text: a stacked lockup shrunk to
           header height leaves "MANERO" an illegible smudge. -->
      <RouterLink to="/" class="brand" :aria-label="`${BRAND_NAME} home`">
        <img :src="markUrl" alt="" aria-hidden="true" class="mark" />
        <span class="wordmark">{{ BRAND_NAME }}</span>
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
  gap: 12px;
  min-height: 44px;
}

.mark {
  height: 46px;
  width: auto;
  flex-shrink: 0;
}

.wordmark {
  font-family: Georgia, 'Times New Roman', serif;
  font-size: 1.45rem;
  letter-spacing: 0.24em;
  text-transform: uppercase;
  /* Gold gradient on the type, matching the monogram it sits beside. */
  background: linear-gradient(180deg, #f6e27a 0%, #d4af37 45%, #b8860b 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  /* Letter-spacing adds a trailing gap; pull it back so the pair looks centred. */
  margin-right: -0.24em;
  white-space: nowrap;
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
    gap: 9px;
  }
  .mark {
    height: 36px;
  }
  .wordmark {
    font-size: 1.12rem;
    letter-spacing: 0.18em;
    margin-right: -0.18em;
  }
}
</style>
