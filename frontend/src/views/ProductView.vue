<script setup lang="ts">
import { computed, ref, watch } from 'vue'

import { api } from '@/api/client'
import type { Product, Variant } from '@/api/types'
import QuantityStepper from '@/components/QuantityStepper.vue'
import VariantSelector from '@/components/VariantSelector.vue'
import { useCartStore } from '@/stores/cart'
import { formatInr } from '@/utils/money'

const props = defineProps<{ slug: string }>()

const cart = useCartStore()

const product = ref<Product | null>(null)
const selected = ref<Variant | null>(null)
const quantity = ref(1)
const loading = ref(true)
const error = ref<string | null>(null)
const added = ref(false)

const attributes = computed(() => {
  if (!product.value) return []
  const p = product.value
  return [
    { label: 'Bean', value: p.bean_type },
    { label: 'Roast', value: p.roast_level },
    { label: 'Grind', value: p.grind.replace('_', ' ') },
    { label: 'Flavour', value: p.flavour },
    { label: 'Origin', value: p.origin },
  ]
})

const maxQuantity = computed(() => Math.max(1, selected.value?.stock_qty ?? 1))
const canAdd = computed(() => Boolean(selected.value?.in_stock) && !cart.loading)

async function load(slug: string) {
  loading.value = true
  error.value = null
  product.value = null
  try {
    const result = await api.getProduct(slug)
    product.value = result
    // Default to the first size that is actually buyable.
    selected.value = result.variants.find((v) => v.in_stock) ?? result.variants[0] ?? null
    quantity.value = 1
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not load this product'
  } finally {
    loading.value = false
  }
}

function selectVariant(variant: Variant) {
  selected.value = variant
  // A smaller pack may not stock what was chosen for a bigger one.
  quantity.value = Math.min(quantity.value, Math.max(1, variant.stock_qty))
}

async function addToCart() {
  if (!selected.value) return
  const ok = await cart.addItem(selected.value.id, quantity.value)
  if (ok) {
    added.value = true
    cart.openDrawer()
    setTimeout(() => (added.value = false), 2000)
  }
}

watch(() => props.slug, load, { immediate: true })
</script>

<template>
  <div class="container page">
    <div v-if="loading" class="layout">
      <div class="skeleton media-skeleton"></div>
      <div>
        <div class="skeleton line lg"></div>
        <div class="skeleton line"></div>
        <div class="skeleton line short"></div>
      </div>
    </div>

    <div v-else-if="error" class="notice notice-error">
      {{ error }}
      <RouterLink to="/shop" class="back">← Back to shop</RouterLink>
    </div>

    <template v-else-if="product">
      <nav class="crumbs" aria-label="Breadcrumb">
        <RouterLink to="/shop">Shop</RouterLink>
        <span aria-hidden="true">/</span>
        <span>{{ product.name }}</span>
      </nav>

      <div class="layout">
        <div class="media">
          <img :src="product.image_url" :alt="product.name" />
        </div>

        <div class="info">
          <p class="origin">{{ product.origin }}</p>
          <h1>{{ product.name }}</h1>
          <p class="notes">{{ product.tasting_notes }}</p>

          <div v-if="selected" class="price-row">
            <span class="price">{{ formatInr(selected.price_paise) }}</span>
            <template v-if="selected.compare_at_price_paise">
              <span class="was">{{ formatInr(selected.compare_at_price_paise) }}</span>
              <span class="badge badge-sale">{{ selected.discount_percent }}% off</span>
            </template>
          </div>
          <p class="tax-note">Inclusive of all taxes.</p>

          <VariantSelector
            :variants="product.variants"
            :selected-id="selected?.id ?? null"
            @select="selectVariant"
          />

          <p v-if="selected && selected.in_stock && selected.stock_qty <= 5" class="low">
            Only {{ selected.stock_qty }} left.
          </p>

          <div class="buy">
            <QuantityStepper
              v-model="quantity"
              :max="maxQuantity"
              :disabled="!selected?.in_stock"
            />
            <button class="btn btn-primary grow" :disabled="!canAdd" @click="addToCart">
              {{
                !selected?.in_stock
                  ? 'Sold out'
                  : added
                    ? 'Added ✓'
                    : cart.loading
                      ? 'Adding…'
                      : 'Add to cart'
              }}
            </button>
          </div>

          <p v-if="cart.error" class="notice notice-error">{{ cart.error }}</p>

          <div class="description">
            <h2>About this coffee</h2>
            <p>{{ product.description }}</p>
          </div>

          <dl class="attrs">
            <div v-for="attr in attributes" :key="attr.label" class="attr">
              <dt>{{ attr.label }}</dt>
              <dd>{{ attr.value }}</dd>
            </div>
          </dl>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.crumbs {
  display: flex;
  gap: 8px;
  font-size: 0.84rem;
  color: var(--ink-soft);
  margin-bottom: 22px;
}

.crumbs a:hover {
  color: var(--accent);
}

.layout {
  display: grid;
  /* minmax(0, …) so both columns can shrink — see CheckoutView. */
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 48px;
  align-items: start;
}

.media {
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--paper);
  border: 1px solid var(--line);
  position: sticky;
  top: calc(var(--header-h) + 20px);
}

.media img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
}

.origin {
  margin: 0 0 8px;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--crema);
  font-weight: 600;
}

.info h1 {
  font-size: 2rem;
  margin: 0 0 10px;
}

.notes {
  margin: 0 0 22px;
  color: var(--ink-soft);
  font-size: 0.98rem;
  line-height: 1.6;
}

.price-row {
  display: flex;
  align-items: baseline;
  gap: 11px;
  flex-wrap: wrap;
}

.price {
  font-size: 1.65rem;
  font-weight: 700;
  color: var(--espresso);
}

.was {
  color: var(--ink-soft);
  text-decoration: line-through;
}

.tax-note {
  margin: 4px 0 24px;
  font-size: 0.8rem;
  color: var(--ink-soft);
}

.low {
  margin: 14px 0 0;
  font-size: 0.85rem;
  color: var(--accent);
  font-weight: 600;
}

.buy {
  display: flex;
  gap: 12px;
  margin: 24px 0 0;
  align-items: center;
}

.grow {
  flex: 1;
}

.description {
  margin-top: 36px;
  padding-top: 28px;
  border-top: 1px solid var(--line);
}

.description h2 {
  font-size: 1.1rem;
}

.description p {
  color: var(--ink-soft);
  line-height: 1.7;
  margin: 0;
}

.attrs {
  margin: 28px 0 0;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1px;
  background: var(--line);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  overflow: hidden;
}

.attr {
  background: var(--paper);
  padding: 12px 14px;
}

.attr dt {
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--ink-soft);
  font-weight: 700;
}

.attr dd {
  margin: 4px 0 0;
  font-size: 0.9rem;
  text-transform: capitalize;
}

.media-skeleton {
  aspect-ratio: 1;
}

.line {
  height: 20px;
  margin-bottom: 14px;
}

.line.lg {
  height: 38px;
}

.line.short {
  width: 55%;
}

.back {
  display: block;
  margin-top: 12px;
  font-weight: 600;
  text-decoration: underline;
}

@media (max-width: 900px) {
  .layout {
    grid-template-columns: 1fr;
    gap: 28px;
  }
  .media {
    position: static;
  }
}

@media (max-width: 480px) {
  .buy {
    flex-wrap: wrap;
  }
  .grow {
    width: 100%;
    flex: none;
  }
}
</style>
