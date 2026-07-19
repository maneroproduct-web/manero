<template>
  <div class="container page wrap">
    <p class="mark" aria-hidden="true">☕</p>
    <h1>Page not found</h1>
    <p class="sub">That page has gone cold. Let's get you back to the good stuff.</p>
    <div class="cta">
      <RouterLink to="/shop" class="btn btn-primary">Shop coffee</RouterLink>
      <RouterLink to="/" class="btn btn-outline">Go home</RouterLink>
    </div>
  </div>
</template>

<style scoped>
.wrap {
  text-align: center;
  padding: 88px 20px 120px;
}

.mark {
  font-size: 3rem;
  margin: 0 0 12px;
}

h1 {
  font-size: 1.9rem;
  margin-bottom: 8px;
}

.sub {
  color: var(--ink-soft);
  margin: 0 0 28px;
}

.cta {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}
</style>
