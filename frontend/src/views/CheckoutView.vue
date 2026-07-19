<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { api } from '@/api/client'
import type { PaymentCallback } from '@/api/types'
import { useCartStore } from '@/stores/cart'
import { formatInr, formatWeight } from '@/utils/money'
import { startPayment } from '@/utils/payment'

const cart = useCartStore()
const router = useRouter()

const form = reactive({
  email: '',
  phone: '',
  name: '',
  line1: '',
  line2: '',
  city: '',
  state: '',
  pincode: '',
})

type FieldName = keyof typeof form
const errors = reactive<Partial<Record<FieldName, string>>>({})
const submitting = ref(false)
const paymentError = ref<string | null>(null)

const STATES = [
  'Andhra Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Delhi', 'Goa', 'Gujarat',
  'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala',
  'Madhya Pradesh', 'Maharashtra', 'Odisha', 'Punjab', 'Rajasthan', 'Tamil Nadu',
  'Telangana', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
]

onMounted(async () => {
  await cart.refresh()
  if (cart.isEmpty) router.replace('/cart')
})

const totals = computed(() => cart.cart)

/** Client-side validation mirrors the Pydantic rules; the server re-checks. */
function validate(): boolean {
  for (const key of Object.keys(errors) as FieldName[]) delete errors[key]

  if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(form.email)) {
    errors.email = 'Enter a valid email address'
  }
  if (!/^\d{10}$/.test(form.phone.replace(/^\+91/, '').trim())) {
    errors.phone = 'Enter a 10-digit mobile number'
  }
  if (form.name.trim().length < 2) errors.name = 'Enter the recipient name'
  if (form.line1.trim().length < 3) errors.line1 = 'Enter the street address'
  if (form.city.trim().length < 2) errors.city = 'Enter the city'
  if (!form.state) errors.state = 'Select a state'
  if (!/^\d{6}$/.test(form.pincode)) errors.pincode = 'Enter a 6-digit pincode'

  return Object.keys(errors).length === 0
}

async function onPaymentCallback(callback: PaymentCallback, orderNumber: string) {
  try {
    await api.verifyPayment(callback)
    // Server has already emptied this cart; drop the local token too.
    cart.reset()
    router.push(`/order/${orderNumber}`)
  } catch (err) {
    const reason = err instanceof Error ? err.message : 'Payment verification failed'
    paymentError.value =
      `${reason.replace(/\.?$/, '.')} ` +
      `If you were charged, contact us with order ${orderNumber}.`
  } finally {
    submitting.value = false
  }
}

async function submit() {
  paymentError.value = null
  if (!validate() || !cart.token) return

  submitting.value = true
  try {
    const order = await api.createOrder({
      cart_token: cart.token,
      email: form.email.trim(),
      phone: form.phone.replace(/^\+91/, '').trim(),
      shipping: {
        name: form.name.trim(),
        line1: form.line1.trim(),
        line2: form.line2.trim(),
        city: form.city.trim(),
        state: form.state,
        pincode: form.pincode,
      },
    })

    // Which gateway opens is decided by the backend; this view doesn't care.
    await startPayment(order, {
      onCallback: (callback) => onPaymentCallback(callback, order.order_number),
      // Closing the gateway is not a failure — let them try again.
      onDismiss: () => {
        submitting.value = false
      },
    })
  } catch (err) {
    paymentError.value = err instanceof Error ? err.message : 'Could not start payment.'
    submitting.value = false
  }
}
</script>

