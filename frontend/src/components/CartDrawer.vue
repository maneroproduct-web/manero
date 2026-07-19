<script setup lang="ts">
import { nextTick, onBeforeUnmount, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import QuantityStepper from '@/components/QuantityStepper.vue'
import { useCartStore } from '@/stores/cart'
import { formatInr, formatWeight } from '@/utils/money'

const cart = useCartStore()
const router = useRouter()

const panel = ref<HTMLElement | null>(null)

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Escape') cart.closeDrawer()
}

watch(
  () => cart.drawerOpen,
  async (open) => {
    // Stop the page behind the drawer from scrolling while it is open.
    document.body.style.overflow = open ? 'hidden' : ''

    if (open) {
      // Listen on the document: Escape must work wherever focus happens to be.
      document.addEventListener('keydown', onKeydown)
      await nextTick()
      panel.value?.focus()
    } else {
      document.removeEventListener('keydown', onKeydown)
    }
  },
)

onBeforeUnmount(() => {
  document.removeEventListener('keydown', onKeydown)
  document.body.style.overflow = ''
})

function goTo(path: string) {
  cart.closeDrawer()
  router.push(path)
}
</script>

<template>
  <Teleport to="body">
    <div v-if="cart.drawerOpen" class="overlay" @click.self="cart.closeDrawer()">
      <aside
        ref="panel"
        class="drawer"
        role="dialog"
        aria-modal="true"
        aria-label="Shopping cart"
        tabindex="-1"
      >
        <header class="head">
          <h2>Your cart</h2>
          <button class="close" aria-label="Close cart" @click="cart.closeDrawer()">
            ✕
          </button>
        </header>

        <p v-if="cart.error" class="notice notice-error m">{{ cart.error }}</p>

        <div v-if="cart.isEmpty" class="empty">
          <p class="empty-icon" aria-hidden="true">☕</p>
          <p>Your cart is empty.</p>
          <button class="btn btn-dark" @click="goTo('/shop')">Browse coffee</button>
        </div>

        <template v-else>
          <p v-if="cart.amountToFreeShipping > 0" class="ship-hint">
            Add <strong>{{ formatInr(cart.amountToFreeShipping) }}</strong> more for free
            shipping.
          </p>
          <p v-else class="ship-hint free">You've unlocked free shipping.</p>

          <ul class="items">
            <li v-for="item in cart.items" :key="item.id" class="item">
              <img :src="item.image_url" :alt="item.product_name" />
              <div class="detail">
                <p class="name">{{ item.product_name }}</p>
                <p class="size">{{ formatWeight(item.size_grams) }}</p>
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

          <footer class="foot">
            <div class="row">
              <span>Subtotal</span>
              <strong>{{ formatInr(cart.cart?.subtotal_paise ?? 0) }}</strong>
            </div>
            <div class="row muted">
              <span>Shipping</span>
              <span>
                {{
                  cart.cart?.shipping_paise
                    ? formatInr(cart.cart.shipping_paise)
                    : 'Free'
                }}
              </span>
            </div>
            <div class="row total">
              <span>Total</span>
              <strong>{{ formatInr(cart.cart?.total_paise ?? 0) }}</strong>
            </div>
            <button class="btn btn-primary btn-block" @click="goTo('/checkout')">
              Checkout
            </button>
            <button class="btn btn-outline btn-block" @click="goTo('/cart')">
              View full cart
            </button>
          </footer>
        </template>
      </aside>
    </div>
  </Teleport>
</template>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(28, 19, 16, 0.45);
  z-index: 100;
  display: flex;
  justify-content: flex-end;
}

.drawer {
  outline: none;
  width: min(420px, 100%);
  background: var(--foam);
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-lg);
}

.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px;
  border-bottom: 1px solid var(--line);
  background: var(--paper);
}

.head h2 {
  margin: 0;
  font-size: 1.15rem;
}

.close {
  background: none;
  border: none;
  font-size: 1.05rem;
  padding: 4px 8px;
}

.m {
  margin: 16px 20px 0;
}

.empty {
  flex: 1;
  display: grid;
  place-content: center;
  justify-items: center;
  gap: 14px;
  padding: 40px;
  text-align: center;
  color: var(--ink-soft);
}

.empty-icon {
  font-size: 2.4rem;
  margin: 0;
}

.ship-hint {
  margin: 0;
  padding: 12px 20px;
  font-size: 0.85rem;
  background: var(--crema-light);
  color: var(--roast);
}

.ship-hint.free {
  background: #e6f2eb;
  color: var(--success);
}

.items {
  list-style: none;
  margin: 0;
  padding: 0;
  flex: 1;
  overflow-y: auto;
}

.item {
  display: grid;
  grid-template-columns: 68px 1fr auto;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--line);
}

.item img {
  width: 68px;
  height: 68px;
  object-fit: cover;
  border-radius: var(--radius);
  background: var(--line);
}

.detail {
  min-width: 0;
}

.name {
  margin: 0 0 3px;
  font-weight: 600;
  font-size: 0.9rem;
  line-height: 1.35;
}

.size {
  margin: 0 0 9px;
  font-size: 0.8rem;
  color: var(--ink-soft);
}

.controls {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.remove {
  background: none;
  border: none;
  padding: 0;
  font-size: 0.78rem;
  color: var(--ink-soft);
  text-decoration: underline;
}

.remove:hover {
  color: var(--danger);
}

.line-total {
  margin: 0;
  font-weight: 700;
  font-size: 0.9rem;
  white-space: nowrap;
}

.foot {
  padding: 20px;
  background: var(--paper);
  border-top: 1px solid var(--line);
  display: flex;
  flex-direction: column;
  gap: 9px;
}

.row {
  display: flex;
  justify-content: space-between;
  font-size: 0.9rem;
}

.row.muted {
  color: var(--ink-soft);
}

.row.total {
  padding-top: 9px;
  border-top: 1px solid var(--line);
  font-size: 1.05rem;
}

.foot .btn {
  margin-top: 4px;
}
</style>
