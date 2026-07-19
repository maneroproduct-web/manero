<script setup lang="ts">
import { ref, watch } from 'vue'

import { api } from '@/api/client'
import type { Order } from '@/api/types'
import { formatInr, formatWeight } from '@/utils/money'

const props = defineProps<{ orderNumber: string }>()

const order = ref<Order | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)

async function load(orderNumber: string) {
  loading.value = true
  error.value = null
  try {
    order.value = await api.getOrder(orderNumber)
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not load this order'
  } finally {
    loading.value = false
  }
}

watch(() => props.orderNumber, load, { immediate: true })
</script>

<template>
  <div class="container page narrow">
    <div v-if="loading" class="skeleton block"></div>

    <p v-else-if="error" class="notice notice-error">{{ error }}</p>

    <template v-else-if="order">
      <div class="hero" :class="{ pending: order.status !== 'paid' }">
        <p class="mark" aria-hidden="true">{{ order.status === 'paid' ? '✓' : '⏳' }}</p>
        <h1>
          {{ order.status === 'paid' ? 'Order confirmed' : 'Payment pending' }}
        </h1>
        <p class="sub">
          <!-- Says only what is true. Nothing sends email yet, so promising a
               receipt would be a lie to someone who has just paid. If you add
               transactional email, change this back to mention it. -->
          <template v-if="order.status === 'paid'">
            Thanks — your order is confirmed. Please keep your order number
            below; quote it in any email to us about this order.
          </template>
          <template v-else>
            We haven't received confirmation for this payment yet. If you were
            charged, it will settle shortly.
          </template>
        </p>
        <p class="number">
          Order <strong>{{ order.order_number }}</strong>
        </p>
      </div>

      <section class="panel">
        <h2>What's coming</h2>
        <ul class="lines">
          <li v-for="(item, i) in order.items" :key="i">
            <div>
              <p class="l-name">{{ item.product_name }}</p>
              <p class="l-meta">
                {{ formatWeight(item.size_grams) }} × {{ item.quantity }}
              </p>
            </div>
            <span>{{ formatInr(item.line_total_paise) }}</span>
          </li>
        </ul>

        <div class="row">
          <span>Subtotal</span>
          <span>{{ formatInr(order.subtotal_paise) }}</span>
        </div>
        <div class="row">
          <span>Shipping</span>
          <span>{{ order.shipping_paise ? formatInr(order.shipping_paise) : 'Free' }}</span>
        </div>
        <div class="row total">
          <span>Total paid</span>
          <strong>{{ formatInr(order.total_paise) }}</strong>
        </div>
      </section>

      <section class="panel">
        <h2>Shipping to</h2>
        <address>
          {{ order.shipping_name }}<br />
          {{ order.shipping_line1 }}<br />
          <template v-if="order.shipping_line2">
            {{ order.shipping_line2 }}<br />
          </template>
          {{ order.shipping_city }}, {{ order.shipping_state }}
          {{ order.shipping_pincode }}
        </address>
      </section>

      <RouterLink to="/shop" class="btn btn-dark btn-block">
        Continue shopping
      </RouterLink>
    </template>
  </div>
</template>

<style scoped>
.narrow {
  max-width: 640px;
}

.hero {
  text-align: center;
  padding: 40px 24px;
  background: #e9f3ed;
  border: 1px solid #c5e0d1;
  border-radius: var(--radius-lg);
  margin-bottom: 20px;
}

.hero.pending {
  background: #fdf6e8;
  border-color: #ecd9ab;
}

.mark {
  width: 52px;
  height: 52px;
  margin: 0 auto 14px;
  border-radius: 50%;
  background: var(--success);
  color: #fff;
  font-size: 1.5rem;
  display: grid;
  place-items: center;
}

.hero.pending .mark {
  background: #c08a2e;
}

.hero h1 {
  font-size: 1.6rem;
  margin: 0 0 8px;
}

.sub {
  margin: 0 0 14px;
  color: var(--ink-soft);
  line-height: 1.6;
}

.number {
  margin: 0;
  font-size: 0.88rem;
  color: var(--ink-soft);
}

.panel {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 22px;
  margin-bottom: 16px;
}

.panel h2 {
  font-size: 1.05rem;
  margin: 0 0 16px;
}

.lines {
  list-style: none;
  margin: 0 0 16px;
  padding: 0 0 14px;
  border-bottom: 1px solid var(--line);
}

.lines li {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  padding: 8px 0;
  font-size: 0.9rem;
}

.l-name {
  margin: 0;
  font-weight: 600;
}

.l-meta {
  margin: 2px 0 0;
  font-size: 0.8rem;
  color: var(--ink-soft);
}

.row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  font-size: 0.9rem;
  color: var(--ink-soft);
}

.row.total {
  margin-top: 8px;
  padding-top: 12px;
  border-top: 1px solid var(--line);
  color: var(--ink);
  font-size: 1.05rem;
}

address {
  font-style: normal;
  line-height: 1.7;
  color: var(--ink-soft);
}

.block {
  height: 280px;
}
</style>
