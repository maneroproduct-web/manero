<script setup lang="ts">
import { computed } from 'vue'

import type { FacetKey, Facets } from '@/api/types'
import { FACET_KEYS, FACET_TITLES, type ActiveFilters } from '@/stores/catalog'

const props = defineProps<{
  facets: Facets | null
  active: ActiveFilters
}>()

const emit = defineEmits<{
  toggle: [key: FacetKey, value: string]
  clear: []
}>()

const activeCount = computed(() =>
  FACET_KEYS.reduce((sum, key) => sum + props.active[key].length, 0),
)

const isChecked = (key: FacetKey, value: string) => props.active[key].includes(value)
</script>

<template>
  <aside class="sidebar" aria-label="Product filters">
    <div class="head">
      <h2>Filter</h2>
      <button v-if="activeCount" class="clear" @click="emit('clear')">
        Clear all ({{ activeCount }})
      </button>
    </div>

    <div v-if="!facets" class="loading">
      <div v-for="n in 4" :key="n" class="skeleton block"></div>
    </div>

    <fieldset v-for="key in FACET_KEYS" v-else :key="key" class="group">
      <legend>{{ FACET_TITLES[key] }}</legend>
      <label v-for="option in facets[key]" :key="option.value" class="option">
        <input
          type="checkbox"
          :checked="isChecked(key, option.value)"
          @change="emit('toggle', key, option.value)"
        />
        <span class="label">{{ option.label }}</span>
        <span class="count">{{ option.count }}</span>
      </label>
    </fieldset>
  </aside>
</template>

<style scoped>
.sidebar {
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 20px;
  align-self: start;
  position: sticky;
  top: calc(var(--header-h) + 20px);
}

.head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 16px;
}

.head h2 {
  font-size: 1.05rem;
  margin: 0;
}

.clear {
  background: none;
  border: none;
  padding: 0;
  font-size: 0.8rem;
  color: var(--accent);
  text-decoration: underline;
}

.group {
  border: none;
  border-top: 1px solid var(--line);
  padding: 16px 0 4px;
  margin: 0;
}

legend {
  font-size: 0.76rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--ink-soft);
  padding: 0;
  margin-bottom: 10px;
}

.option {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 6px 0;
  cursor: pointer;
  font-size: 0.89rem;
}

.option input {
  accent-color: var(--accent);
  width: 15px;
  height: 15px;
  cursor: pointer;
}

.label {
  flex: 1;
}

.count {
  font-size: 0.78rem;
  color: var(--ink-soft);
}

.block {
  height: 84px;
  margin-bottom: 12px;
}

@media (max-width: 900px) {
  .sidebar {
    position: static;
  }
}
</style>
