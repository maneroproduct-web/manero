<script setup lang="ts">
import { onMounted } from 'vue'

import QuantityStepper from '@/components/QuantityStepper.vue'
import { useCartStore } from '@/stores/cart'
import { formatInr, formatWeight } from '@/utils/money'

const cart = useCartStore()

// Stock may have moved since the cart was filled; re-read on landing.
onMounted(() => cart.refresh())
</script>

<template>
  <div class="container page">
    <h1 class="page-title">Your cart</h1>
    <p class="page-subtitle">
      {{ cart.itemCount }} item{{ cart.itemCount === 1 ? '' : 's' }}
    </p>

    <p v-if="cart.error" class="notice notice-error">{{ cart.error }}</p>

    <div v-if="cart.isEmpty" class="empty">
      <p class="empty-icon" aria-hidden="true">☕</p>
      <h3>Your cart is empty</h3>
      <p>Pick a bag and it'll show up here.</p>
      <RouterLink to="/shop" class="btn btn-dark">Browse coffee</RouterLink>
    </div>

    <div v-else class="layout">
      <ul class="items">
        <li v-for="item in cart.items" :key="item.id" class="item">
          <RouterLink :to="`/shop/${item.product_slug}`" class="thumb">
            <img :src="item.image_url" :alt="item.product_name" />
          </RouterLink>

          <div class="detail">
            <RouterLink :to="`/shop/${item.product_slug}`" class="name">
              {{ item.product_name }}
            </RouterLink>
            <p class="size">
              {{ formatWeight(item.size_grams) }} ·
              {{ formatInr(item.unit_price_paise) }} each
            </p>
            <div class="controls">
              <QuantityStepper
                :model-value="item.quantity"
                :max="item.stock_qty"
                :disabled="cart.loading"
                @update:model-value="cart.updateQuantity(item.id, $event)"
              />
              <button class="remove" @click="cart.removeItem(item.id)">Remove</button>
            </div>
          </div>

          <p class="line-total">{{ formatInr(item.line_total_paise) }}</p>
        </li>
      </ul>

      <aside class="summary">
        <h2>Order summary</h2>

        <div class="row">
          <span>Subtotal</span>
          <span>{{ formatInr(cart.cart?.subtotal_paise ?? 0) }}</span>
        </div>
        <div class="row">
          <span>Shipping</span>
          <span>
            {{
              cart.cart?.shipping_paise ? formatInr(cart.cart.shipping_paise) : 'Free'
            }}
          </span>
        </div>

        <p v-if="cart.amountToFreeShipping > 0" class="hint">
          Add {{ formatInr(cart.amountToFreeShipping) }} more for free shipping.
        </p>

        <div class="row total">
          <span>Total</span>
          <strong>{{ formatInr(cart.cart?.total_paise ?? 0) }}</strong>
        </div>

        <RouterLink to="/checkout" class="btn btn-primary btn-block">
          Proceed to checkout
        </RouterLink>
        <RouterLink to="/shop" class="btn btn-outline btn-block">
          Continue shopping
        </RouterLink>
      </aside>
    </div>
  </div>
</template>

<style scoped>
.layout {
  display: grid;
  /* minmax(0, …) so the flexible column can shrink — see CheckoutView. */
  grid-template-columns: minmax(0, 1fr) 330px;
  gap: 32px;
  align-items: start;
}

.items {
  list-style: none;
  margin: 0;
  padding: 0;
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.item {
  display: grid;
  grid-template-columns: 96px 1fr auto;
  gap: 18px;
  padding: 20px;
  border-bottom: 1px solid var(--line);
}

.item:last-child {
  border-bottom: none;
}

.thumb img {
  width: 96px;
  height: 96px;
  object-fit: cover;
  border-radius: var(--radius);
  background: var(--foam);
}

.name {
  font-weight: 600;
  font-size: 1rem;
  display: block;
  margin-bottom: 5px;
}

.name:hover {
  color: var(--accent);
}

.size {
  margin: 0 0 14px;
  font-size: 0.85rem;
  color: var(--ink-soft);
}

.controls {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}

.remove {
  background: none;
  border: none;
  padding: 0;
  font-size: 0.82rem;
  color: var(--ink-soft);
  text-decoration: underline;
}

.remove:hover {
  color: var(--danger);
}

@media (max-width: 900px), (pointer: coarse) {
  .remove {
    padding: 11px 0;
  }
}

.line-total {
  margin: 0;
  font-weight: 700;
  white-space: nowrap;
}

.summary {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 22px;
  position: sticky;
  top: calc(var(--header-h) + 20px);
}

.summary h2 {
  font-size: 1.1rem;
  margin: 0 0 18px;
}

.row {
  display: flex;
  justify-content: space-between;
  padding: 7px 0;
  font-size: 0.92rem;
  color: var(--ink-soft);
}

.row.total {
  margin-top: 10px;
  padding-top: 14px;
  border-top: 1px solid var(--line);
  color: var(--ink);
  font-size: 1.08rem;
}

.hint {
  margin: 10px 0;
  padding: 9px 11px;
  background: var(--crema-light);
  color: var(--roast);
  border-radius: var(--radius);
  font-size: 0.82rem;
}

.summary .btn {
  margin-top: 10px;
}

.empty {
  text-align: center;
  padding: 72px 20px;
  color: var(--ink-soft);
}

.empty-icon {
  font-size: 2.6rem;
  margin: 0 0 10px;
}

.empty .btn {
  margin-top: 20px;
}

@media (max-width: 900px) {
  .layout {
    grid-template-columns: 1fr;
  }
  .summary {
    position: static;
  }
}

@media (max-width: 520px) {
  .item {
    grid-template-columns: 72px 1fr;
    gap: 14px;
  }
  .thumb img {
    width: 72px;
    height: 72px;
  }
  .line-total {
    grid-column: 2;
  }
}
</style>
