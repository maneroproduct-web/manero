<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    modelValue: number
    max?: number
    min?: number
    disabled?: boolean
  }>(),
  { max: 99, min: 1, disabled: false },
)

const emit = defineEmits<{ 'update:modelValue': [value: number] }>()

const canDecrease = computed(() => !props.disabled && props.modelValue > props.min)
const canIncrease = computed(() => !props.disabled && props.modelValue < props.max)

const step = (delta: number) => {
  const next = Math.min(props.max, Math.max(props.min, props.modelValue + delta))
  if (next !== props.modelValue) emit('update:modelValue', next)
}
</script>

<template>
  <div class="stepper">
    <button :disabled="!canDecrease" aria-label="Decrease quantity" @click="step(-1)">
      −
    </button>
    <span class="value" aria-live="polite">{{ modelValue }}</span>
    <button :disabled="!canIncrease" aria-label="Increase quantity" @click="step(1)">
      +
    </button>
  </div>
</template>

<style scoped>
.stepper {
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  background: var(--paper);
  overflow: hidden;
}

button {
  width: 34px;
  height: 36px;
  border: none;
  background: none;
  font-size: 1.05rem;
  color: var(--espresso);
  line-height: 1;
}

button:hover:not(:disabled) {
  background: var(--foam);
}

button:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.value {
  min-width: 32px;
  text-align: center;
  font-weight: 600;
  font-size: 0.92rem;
}
</style>
