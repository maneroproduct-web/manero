<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { api } from '@/api/client'
import type {
  BeanType,
  Flavour,
  Grind,
  Product,
  ProductInput,
  RoastLevel,
} from '@/api/types'
import { BRAND_NAME, markUrl } from '@/assets/logo'
import { useAuthStore } from '@/stores/auth'
import { formatInr, formatWeight } from '@/utils/money'

const auth = useAuthStore()
const router = useRouter()

const products = ref<Product[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const notice = ref<string | null>(null)

const editing = ref<Product | null>(null)
const creating = ref(false)
const saving = ref(false)
const formError = ref<string | null>(null)

const BEAN: BeanType[] = ['arabica', 'robusta', 'blend']
const ROAST: RoastLevel[] = ['light', 'medium', 'dark']
const GRIND: Grind[] = ['whole_bean', 'filter', 'espresso', 'instant']
const FLAVOUR: Flavour[] = ['original', 'hazelnut', 'vanilla', 'caramel', 'mocha']

const blank = (): ProductInput => ({
  slug: '',
  name: '',
  description: '',
  bean_type: 'arabica',
  roast_level: 'medium',
  grind: 'filter',
  flavour: 'original',
  origin: '',
  tasting_notes: '',
  image_url: '',
  is_active: true,
  is_bestseller: false,
  variants: [
    { size_grams: 250, sku: '', price_paise: 0, compare_at_price_paise: null, stock_qty: 0 },
  ],
})

const form = reactive<ProductInput>(blank())

/**
 * Prices are entered in rupees but stored as integer paise. These two helpers
 * are the only place the conversion happens, so a stray ×100 can't creep in.
 */
const toRupees = (paise: number | null) => (paise === null ? '' : String(paise / 100))
const toPaise = (rupees: string | number) => Math.round(Number(rupees || 0) * 100)

const isOpen = computed(() => creating.value || editing.value !== null)

async function load() {
  loading.value = true
  error.value = null
  try {
    products.value = await api.adminListProducts()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not load products'
  } finally {
    loading.value = false
  }
}

function startCreate() {
  Object.assign(form, blank())
  formError.value = null
  editing.value = null
  creating.value = true
}

function startEdit(product: Product) {
  Object.assign(form, {
    slug: product.slug,
    name: product.name,
    description: product.description,
    bean_type: product.bean_type,
    roast_level: product.roast_level,
    grind: product.grind,
    flavour: product.flavour,
    origin: product.origin,
    tasting_notes: product.tasting_notes,
    image_url: product.image_url,
    // Carry the current value through: forcing true here would silently
    // un-hide a product every time someone edited its description.
    is_active: product.is_active,
    is_bestseller: product.is_bestseller,
    variants: product.variants.map((v) => ({
      id: v.id,
      size_grams: v.size_grams,
      sku: v.sku,
      price_paise: v.price_paise,
      compare_at_price_paise: v.compare_at_price_paise,
      stock_qty: v.stock_qty,
    })),
  })
  formError.value = null
  creating.value = false
  editing.value = product
}

function close() {
  creating.value = false
  editing.value = null
}

function addVariant() {
  form.variants.push({
    size_grams: 500,
    sku: '',
    price_paise: 0,
    compare_at_price_paise: null,
    stock_qty: 0,
  })
}

function removeVariant(i: number) {
  if (form.variants.length > 1) form.variants.splice(i, 1)
}

async function save() {
  formError.value = null

  if (!form.name.trim() || !form.slug.trim()) {
    formError.value = 'Name and slug are both required.'
    return
  }
  if (form.variants.some((v) => !v.sku.trim())) {
    formError.value = 'Every size needs a SKU.'
    return
  }
  if (form.variants.some((v) => v.price_paise <= 0)) {
    formError.value = 'Every size needs a price above zero.'
    return
  }

  saving.value = true
  try {
    const payload: ProductInput = { ...form, variants: [...form.variants] }
    if (editing.value) {
      await api.adminUpdateProduct(editing.value.id, payload)
      notice.value = `Saved “${form.name}”.`
    } else {
      await api.adminCreateProduct(payload)
      notice.value = `Added “${form.name}”.`
    }
    close()
    await load()
  } catch (err) {
    formError.value = err instanceof Error ? err.message : 'Could not save.'
  } finally {
    saving.value = false
  }
}

async function remove(product: Product, force: boolean) {
  const question = force
    ? `Permanently delete “${product.name}”? This cannot be undone.`
    : `Hide “${product.name}” from the shop? It stays in your records and can be restored.`
  if (!window.confirm(question)) return

  try {
    const result = await api.adminDeleteProduct(product.id, force)
    notice.value = result.detail
    await load()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not delete.'
  }
}

async function restore(product: Product) {
  try {
    await api.adminUpdateProduct(product.id, { is_active: true })
    notice.value = `“${product.name}” is visible in the shop again.`
    await load()
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Could not restore.'
  }
}

function signOut() {
  auth.logout()
  router.push('/admin/login')
}

onMounted(load)
</script>

<template>
  <div class="admin">
    <header class="bar">
      <div class="brand">
        <img :src="markUrl" alt="" aria-hidden="true" />
        <span>{{ BRAND_NAME }} admin</span>
      </div>
      <div class="bar-right">
        <RouterLink to="/" class="bar-link">View shop</RouterLink>
        <span class="who">{{ auth.admin?.email }}</span>
        <button class="bar-link" @click="signOut">Sign out</button>
      </div>
    </header>

    <main class="container page">
      <div class="head">
        <div>
          <h1>Products</h1>
          <p class="sub">{{ products.length }} in the catalog</p>
        </div>
        <button class="btn btn-primary" @click="startCreate">Add product</button>
      </div>

      <p v-if="notice" class="notice ok">{{ notice }}</p>
      <p v-if="error" class="notice notice-error">{{ error }}</p>

      <div v-if="loading" class="skeleton block"></div>

      <p v-else-if="!products.length" class="notice">
        No products yet. Add one, or seed the sample catalog with
        <code>python -m app.seeds.seed_products</code>.
      </p>

      <table v-else class="grid">
        <thead>
          <tr>
            <th>Product</th>
            <th>Type</th>
            <th>Sizes</th>
            <th>Stock</th>
            <th>Status</th>
            <th class="right">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="product in products" :key="product.id">
            <td>
              <div class="cell-product">
                <img v-if="product.image_url" :src="product.image_url" alt="" />
                <div>
                  <p class="name">{{ product.name }}</p>
                  <p class="slug">/{{ product.slug }}</p>
                </div>
              </div>
            </td>
            <td class="meta">
              {{ product.bean_type }} · {{ product.roast_level }}<br />
              <span class="muted">{{ product.grind.replace('_', ' ') }}</span>
            </td>
            <td class="meta">
              <span v-for="v in product.variants" :key="v.id" class="size">
                {{ formatWeight(v.size_grams) }} {{ formatInr(v.price_paise) }}
              </span>
            </td>
            <td class="meta">
              <span
                v-for="v in product.variants"
                :key="v.id"
                :class="['stock', { low: v.stock_qty <= 5 }]"
              >
                {{ v.stock_qty }}
              </span>
            </td>
            <td>
              <span v-if="product.is_bestseller" class="tag best">Bestseller</span>
              <span v-if="product.is_active" class="tag live">Live</span>
              <span v-else class="tag hidden">Hidden</span>
            </td>
            <td class="right actions">
              <button class="link" @click="startEdit(product)">Edit</button>
              <button
                v-if="product.is_active"
                class="link danger"
                @click="remove(product, false)"
              >
                Hide
              </button>
              <button v-else class="link" @click="restore(product)">Restore</button>
              <button class="link danger" @click="remove(product, true)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </main>

    <!-- Editor -->
    <div v-if="isOpen" class="overlay" @click.self="close">
      <div class="drawer" role="dialog" aria-modal="true">
        <header class="drawer-head">
          <h2>{{ creating ? 'Add product' : `Edit ${editing?.name}` }}</h2>
          <button class="close" aria-label="Close" @click="close">✕</button>
        </header>

        <div class="drawer-body">
          <p v-if="formError" class="notice notice-error">{{ formError }}</p>

          <div class="row-2">
            <div class="field">
              <label>Name</label>
              <input v-model="form.name" />
            </div>
            <div class="field">
              <label>Slug (web address)</label>
              <input v-model="form.slug" :disabled="!creating" placeholder="instant-hazelnut" />
              <span v-if="!creating" class="field-hint">
                Slugs cannot be changed — links and past orders point at them.
              </span>
            </div>
          </div>

          <div class="field">
            <label>Description</label>
            <textarea v-model="form.description" rows="3"></textarea>
          </div>

          <div class="row-2">
            <div class="field">
              <label>Origin</label>
              <input v-model="form.origin" placeholder="Chikmagalur, Karnataka" />
            </div>
            <div class="field">
              <label>Tasting notes</label>
              <input v-model="form.tasting_notes" placeholder="Cocoa, almond, citrus" />
            </div>
          </div>

          <div class="field">
            <label>Image URL</label>
            <input v-model="form.image_url" placeholder="https://…" />
          </div>

          <div class="row-4">
            <div class="field">
              <label>Bean</label>
              <select v-model="form.bean_type">
                <option v-for="b in BEAN" :key="b" :value="b">{{ b }}</option>
              </select>
            </div>
            <div class="field">
              <label>Roast</label>
              <select v-model="form.roast_level">
                <option v-for="r in ROAST" :key="r" :value="r">{{ r }}</option>
              </select>
            </div>
            <div class="field">
              <label>Grind</label>
              <select v-model="form.grind">
                <option v-for="g in GRIND" :key="g" :value="g">
                  {{ g.replace('_', ' ') }}
                </option>
              </select>
            </div>
            <div class="field">
              <label>Flavour</label>
              <select v-model="form.flavour">
                <option v-for="f in FLAVOUR" :key="f" :value="f">{{ f }}</option>
              </select>
            </div>
          </div>

          <label class="check">
            <input v-model="form.is_bestseller" type="checkbox" />
            Show on the homepage as a bestseller
          </label>

          <h3 class="sizes-head">
            Sizes and prices
            <button class="link" @click="addVariant">+ Add size</button>
          </h3>

          <div v-for="(variant, i) in form.variants" :key="i" class="variant">
            <div class="field">
              <label>Grams</label>
              <input v-model.number="variant.size_grams" type="number" min="1" />
            </div>
            <div class="field">
              <label>SKU</label>
              <input v-model="variant.sku" placeholder="MNR-IH-50G" />
            </div>
            <div class="field">
              <label>Price ₹</label>
              <input
                :value="toRupees(variant.price_paise)"
                type="number"
                min="0"
                step="0.01"
                @input="variant.price_paise = toPaise(($event.target as HTMLInputElement).value)"
              />
            </div>
            <div class="field">
              <label>Was ₹</label>
              <input
                :value="toRupees(variant.compare_at_price_paise)"
                type="number"
                min="0"
                step="0.01"
                placeholder="—"
                @input="
                  variant.compare_at_price_paise =
                    ($event.target as HTMLInputElement).value
                      ? toPaise(($event.target as HTMLInputElement).value)
                      : null
                "
              />
            </div>
            <div class="field">
              <label>Stock</label>
              <input v-model.number="variant.stock_qty" type="number" min="0" />
            </div>
            <button
              class="link danger remove"
              :disabled="form.variants.length === 1"
              @click="removeVariant(i)"
            >
              Remove
            </button>
          </div>
        </div>

        <footer class="drawer-foot">
          <button class="btn btn-outline" @click="close">Cancel</button>
          <button class="btn btn-primary" :disabled="saving" @click="save">
            {{ saving ? 'Saving…' : creating ? 'Add product' : 'Save changes' }}
          </button>
        </footer>
      </div>
    </div>
  </div>
</template>

<style scoped>
.admin {
  min-height: 100vh;
  background: var(--foam);
}

.bar {
  background: var(--espresso);
  padding: 0 20px;
  height: 62px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
}

.brand img {
  height: 30px;
}

.brand span {
  font-family: Georgia, serif;
  letter-spacing: 0.16em;
  text-transform: uppercase;
  color: var(--gold-light);
  font-size: 0.9rem;
}

.bar-right {
  display: flex;
  align-items: center;
  gap: 18px;
}

.bar-link {
  background: none;
  border: none;
  color: var(--crema);
  font-size: 0.85rem;
  padding: 8px 0;
}

.bar-link:hover {
  color: var(--gold-light);
}

.who {
  color: var(--crema);
  font-size: 0.8rem;
  opacity: 0.7;
}

.head {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 22px;
}

.head h1 {
  font-size: 1.7rem;
  margin: 0;
}

.sub {
  margin: 4px 0 0;
  color: var(--ink-soft);
  font-size: 0.9rem;
}

.notice.ok {
  border-color: #c5e0d1;
  background: #e9f3ed;
  color: var(--success);
  margin-bottom: 16px;
}

.grid {
  width: 100%;
  border-collapse: collapse;
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

th {
  text-align: left;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--ink-soft);
  padding: 13px 14px;
  border-bottom: 1px solid var(--line);
  background: var(--foam);
}

td {
  padding: 13px 14px;
  border-bottom: 1px solid var(--line);
  vertical-align: top;
  font-size: 0.88rem;
}

tbody tr:last-child td {
  border-bottom: none;
}

.right {
  text-align: right;
}

.cell-product {
  display: flex;
  gap: 11px;
  align-items: center;
}

.cell-product img {
  width: 42px;
  height: 42px;
  border-radius: 7px;
  object-fit: cover;
  background: var(--foam);
}

.name {
  margin: 0;
  font-weight: 600;
}

.slug {
  margin: 2px 0 0;
  font-size: 0.78rem;
  color: var(--ink-soft);
}

.meta {
  color: var(--ink-soft);
  text-transform: capitalize;
  font-size: 0.83rem;
  line-height: 1.6;
}

.muted {
  opacity: 0.7;
}

.size,
.stock {
  display: block;
  white-space: nowrap;
}

.stock.low {
  color: var(--danger);
  font-weight: 600;
}

.tag {
  display: inline-block;
  padding: 3px 9px;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  margin-right: 5px;
}

.tag.best {
  background: var(--espresso);
  color: var(--gold-light);
}

.tag.live {
  background: #e9f3ed;
  color: var(--success);
}

.tag.hidden {
  background: var(--line);
  color: var(--ink-soft);
}

.actions {
  white-space: nowrap;
}

.link {
  background: none;
  border: none;
  color: var(--accent);
  font-size: 0.83rem;
  padding: 4px 6px;
  text-decoration: underline;
}

.link.danger {
  color: var(--ink-soft);
}

.link.danger:hover {
  color: var(--danger);
}

.link:disabled {
  opacity: 0.4;
  text-decoration: none;
}

.block {
  height: 260px;
}

/* ---------- Editor ---------- */

.overlay {
  position: fixed;
  inset: 0;
  background: rgba(13, 11, 9, 0.5);
  z-index: 100;
  display: flex;
  justify-content: flex-end;
}

.drawer {
  width: min(720px, 100%);
  background: var(--foam);
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-lg);
}

