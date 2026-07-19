<script setup lang="ts">
/**
 * Social icons, drawn as inline SVG rather than loaded from an icon font or
 * CDN — they inherit `currentColor`, stay sharp at any size, and add no
 * network request.
 *
 * TO CHANGE: edit the `href` values below to your real accounts. Delete an
 * entry to hide that icon. An empty `href` renders nothing, so you can leave a
 * placeholder in place without shipping a dead link.
 */
const socials = [
  { name: 'Instagram', href: 'https://instagram.com/manero.coffee', icon: 'instagram' },
  { name: 'Facebook', href: 'https://facebook.com/manerocoffee', icon: 'facebook' },
  { name: 'X (Twitter)', href: 'https://x.com/manerocoffee', icon: 'x' },
  { name: 'YouTube', href: 'https://youtube.com/@manerocoffee', icon: 'youtube' },
].filter((s) => s.href)
</script>

<template>
  <ul class="socials">
    <li v-for="social in socials" :key="social.name">
      <a
        :href="social.href"
        target="_blank"
        rel="noopener noreferrer"
        :aria-label="social.name"
        class="social"
      >
        <svg
          viewBox="0 0 24 24"
          width="18"
          height="18"
          aria-hidden="true"
          focusable="false"
        >
          <template v-if="social.icon === 'instagram'">
            <rect
              x="2.5" y="2.5" width="19" height="19" rx="5.5"
              fill="none" stroke="currentColor" stroke-width="1.8"
            />
            <circle
              cx="12" cy="12" r="4.2"
              fill="none" stroke="currentColor" stroke-width="1.8"
            />
            <circle cx="17.4" cy="6.6" r="1.25" fill="currentColor" />
          </template>

          <template v-else-if="social.icon === 'facebook'">
            <path
              fill="currentColor"
              d="M13.5 21v-8h2.7l.4-3.1h-3.1V7.9c0-.9.25-1.5 1.55-1.5h1.65V3.6c-.29-.04-1.27-.12-2.41-.12-2.38 0-4.01 1.45-4.01 4.13v2.3H7.6V13h2.68v8h3.22z"
            />
          </template>

          <template v-else-if="social.icon === 'x'">
            <path
              fill="currentColor"
              d="M17.53 3h3.05l-6.66 7.61L21.75 21h-6.13l-4.8-6.28L5.32 21H2.27l7.12-8.14L2.5 3h6.28l4.34 5.74L17.53 3zm-1.07 16.2h1.69L7.62 4.71H5.8l10.66 14.49z"
            />
          </template>

          <template v-else-if="social.icon === 'youtube'">
            <path
              fill="currentColor"
              d="M21.6 7.2c-.23-.87-.91-1.55-1.78-1.78C18.25 5 12 5 12 5s-6.25 0-7.82.42c-.87.23-1.55.91-1.78 1.78C2 8.77 2 12 2 12s0 3.23.4 4.8c.23.87.91 1.55 1.78 1.78C5.75 19 12 19 12 19s6.25 0 7.82-.42c.87-.23 1.55-.91 1.78-1.78.4-1.57.4-4.8.4-4.8s0-3.23-.4-4.8zM10 15.1V8.9l5.2 3.1-5.2 3.1z"
            />
          </template>
        </svg>
      </a>
    </li>
  </ul>
</template>

<style scoped>
.socials {
  display: flex;
  gap: 10px;
  list-style: none;
  margin: 20px 0 0;
  padding: 0;
}

.social {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  border: 1px solid rgba(212, 175, 55, 0.35);
  color: var(--crema);
  transition: color 0.15s, border-color 0.15s, background-color 0.15s;
}

.social:hover {
  color: var(--espresso);
  background: linear-gradient(180deg, var(--gold) 0%, var(--gold-dark) 100%);
  border-color: var(--gold);
}

@media (max-width: 900px), (pointer: coarse) {
  .social {
    width: 44px;
    height: 44px;
  }
}
</style>
