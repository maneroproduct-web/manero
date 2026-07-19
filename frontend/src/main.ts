import { createPinia } from 'pinia'
import { createApp } from 'vue'

import App from './App.vue'
import { router } from './router'
import { useCartStore } from './stores/cart'
import './style.css'

const app = createApp(App)
app.use(createPinia())
app.use(router)

// Restore the cart before mount so the header badge is right on first paint.
useCartStore().init()

app.mount('#app')
