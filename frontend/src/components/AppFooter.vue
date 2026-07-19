<script setup lang="ts">
import { BRAND_NAME, BRAND_TAGLINE, logoUrl } from '@/assets/logo'
import SocialLinks from '@/components/SocialLinks.vue'
// Statutory identifiers — see content/business.ts. Placeholders until replaced.
import { business, identifiers } from '@/content/business'

const year = new Date().getFullYear()

/** Legal pages, shown along the bottom bar. */
const legalLinks = [
  { to: '/policies/terms', label: 'Terms of Service' },
  { to: '/policies/privacy', label: 'Privacy Policy' },
  { to: '/policies/shipping', label: 'Shipping Policy' },
  { to: '/policies/refunds', label: 'Cancellation & Refunds' },
]

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
      { to: '/shop?roast_level=dark', label: 'Dark Roast' },
      { to: '/shop?sort=price_asc', label: 'Best Value' },
    ],
  },
  {
    title: 'Manero',
    links: [
      { to: '/story', label: 'Our Story' },
      { to: '/contact', label: 'Contact Us' },
      { to: '/contact', label: 'Wholesale' },
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
        <SocialLinks />
      </div>

      <div v-for="col in columns" :key="col.title" class="col">
        <h4>{{ col.title }}</h4>
        <RouterLink v-for="link in col.links" :key="link.to" :to="link.to">
          {{ link.label }}
        </RouterLink>
      </div>
    </div>

    <div class="container compliance">
      <p class="entity">
        {{ business.legalName }} · {{ business.address.line1 }},
        {{ business.address.line2 }}
      </p>
      <dl class="ids">
        <div v-for="row in identifiers" :key="row.label" class="id">
          <dt>{{ row.label }}</dt>
          <dd>{{ row.value }}</dd>
        </div>
      </dl>
    </div>

    <div class="container bottom">
      <p>© {{ year }} {{ BRAND_NAME }}. All rights reserved.</p>
      <nav class="legal" aria-label="Legal">
        <RouterLink v-for="link in legalLinks" :key="link.to" :to="link.to">
          {{ link.label }}
        </RouterLink>
      </nav>
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
  grid-template-columns: 1.6fr repeat(3, 1fr);
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

.compliance {
  margin-top: 36px;
  padding-top: 22px;
  border-top: 1px solid rgba(212, 175, 55, 0.2);
}

.entity {
  margin: 0 0 12px;
  font-size: 0.8rem;
  color: var(--crema);
}

.ids {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 26px;
  margin: 0;
}

.id {
  display: flex;
  align-items: baseline;
  gap: 7px;
}

.id dt {
  font-size: 0.7rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--crema);
  opacity: 0.65;
}

.id dd {
  margin: 0;
  font-size: 0.8rem;
  color: var(--gold-light);
  font-variant-numeric: tabular-nums;
}

.bottom {
  margin-top: 26px;
  padding-top: 20px;
  border-top: 1px solid rgba(212, 175, 55, 0.2);
  font-size: 0.82rem;
  color: var(--crema);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
}

.bottom p {
  margin: 0;
}

.legal {
  display: flex;
  gap: 18px;
  flex-wrap: wrap;
}

.legal a:hover {
  color: var(--gold-light);
}

@media (max-width: 700px) {
  .bottom {
    flex-direction: column;
    align-items: flex-start;
    gap: 14px;
  }
  .legal {
    gap: 8px 18px;
  }
}

@media (max-width: 900px), (pointer: coarse) {
  .legal a {
    padding: 8px 0;
  }
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