<template>
  <div class="container page">
    <h1 class="page-title">Checkout</h1>
    <p class="page-subtitle">No account needed — just where to send the coffee.</p>

    <p v-if="paymentError" class="notice notice-error">{{ paymentError }}</p>

    <form class="layout" novalidate @submit.prevent="submit">
      <section class="panel">
        <h2>Contact</h2>
        <div class="field">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="form.email"
            type="email"
            autocomplete="email"
            placeholder="you@example.com"
            :aria-invalid="Boolean(errors.email)"
          />
          <span v-if="errors.email" class="field-error">{{ errors.email }}</span>
        </div>
        <div class="field">
          <label for="phone">Mobile number</label>
          <input
            id="phone"
            v-model="form.phone"
            type="tel"
            autocomplete="tel"
            placeholder="9876543210"
            :aria-invalid="Boolean(errors.phone)"
          />
          <span v-if="errors.phone" class="field-error">{{ errors.phone }}</span>
        </div>

        <h2 class="mt">Shipping address</h2>
        <div class="field">
          <label for="name">Full name</label>
          <input
            id="name"
            v-model="form.name"
            autocomplete="name"
            :aria-invalid="Boolean(errors.name)"
          />
          <span v-if="errors.name" class="field-error">{{ errors.name }}</span>
        </div>
        <div class="field">
          <label for="line1">Address</label>
          <input
            id="line1"
            v-model="form.line1"
            autocomplete="address-line1"
            placeholder="Flat / house no., street"
            :aria-invalid="Boolean(errors.line1)"
          />
          <span v-if="errors.line1" class="field-error">{{ errors.line1 }}</span>
        </div>
        <div class="field">
          <label for="line2">Apartment, landmark (optional)</label>
          <input id="line2" v-model="form.line2" autocomplete="address-line2" />
        </div>

        <div class="row-3">
          <div class="field">
            <label for="city">City</label>
            <input
              id="city"
              v-model="form.city"
              autocomplete="address-level2"
              :aria-invalid="Boolean(errors.city)"
            />
            <span v-if="errors.city" class="field-error">{{ errors.city }}</span>
          </div>
          <div class="field">
            <label for="state">State</label>
            <select id="state" v-model="form.state" :aria-invalid="Boolean(errors.state)">
              <option value="">Select</option>
              <option v-for="s in STATES" :key="s" :value="s">{{ s }}</option>
            </select>
            <span v-if="errors.state" class="field-error">{{ errors.state }}</span>
          </div>
          <div class="field">
            <label for="pincode">Pincode</label>
            <input
              id="pincode"
              v-model="form.pincode"
              inputmode="numeric"
              maxlength="6"
              autocomplete="postal-code"
              :aria-invalid="Boolean(errors.pincode)"
            />
            <span v-if="errors.pincode" class="field-error">{{ errors.pincode }}</span>
          </div>
        </div>
      </section>

      <aside class="panel summary">
        <h2>Your order</h2>

        <ul class="lines">
          <li v-for="item in cart.items" :key="item.id">
            <img :src="item.image_url" :alt="item.product_name" />
            <div>
              <p class="l-name">{{ item.product_name }}</p>
              <p class="l-meta">
                {{ formatWeight(item.size_grams) }} × {{ item.quantity }}
              </p>
            </div>
            <span class="l-total">{{ formatInr(item.line_total_paise) }}</span>
          </li>
        </ul>

        <div class="row">
          <span>Subtotal</span>
          <span>{{ formatInr(totals?.subtotal_paise ?? 0) }}</span>
        </div>
        <div class="row">
          <span>Shipping</span>
          <span>
            {{ totals?.shipping_paise ? formatInr(totals.shipping_paise) : 'Free' }}
          </span>
        </div>
        <div class="row total">
          <span>Total</span>
          <strong>{{ formatInr(totals?.total_paise ?? 0) }}</strong>
        </div>

        <button type="submit" class="btn btn-primary btn-block" :disabled="submitting">
          {{ submitting ? 'Opening payment…' : `Pay ${formatInr(totals?.total_paise ?? 0)}` }}
        </button>

        <!-- Deliberately doesn't name a gateway: which one runs is a backend
             setting, so hardcoding "Razorpay" here can silently become a lie. -->
        <p class="secure">
          🔒 Payments are processed by our secure payment provider. Card details
          never touch our servers.
        </p>
      </aside>
    </form>
  </div>
</template>

<style scoped>
.layout {
  display: grid;
  /* minmax(0, 1fr), not 1fr: a bare 1fr track refuses to shrink below its
     content's min-content width, so between the breakpoints the two columns
     add up to more than the container and the page scrolls sideways. */
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 28px;
  align-items: start;
}

.panel {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 24px;
}

.panel h2 {
  font-size: 1.08rem;
  margin: 0 0 18px;
}

.panel h2.mt {
  margin-top: 30px;
  padding-top: 24px;
  border-top: 1px solid var(--line);
}

.row-3 {
  display: grid;
  grid-template-columns: 1fr 1fr 140px;
  gap: 14px;
}

.summary {
  position: sticky;
  top: calc(var(--header-h) + 20px);
}

.lines {
  list-style: none;
  margin: 0 0 18px;
  padding: 0 0 16px;
  border-bottom: 1px solid var(--line);
}

.lines li {
  display: grid;
  grid-template-columns: 48px 1fr auto;
  gap: 12px;
  align-items: center;
  padding: 8px 0;
}

.lines img {
  width: 48px;
  height: 48px;
  object-fit: cover;
  border-radius: 8px;
  background: var(--foam);
}

.l-name {
  margin: 0;
  font-size: 0.87rem;
  font-weight: 600;
  line-height: 1.3;
}

.l-meta {
  margin: 2px 0 0;
  font-size: 0.78rem;
  color: var(--ink-soft);
}

.l-total {
  font-size: 0.87rem;
  font-weight: 600;
  white-space: nowrap;
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
  padding-top: 13px;
  border-top: 1px solid var(--line);
  color: var(--ink);
  font-size: 1.07rem;
}

.summary .btn {
  margin-top: 16px;
}

.secure {
  margin: 14px 0 0;
  font-size: 0.76rem;
  color: var(--ink-soft);
  text-align: center;
  line-height: 1.5;
}

@media (max-width: 940px) {
  .layout {
    grid-template-columns: 1fr;
  }
  .summary {
    position: static;
    order: -1;
  }
}

@media (max-width: 520px) {
  .row-3 {
    grid-template-columns: 1fr;
  }
}
</style>
