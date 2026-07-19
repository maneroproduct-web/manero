<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { LocationQuery } from 'vue-router'

import type { FacetKey, SortOption } from '@/api/types'
import FilterSidebar from '@/components/FilterSidebar.vue'
import ProductCard from '@/components/ProductCard.vue'
import { FACET_KEYS, emptyFilters, useCatalogStore } from '@/stores/catalog'
import type { ActiveFilters } from '@/stores/catalog'

const route = useRoute()
const router = useRouter()
const catalog = useCatalogStore()

const SORTS: { value: SortOption; label: string }[] = [
  { value: 'featured', label: 'Featured' },
  { value: 'price_asc', label: 'Price: low to high' },
  { value: 'price_desc', label: 'Price: high to low' },
  { value: 'newest', label: 'Newest' },
]

/** The URL query is the source of truth, so filtered views are shareable. */
function asArray(value: LocationQuery[string]): string[] {
  if (Array.isArray(value)) return value.filter((v): v is string => v !== null)
  return typeof value === 'string' && value ? [value] : []
}

const filters = computed<ActiveFilters>(() => {
  const next = emptyFilters()
  for (const key of FACET_KEYS) next[key] = asArray(route.query[key])
  return next
})

const sort = computed<SortOption>(() => {
  const raw = route.query.sort
  const found = SORTS.find((s) => s.value === raw)
  return found ? found.value : 'featured'
})

const page = computed(() => {
  const parsed = Number(route.query.page)
  return Number.isInteger(parsed) && parsed > 0 ? parsed : 1
})

function updateQuery(patch: Record<string, string | string[] | undefined>) {
  const query: Record<string, string | string[]> = { ...route.query } as Record<
    string,
    string | string[]
  >
  for (const [key, value] of Object.entries(patch)) {
    if (value === undefined || (Array.isArray(value) && value.length === 0)) {
      delete query[key]
    } else {
      query[key] = value
    }
  }
  router.push({ path: '/shop', query })
}

function toggleFilter(key: FacetKey, value: string) {
  const current = filters.value[key]
  const next = current.includes(value)
    ? current.filter((v) => v !== value)
    : [...current, value]
  // Changing a filter invalidates the current page number.
  updateQuery({ [key]: next, page: undefined })
}

function clearFilters() {
  updateQuery({
    bean_type: undefined,
    roast_level: undefined,
    grind: undefined,
    flavour: undefined,
    page: undefined,
  })
}

const onSortChange = (event: Event) =>
  updateQuery({ sort: (event.target as HTMLSelectElement).value, page: undefined })

const goToPage = (n: number) => updateQuery({ page: n === 1 ? undefined : String(n) })

catalog.loadFacets()

watch(
  [filters, sort, page],
  () => catalog.loadProducts(filters.value, sort.value, page.value),
  { immediate: true, deep: true },
)
</script>

<template>
  <div class="container page">
    <h1 class="page-title">Shop coffee</h1>
    <p class="page-subtitle">
      {{ catalog.loading ? 'Loading…' : `${catalog.total} product(s)` }}
    </p>

    <div class="layout">
      <FilterSidebar
        :facets="catalog.facets"
        :active="filters"
        @toggle="toggleFilter"
        @clear="clearFilters"
      />

      <section class="results">
        <div class="toolbar">
          <label class="sort">
            <span>Sort</span>
            <select :value="sort" @change="onSortChange">
              <option v-for="opt in SORTS" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </label>
        </div>

        <p v-if="catalog.error" class="notice notice-error">{{ catalog.error }}</p>

        <div v-else-if="catalog.loading" class="grid">
          <div v-for="n in 6" :key="n" class="skeleton card-skeleton"></div>
        </div>

        <div v-else-if="catalog.isEmpty" class="empty">
          <p class="empty-icon" aria-hidden="true">🔍</p>
          <h3>No coffee matches those filters</h3>
          <p>Try loosening a filter or two.</p>
          <button class="btn btn-outline" @click="clearFilters">Clear filters</button>
        </div>

        <template v-else>
          <div class="grid">
            <ProductCard
              v-for="product in catalog.products"
              :key="product.id"
              :product="product"
            />
          </div>

          <nav v-if="catalog.totalPages > 1" class="pager" aria-label="Pagination">
            <button
              class="btn btn-outline"
              :disabled="page <= 1"
              @click="goToPage(page - 1)"
            >
              Previous
            </button>
            <span class="page-of">Page {{ page }} of {{ catalog.totalPages }}</span>
            <button
              class="btn btn-outline"
              :disabled="page >= catalog.totalPages"
              @click="goToPage(page + 1)"
            >
              Next
            </button>
          </nav>
        </template>
      </section>
    </div>
  </div>
</template>

<style scoped>
.layout {
  display: grid;
  /* minmax(0, …) so the product grid can shrink — see CheckoutView. */
  grid-template-columns: 250px minmax(0, 1fr);
  gap: 28px;
  align-items: start;
}

.toolbar {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 18px;
}

.sort {
  display: flex;
  align-items: center;
  gap: 9px;
  font-size: 0.85rem;
  color: var(--ink-soft);
}

.sort select {
  padding: 8px 11px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--paper);
}

.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

.card-skeleton {
  height: 340px;
}

.empty {
  text-align: center;
  padding: 64px 20px;
  color: var(--ink-soft);
}

.empty-icon {
  font-size: 2.2rem;
  margin: 0 0 8px;
}

.empty h3 {
  margin-bottom: 6px;
}

.empty .btn {
  margin-top: 18px;
}

.pager {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 18px;
  margin-top: 36px;
}

.page-of {
  font-size: 0.87rem;
  color: var(--ink-soft);
}

@media (max-width: 1050px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 900px) {
  .layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 560px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
