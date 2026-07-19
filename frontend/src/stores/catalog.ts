import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

import { api } from '@/api/client'
import type { FacetKey, Facets, Product, ProductQuery, SortOption } from '@/api/types'

export const FACET_KEYS: FacetKey[] = ['bean_type', 'roast_level', 'grind', 'flavour']

export const FACET_TITLES: Record<FacetKey, string> = {
  bean_type: 'Bean',
  roast_level: 'Roast',
  grind: 'Grind',
  flavour: 'Flavour',
}

export type ActiveFilters = Record<FacetKey, string[]>

export const emptyFilters = (): ActiveFilters => ({
  bean_type: [],
  roast_level: [],
  grind: [],
  flavour: [],
})

export const useCatalogStore = defineStore('catalog', () => {
  const products = ref<Product[]>([])
  const facets = ref<Facets | null>(null)
  const total = ref(0)
  const page = ref(1)
  const totalPages = ref(0)
  const loading = ref(false)
  const error = ref<string | null>(null)

  const bestsellers = ref<Product[]>([])
  const bestsellersLoading = ref(false)

  const isEmpty = computed(() => !loading.value && products.value.length === 0)

  async function loadFacets() {
    if (facets.value) return
    try {
      facets.value = await api.getFacets()
    } catch {
      // The sidebar just won't render; the grid still works.
    }
  }

  async function loadProducts(filters: ActiveFilters, sort: SortOption, pageNo: number) {
    loading.value = true
    error.value = null
    const query: ProductQuery = { sort, page: pageNo, page_size: 12 }
    for (const key of FACET_KEYS) {
      if (filters[key].length) query[key] = filters[key]
    }

    try {
      const result = await api.listProducts(query)
      products.value = result.items
      total.value = result.total
      page.value = result.page
      totalPages.value = result.total_pages
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Could not load products'
      products.value = []
      total.value = 0
      totalPages.value = 0
    } finally {
      loading.value = false
    }
  }

  async function loadBestsellers() {
    if (bestsellers.value.length) return
    bestsellersLoading.value = true
    try {
      const result = await api.listProducts({ bestseller: true, page_size: 4 })
      bestsellers.value = result.items
    } catch {
      bestsellers.value = []
    } finally {
      bestsellersLoading.value = false
    }
  }

  return {
    products,
    facets,
    total,
    page,
    totalPages,
    loading,
    error,
    isEmpty,
    bestsellers,
    bestsellersLoading,
    loadFacets,
    loadProducts,
    loadBestsellers,
  }
})
