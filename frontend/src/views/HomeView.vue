<script setup lang="ts">
import { onMounted } from 'vue'

import ProductCard from '@/components/ProductCard.vue'
import { useCatalogStore } from '@/stores/catalog'

const catalog = useCatalogStore()

onMounted(() => catalog.loadBestsellers())

const categories = [
  { to: '/shop?grind=filter', label: 'Filter Coffee', blurb: 'Ground for the decoction' },
  { to: '/shop?grind=whole_bean', label: 'Whole Bean', blurb: 'Grind it your way' },
  { to: '/shop?grind=instant', label: 'Instant', blurb: 'Café in 30 seconds' },
  { to: '/shop?grind=espresso', label: 'Espresso', blurb: 'Crema, guaranteed' },
]

const promises = [
  { icon: '🌱', title: 'Single-origin sourcing', copy: 'Traceable to the estate.' },
  { icon: '🔥', title: 'Roasted to order', copy: 'Shipped within 48 hours of roasting.' },
  { icon: '🚚', title: 'Free shipping over ₹599', copy: 'Delivered across India.' },
]
</script>

<template>
  <section class="hero">
    <div class="container hero-inner">
      <p class="eyebrow">Small-batch · South Indian estates</p>
      <h1>Coffee worth<br />waking up for.</h1>
      <p class="lede">
        Single-origin Arabica and considered blends, roasted in small batches and
        ground the way you actually brew.
      </p>
      <div class="cta">
        <RouterLink to="/shop" class="btn btn-primary">Shop all coffee</RouterLink>
        <RouterLink to="/shop?grind=instant" class="btn btn-outline light">
          Try instant
        </RouterLink>
      </div>
    </div>
  </section>

  <section class="container categories">
    <RouterLink v-for="cat in categories" :key="cat.to" :to="cat.to" class="cat">
      <h3>{{ cat.label }}</h3>
      <p>{{ cat.blurb }}</p>
    </RouterLink>
  </section>

  <section class="container block">
    <header class="block-head">
      <div>
        <h2>Bestsellers</h2>
        <p class="page-subtitle">What our regulars keep reordering.</p>
      </div>
      <RouterLink to="/shop" class="see-all">See all →</RouterLink>
    </header>

    <div v-if="catalog.bestsellersLoading" class="grid">
      <div v-for="n in 4" :key="n" class="skeleton card-skeleton"></div>
    </div>

    <p v-else-if="!catalog.bestsellers.length" class="notice">
      Nothing to show yet — make sure the API is running and the catalog is seeded.
    </p>

    <div v-else class="grid">
      <ProductCard
        v-for="product in catalog.bestsellers"
        :key="product.id"
        :product="product"
      />
    </div>
  </section>

  <section class="promises">
    <div class="container promise-grid">
      <div v-for="p in promises" :key="p.title" class="promise">
        <span class="icon" aria-hidden="true">{{ p.icon }}</span>
        <h4>{{ p.title }}</h4>
        <p>{{ p.copy }}</p>
      </div>
    </div>
  </section>
</template>

<style scoped>
.hero {
  background: linear-gradient(165deg, #0d0b09 0%, #1c1713 55%, #241d16 100%);
  color: var(--crema-light);
  padding: 84px 0 92px;
}

.eyebrow {
  margin: 0 0 14px;
  font-size: 0.78rem;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: var(--gold);
  font-weight: 600;
}

.hero h1 {
  /* Gold gradient on the headline, echoing the mark. */
  background: linear-gradient(180deg, #f6e27a 0%, #d4af37 45%, #b8860b 100%);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  font-size: clamp(2.3rem, 5.5vw, 3.7rem);
  margin: 0 0 20px;
}

.lede {
  max-width: 46ch;
  font-size: 1.04rem;
  line-height: 1.65;
  color: var(--crema-light);
  margin: 0 0 32px;
}

.cta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.btn-outline.light {
  color: var(--gold-light);
  border-color: rgba(212, 175, 55, 0.45);
}

.btn-outline.light:hover {
  background: rgba(212, 175, 55, 0.12);
  border-color: var(--gold);
}

.categories {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-top: -36px;
  position: relative;
  z-index: 1;
}

.cat {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 22px;
  box-shadow: var(--shadow-sm);
  transition: transform 0.15s, box-shadow 0.15s;
}

.cat:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow);
}

.cat h3 {
  font-size: 1.02rem;
  margin: 0 0 5px;
}

.cat p {
  margin: 0;
  font-size: 0.84rem;
  color: var(--ink-soft);
}

.block {
  padding: 64px 20px 0;
}

.block-head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 24px;
}

.block-head h2 {
  font-size: 1.75rem;
  margin: 0 0 4px;
}

.block-head .page-subtitle {
  margin: 0;
}

.see-all {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--accent);
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  min-height: 44px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.card-skeleton {
  height: 340px;
}

.promises {
  margin-top: 72px;
  background: var(--paper);
  border-top: 1px solid var(--line);
  border-bottom: 1px solid var(--line);
  padding: 48px 0;
}

.promise-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
  text-align: center;
}

.icon {
  font-size: 1.7rem;
}

.promise h4 {
  margin: 12px 0 6px;
  font-size: 1rem;
}

.promise p {
  margin: 0;
  color: var(--ink-soft);
  font-size: 0.88rem;
}

@media (max-width: 900px) {
  .categories,
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .promise-grid {
    grid-template-columns: 1fr;
    gap: 26px;
  }
}

@media (max-width: 520px) {
  .hero {
    padding: 56px 0 68px;
  }
  .categories,
  .grid {
    grid-template-columns: 1fr;
  }
  .cta .btn {
    width: 100%;
  }
}
</style>
