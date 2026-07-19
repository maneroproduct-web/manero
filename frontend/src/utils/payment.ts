/**
 * Payment orchestration.
 *
 * `startPayment` takes the order the backend just created and drives whichever
 * gateway that order was opened against. The checkout view doesn't know or care
 * which one is live — swapping providers is a backend .env change.
 */

import { api } from '@/api/client'
import type { CreateOrderResult, PaymentCallback } from '@/api/types'
import { BRAND_NAME } from '@/assets/logo'
import { loadRazorpay, type RazorpayHandlerResponse } from '@/utils/razorpay'

export interface PaymentHandlers {
  /** The gateway authorised the payment; verify it server-side. */
  onCallback: (callback: PaymentCallback) => void | Promise<void>
  /** The customer closed the gateway without paying. Not an error. */
  onDismiss: () => void
}

/** Resolves once the gateway UI is open. Outcome arrives via the handlers. */
export async function startPayment(
  order: CreateOrderResult,
  handlers: PaymentHandlers,
): Promise<void> {
  if (order.provider === 'dummy') {
    return openDummyPayment(order, handlers)
  }
  return openRazorpayPayment(order, handlers)
}

// --- dummy ----------------------------------------------------------------

/**
 * Stand-in for a hosted gateway page while PAYMENT_PROVIDER=dummy.
 *
 * Resolves the caller's promise as soon as the dialog is on screen; the chosen
 * outcome is delivered through the handlers, matching how a real gateway
 * behaves. The signature is minted server-side by /checkout/dummy-pay — this
 * code never holds a signing secret.
 */
function openDummyPayment(
  order: CreateOrderResult,
  handlers: PaymentHandlers,
): Promise<void> {
  return new Promise((resolve) => {
    const dialog = buildDummyDialog(order, {
      onChoice: async (succeed: boolean) => {
        close()
        try {
          handlers.onCallback(await api.dummyPay(order.provider_order_id, succeed))
        } catch {
          handlers.onDismiss()
        }
      },
      onCancel: () => {
        close()
        handlers.onDismiss()
      },
    })

    function close() {
      document.removeEventListener('keydown', onKey)
      dialog.root.remove()
      document.body.style.overflow = ''
    }

    function onKey(event: KeyboardEvent) {
      if (event.key === 'Escape') {
        close()
        handlers.onDismiss()
      }
    }

    document.addEventListener('keydown', onKey)
    document.body.style.overflow = 'hidden'
    document.body.appendChild(dialog.root)
    dialog.payButton.focus()
    resolve()
  })
}

function buildDummyDialog(
  order: CreateOrderResult,
  callbacks: { onChoice: (succeed: boolean) => void; onCancel: () => void },
) {
  const amount = new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2,
  }).format(order.amount_paise / 100)

  const root = document.createElement('div')
  root.className = 'dummy-pay-overlay'
  root.setAttribute('role', 'dialog')
  root.setAttribute('aria-modal', 'true')
  root.setAttribute('aria-label', 'Test payment')

  root.innerHTML = `
    <div class="dummy-pay-card">
      <p class="dummy-pay-tag">Test mode — no real payment</p>
      <h2 class="dummy-pay-brand">${BRAND_NAME}</h2>
      <p class="dummy-pay-amount">${amount}</p>
      <p class="dummy-pay-order">Order ${order.order_number}</p>
      <div class="dummy-pay-actions">
        <button type="button" data-act="pay" class="dummy-pay-btn primary">
          Simulate successful payment
        </button>
        <button type="button" data-act="fail" class="dummy-pay-btn ghost">
          Simulate failed payment
        </button>
        <button type="button" data-act="cancel" class="dummy-pay-btn link">
          Cancel
        </button>
      </div>
      <p class="dummy-pay-note">
        Swap in a real gateway by setting <code>PAYMENT_PROVIDER</code> in
        <code>backend/.env</code>.
      </p>
    </div>
  `

  const payButton = root.querySelector<HTMLButtonElement>('[data-act="pay"]')!
  payButton.addEventListener('click', () => callbacks.onChoice(true))
  root
    .querySelector<HTMLButtonElement>('[data-act="fail"]')!
    .addEventListener('click', () => callbacks.onChoice(false))
  root
    .querySelector<HTMLButtonElement>('[data-act="cancel"]')!
    .addEventListener('click', callbacks.onCancel)

  // Clicking the backdrop cancels, same as a hosted gateway page.
  root.addEventListener('click', (event) => {
    if (event.target === root) callbacks.onCancel()
  })

  return { root, payButton }
}

// --- razorpay -------------------------------------------------------------

async function openRazorpayPayment(
  order: CreateOrderResult,
  handlers: PaymentHandlers,
): Promise<void> {
  await loadRazorpay()
  if (!window.Razorpay) throw new Error('Payment widget unavailable.')

  new window.Razorpay({
    key: order.public_key,
    amount: order.amount_paise,
    currency: order.currency,
    name: BRAND_NAME,
    description: `Order ${order.order_number}`,
    order_id: order.provider_order_id,
    theme: { color: '#c9a227' },
    handler: (response: RazorpayHandlerResponse) =>
      handlers.onCallback({
        provider_order_id: response.razorpay_order_id,
        provider_payment_id: response.razorpay_payment_id,
        signature: response.razorpay_signature,
      }),
    modal: { ondismiss: handlers.onDismiss },
  }).open()
}
