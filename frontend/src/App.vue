<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import AppFooter from '@/components/AppFooter.vue'
import AppHeader from '@/components/AppHeader.vue'
import CartDrawer from '@/components/CartDrawer.vue'

const route = useRoute()

// Admin screens carry their own header and have no business showing a shop
// header, footer or cart drawer.
const showChrome = computed(() => route.meta.chrome !== false)
</script>

<template>
  <AppHeader v-if="showChrome" />
  <main id="main">
    <RouterView />
  </main>
  <AppFooter v-if="showChrome" />
  <CartDrawer v-if="showChrome" />
</template>

<style scoped>
#main {
  min-height: calc(100vh - var(--header-h) - 240px);
}
</style>
