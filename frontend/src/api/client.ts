import type {
  Admin,
  Cart,
  ContactMessagePayload,
  ContactMessageResult,
  CreateOrderPayload,
  CreateOrderResult,
  DeleteResult,
  Facets,
  LoginResult,
  Order,
  PaymentCallback,
  Product,
  ProductInput,
  ProductList,
  ProductQuery,
} from './types'

const BASE = import.meta.env.VITE_API_BASE_URL ?? ''

export class ApiError extends Error {
  readonly status: number

  constructor(message: string, status: number) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

/**
 * The admin session token, held in module scope so every request picks it up
 * without each call site remembering to pass it. The auth store owns the value
 * and is the only thing that should set it.
 */
let authToken: string | null = null

export function setAuthToken(token: string | null): void {
  authToken = token
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...((init?.headers as Record<string, string>) ?? {}),
  }
  if (authToken) headers.Authorization = `Bearer ${authToken}`

  let res: Response
  try {
    res = await fetch(`${BASE}/api/v1${path}`, { ...init, headers })
  } catch {
    // Network-level failure — the API is unreachable, not a 4xx/5xx.
    throw new ApiError('Could not reach the server. Check your connection.', 0)
  }

  if (!res.ok) {
    throw new ApiError(await readErrorMessage(res), res.status)
  }

  return res.status === 204 ? (undefined as T) : ((await res.json()) as T)
}

async function readErrorMessage(res: Response): Promise<string> {
  try {
    const body = await res.json()
    const detail = body?.detail
    if (typeof detail === 'string') return detail
    // FastAPI validation errors arrive as a list of {loc, msg}.
    if (Array.isArray(detail) && detail.length > 0) {
      return detail.map((d: { msg?: string }) => d.msg ?? 'Invalid value').join('. ')
    }
  } catch {
    /* fall through to the generic message */
  }
  return `Request failed (${res.status})`
}

function toQueryString(query: ProductQuery): string {
  const params = new URLSearchParams()
  for (const [key, value] of Object.entries(query)) {
    if (value === undefined || value === null) continue
    // Repeated keys for multi-select facets: ?grind=filter&grind=instant
    if (Array.isArray(value)) {
      value.forEach((v) => params.append(key, String(v)))
    } else {
      params.set(key, String(value))
    }
  }
  const qs = params.toString()
  return qs ? `?${qs}` : ''
}

const json = (body: unknown): RequestInit => ({ body: JSON.stringify(body) })

export const api = {
  listProducts: (query: ProductQuery = {}) =>
    request<ProductList>(`/products${toQueryString(query)}`),

  getProduct: (slug: string) => request<Product>(`/products/${slug}`),

  getFacets: () => request<Facets>('/products/facets'),

  createCart: () => request<Cart>('/carts', { method: 'POST' }),

  getCart: (token: string) => request<Cart>(`/carts/${token}`),

  addToCart: (token: string, variantId: number, quantity = 1) =>
    request<Cart>(`/carts/${token}/items`, {
      method: 'POST',
      ...json({ variant_id: variantId, quantity }),
    }),

  updateCartItem: (token: string, itemId: number, quantity: number) =>
    request<Cart>(`/carts/${token}/items/${itemId}`, {
      method: 'PATCH',
      ...json({ quantity }),
    }),

  removeCartItem: (token: string, itemId: number) =>
    request<Cart>(`/carts/${token}/items/${itemId}`, { method: 'DELETE' }),

  createOrder: (payload: CreateOrderPayload) =>
    request<CreateOrderResult>('/checkout/create-order', {
      method: 'POST',
      ...json(payload),
    }),

  /** Simulate the gateway UI. Only available while the dummy provider is active. */
  dummyPay: (providerOrderId: string, succeed = true) =>
    request<PaymentCallback>('/checkout/dummy-pay', {
      method: 'POST',
      ...json({ provider_order_id: providerOrderId, succeed }),
    }),

  verifyPayment: (payload: PaymentCallback) =>
    request<Order>('/checkout/verify', { method: 'POST', ...json(payload) }),

  getOrder: (orderNumber: string) => request<Order>(`/checkout/orders/${orderNumber}`),

  sendContactMessage: (payload: ContactMessagePayload) =>
    request<ContactMessageResult>('/contact', { method: 'POST', ...json(payload) }),

  // --- admin ---

  login: (email: string, password: string) =>
    request<LoginResult>('/auth/login', { method: 'POST', ...json({ email, password }) }),

  me: () => request<Admin>('/auth/me'),

  /** Every product, including inactive ones the storefront hides. */
  adminListProducts: () => request<Product[]>('/admin/products'),

  adminCreateProduct: (payload: ProductInput) =>
    request<Product>('/admin/products', { method: 'POST', ...json(payload) }),

  adminUpdateProduct: (id: number, payload: Partial<ProductInput>) =>
    request<Product>(`/admin/products/${id}`, { method: 'PATCH', ...json(payload) }),

  /** Deactivates by default; `force` permanently deletes an unsold product. */
  adminDeleteProduct: (id: number, force = false) =>
    request<DeleteResult>(`/admin/products/${id}${force ? '?force=true' : ''}`, {
      method: 'DELETE',
    }),
}
