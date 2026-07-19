// Mirrors the Pydantic schemas in backend/app/schemas/.
// Keep these in sync when the backend response shapes change.

export type BeanType = 'arabica' | 'robusta' | 'blend'
export type RoastLevel = 'light' | 'medium' | 'dark'
export type Grind = 'whole_bean' | 'filter' | 'espresso' | 'instant'
export type Flavour = 'original' | 'hazelnut' | 'vanilla' | 'caramel' | 'mocha'
export type OrderStatus = 'pending' | 'paid' | 'failed'

export type FacetKey = 'bean_type' | 'roast_level' | 'grind' | 'flavour'
export type SortOption = 'featured' | 'price_asc' | 'price_desc' | 'newest'

export interface Variant {
  id: number
  sku: string
  size_grams: number
  price_paise: number
  compare_at_price_paise: number | null
  stock_qty: number
  in_stock: boolean
  price_display: string
  discount_percent: number | null
}

export interface Product {
  id: number
  slug: string
  name: string
  description: string
  bean_type: BeanType
  roast_level: RoastLevel
  grind: Grind
  flavour: Flavour
  origin: string
  tasting_notes: string
  image_url: string
  /** Hidden products stay in the database but vanish from the shop. */
  is_active: boolean
  is_bestseller: boolean
  variants: Variant[]
}

export interface ProductList {
  items: Product[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface FacetValue {
  value: string
  label: string
  count: number
}

export type Facets = Record<FacetKey, FacetValue[]>

export interface CartItem {
  id: number
  variant_id: number
  quantity: number
  size_grams: number
  sku: string
  unit_price_paise: number
  line_total_paise: number
  stock_qty: number
  product_name: string
  product_slug: string
  image_url: string
}

export interface Cart {
  token: string
  items: CartItem[]
  item_count: number
  subtotal_paise: number
  shipping_paise: number
  total_paise: number
  free_shipping_threshold_paise: number
}

export interface ShippingAddress {
  name: string
  line1: string
  line2: string
  city: string
  state: string
  pincode: string
}

export interface CreateOrderPayload {
  cart_token: string
  email: string
  phone: string
  shipping: ShippingAddress
}

export type PaymentProvider = 'dummy' | 'razorpay'

export interface CreateOrderResult {
  order_number: string
  provider: PaymentProvider
  provider_order_id: string
  public_key: string
  amount_paise: number
  currency: string
}

/** Gateway callback. Same shape whichever provider produced it. */
export interface PaymentCallback {
  provider_order_id: string
  provider_payment_id: string
  signature: string
}

export interface OrderItem {
  product_name: string
  product_slug: string
  size_grams: number
  quantity: number
  unit_price_paise: number
  line_total_paise: number
}

export interface Order {
  order_number: string
  status: OrderStatus
  email: string
  subtotal_paise: number
  shipping_paise: number
  total_paise: number
  shipping_name: string
  shipping_line1: string
  shipping_line2: string
  shipping_city: string
  shipping_state: string
  shipping_pincode: string
  items: OrderItem[]
}

export interface Admin {
  id: number
  email: string
  name: string
}

export interface LoginResult {
  access_token: string
  token_type: string
  expires_in_minutes: number
  admin: Admin
}

/** A variant as sent to the admin API. `id` present = update, absent = create. */
export interface VariantInput {
  id?: number
  size_grams: number
  sku: string
  price_paise: number
  compare_at_price_paise: number | null
  stock_qty: number
}

export interface ProductInput {
  slug: string
  name: string
  description: string
  bean_type: BeanType
  roast_level: RoastLevel
  grind: Grind
  flavour: Flavour
  origin: string
  tasting_notes: string
  image_url: string
  is_active: boolean
  is_bestseller: boolean
  variants: VariantInput[]
}

export interface DeleteResult {
  status: 'deleted' | 'deactivated'
  detail: string
}

export interface ContactMessagePayload {
  name: string
  email: string
  phone: string
  subject: string
  message: string
}

export interface ContactMessageResult {
  ok: boolean
  reference: string
}

export interface ProductQuery {
  bean_type?: string[]
  roast_level?: string[]
  grind?: string[]
  flavour?: string[]
  bestseller?: boolean
  sort?: SortOption
  page?: number
  page_size?: number
}
