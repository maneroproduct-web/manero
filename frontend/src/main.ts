import { createPinia } from 'pinia'
import { createApp } from 'vue'

import App from './App.vue'
import { router } from './router'
import { useAuthStore } from './stores/auth'
import { useCartStore } from './stores/cart'
import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)

// Restore the cart before mount so the header badge is right on first paint.
useCartStore().init()
// Verify any stored admin token in the background; the router guard awaits
// this when it needs a decision.
useAuthStore().init()

app.mount('#app')
