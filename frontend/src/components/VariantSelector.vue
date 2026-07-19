<script setup lang="ts">
import type { Variant } from '@/api/types'
import { formatInr, formatWeight } from '@/utils/money'

defineProps<{
  variants: Variant[]
  selectedId: number | null
}>()

const emit = defineEmits<{ select: [variant: Variant] }>()
</script>

<template>
  <div class="selector">
    <p class="label">Size</p>
    <div class="options" role="radiogroup" aria-label="Pack size">
      <button
        v-for="variant in variants"
        :key="variant.id"
        role="radio"
        :aria-checked="variant.id === selectedId"
        :disabled="!variant.in_stock"
        :class="['option', { selected: variant.id === selectedId }]"
        @click="emit('select', variant)"
      >
        <span class="size">{{ formatWeight(variant.size_grams) }}</span>
        <span class="price">{{ formatInr(variant.price_paise) }}</span>
        <span v-if="!variant.in_stock" class="oos">Sold out</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
.label {
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--ink-soft);
  margin: 0 0 10px;
}

.options {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.option {
  min-width: 96px;
  padding: 11px 14px;
  border: 1.5px solid var(--line);
  border-radius: var(--radius);
  background: var(--paper);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 3px;
  transition: border-color 0.15s, background-color 0.15s;
}

.option:hover:not(:disabled) {
  border-color: var(--crema);
}

.option.selected {
  border-color: var(--accent);
  background: #fdf5f1;
}

.option:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.size {
  font-weight: 700;
  font-size: 0.92rem;
  color: var(--espresso);
}

.price {
  font-size: 0.85rem;
  color: var(--ink-soft);
}

.oos {
  font-size: 0.7rem;
  color: var(--danger);
  font-weight: 600;
}
</style>