.drawer-head,
.drawer-foot {
  padding: 18px 22px;
  background: var(--paper);
  border-bottom: 1px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.drawer-foot {
  border-bottom: none;
  border-top: 1px solid var(--line);
  gap: 10px;
  justify-content: flex-end;
}

.drawer-head h2 {
  margin: 0;
  font-size: 1.1rem;
}

.close {
  background: none;
  border: none;
  font-size: 1.05rem;
}

.drawer-body {
  flex: 1;
  overflow-y: auto;
  padding: 22px;
}

.row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.row-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 12px;
}

.field-hint {
  font-size: 0.76rem;
  color: var(--ink-soft);
}

textarea {
  padding: 11px 13px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  font-family: inherit;
  resize: vertical;
}

.check {
  display: flex;
  align-items: center;
  gap: 9px;
  margin: 6px 0 22px;
  font-size: 0.9rem;
}

.check input {
  width: 16px;
  height: 16px;
  accent-color: var(--accent);
}

.sizes-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 1rem;
  padding-top: 18px;
  border-top: 1px solid var(--line);
  margin-bottom: 14px;
}

.variant {
  display: grid;
  grid-template-columns: 88px 1fr 108px 108px 88px auto;
  gap: 10px;
  align-items: end;
  padding: 12px;
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: var(--radius);
  margin-bottom: 10px;
}

.variant .field {
  margin-bottom: 0;
}

.remove {
  padding-bottom: 12px;
}

@media (max-width: 860px) {
  .row-4,
  .row-2 {
    grid-template-columns: 1fr 1fr;
  }
  .variant {
    grid-template-columns: 1fr 1fr;
  }
  .grid,
  thead {
    font-size: 0.82rem;
  }
}
</style>
