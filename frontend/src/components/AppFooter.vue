<script setup lang="ts">
import { BRAND_NAME, BRAND_TAGLINE, logoUrl } from '@/assets/logo'

const year = new Date().getFullYear()

const columns = [
  {
    title: 'Shop',
    links: [
      { to: '/shop', label: 'All Coffee' },
      { to: '/shop?grind=filter', label: 'Filter Coffee' },
      { to: '/shop?grind=instant', label: 'Instant Coffee' },
      { to: '/shop?grind=whole_bean', label: 'Whole Bean' },
    ],
  },
  {
    title: 'Explore',
    links: [
      { to: '/shop?bean_type=arabica', label: 'Arabica' },
      { to: '/shop?bean_type=robusta', label: 'Robusta' },
      { to: '/shop?roast_level=dark', label: 'Dark Roast' },
      { to: '/shop?sort=price_asc', label: 'Best Value' },
    ],
  },
]
</script>

<template>
  <footer class="footer">
    <div class="container inner">
      <div class="about">
        <img :src="logoUrl" :alt="BRAND_NAME" class="logo" />
        <p class="tagline">{{ BRAND_TAGLINE }}</p>
      </div>

      <div v-for="col in columns" :key="col.title" class="col">
        <h4>{{ col.title }}</h4>
        <RouterLink v-for="link in col.links" :key="link.to" :to="link.to">
          {{ link.label }}
        </RouterLink>
      </div>
    </div>

    <div class="container bottom">
      <p>© {{ year }} {{ BRAND_NAME }}. All rights reserved.</p>
    </div>
  </footer>
</template>

<style scoped>
.footer {
  background: var(--espresso);
  color: var(--crema-light);
  padding: 48px 0 24px;
  margin-top: 64px;
}

.inner {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 40px;
}

.logo {
  height: 92px;
  width: auto;
}

.tagline {
  margin-top: 14px;
  color: var(--crema);
  font-size: 0.9rem;
  max-width: 34ch;
  line-height: 1.6;
}

.col h4 {
  color: var(--gold-light);
  font-size: 0.95rem;
  margin-bottom: 14px;
}

.col a {
  display: block;
  padding: 5px 0;
  font-size: 0.88rem;
  color: var(--crema);
}

.col a:hover {
  color: var(--gold-light);
}

.bottom {
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid rgba(212, 175, 55, 0.2);
  font-size: 0.82rem;
  color: var(--crema);
}

.bottom p {
  margin: 0;
}

/* Roomier tap targets on touch devices and narrow screens. */
@media (max-width: 900px), (pointer: coarse) {
  .col a {
    padding: 14px 0;
  }
}

@media (max-width: 720px) {
  .inner {
    grid-template-columns: 1fr 1fr;
    gap: 28px;
  }
  .about {
    grid-column: 1 / -1;
  }
}
</style>
