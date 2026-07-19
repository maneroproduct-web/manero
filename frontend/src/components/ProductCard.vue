<script setup lang="ts">
import { computed } from 'vue'

import type { Product } from '@/api/types'
import { formatInr, formatWeight } from '@/utils/money'

const props = defineProps<{ product: Product }>()

/** The card advertises the cheapest size, matching how the grid is sorted. */
const leadVariant = computed(() =>
  props.product.variants.reduce(
    (cheapest, v) => (v.price_paise < cheapest.price_paise ? v : cheapest),
    props.product.variants[0],
  ),
)

const anyInStock = computed(() => props.product.variants.some((v) => v.in_stock))
</script>

<template>
  <RouterLink :to="`/shop/${product.slug}`" class="card">
    <div class="media">
      <img :src="product.image_url" :alt="product.name" loading="lazy" />
      <span v-if="!anyInStock" class="badge sold-out">Sold out</span>
      <span
        v-else-if="leadVariant?.discount_percent"
        class="badge badge-sale discount"
      >
        {{ leadVariant.discount_percent }}% off
      </span>
      <span v-else-if="product.is_bestseller" class="badge badge-best discount">
        Bestseller
      </span>
    </div>

    <div class="body">
      <p class="meta">{{ product.origin }}</p>
      <h3 class="name">{{ product.name }}</h3>
      <p class="notes">{{ product.tasting_notes }}</p>

      <div class="price-row" v-if="leadVariant">
        <span class="price">{{ formatInr(leadVariant.price_paise) }}</span>
        <span v-if="leadVariant.compare_at_price_paise" class="was">
          {{ formatInr(leadVariant.compare_at_price_paise) }}
        </span>
        <span class="size">/ {{ formatWeight(leadVariant.size_grams) }}</span>
      </div>
    </div>
  </RouterLink>
</template>

<style scoped>
.card {
  display: flex;
  flex-direction: column;
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: transform 0.16s, box-shadow 0.16s;
  height: 100%;
}

.card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow);
}

.media {
  position: relative;
  aspect-ratio: 4 / 3;
  background: var(--foam);
  /* Don't let the flex row's stretched height feed back into this box. */
  flex: 0 0 auto;
}

/* Absolutely positioned so the image's intrinsic ratio can't influence
   .media's height. Left in flow with height:100%, the two sizes depend on each
   other, the cycle resolves in the image's favour, and every card ends up a
   different height. */
.media img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.discount,
.sold-out {
  position: absolute;
  top: 12px;
  left: 12px;
}

.sold-out {
  background: var(--ink-soft);
  color: #fff;
}

.body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.meta {
  margin: 0 0 6px;
  font-size: 0.74rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--crema);
  font-weight: 600;
}

.name {
  font-size: 1.03rem;
  margin: 0 0 8px;
  line-height: 1.3;
}

.notes {
  margin: 0 0 16px;
  font-size: 0.85rem;
  color: var(--ink-soft);
  line-height: 1.5;
  flex: 1;
}

.price-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
  flex-wrap: wrap;
}

.price {
  font-weight: 700;
  font-size: 1.06rem;
  color: var(--espresso);
}

.was {
  font-size: 0.85rem;
  color: var(--ink-soft);
  text-decoration: line-through;
}

.size {
  font-size: 0.8rem;
  color: var(--ink-soft);
}
</style>
