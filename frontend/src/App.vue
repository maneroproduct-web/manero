<script setup lang="ts">
import AppFooter from '@/components/AppFooter.vue'
import AppHeader from '@/components/AppHeader.vue'
import CartDrawer from '@/components/CartDrawer.vue'
</script>

<template>
  <AppHeader />
  <main id="main">
    <RouterView />
  </main>
  <AppFooter />
  <CartDrawer />
</template>

<style scoped>
#main {
  min-height: calc(100vh - var(--header-h) - 240px);
}
</style>
