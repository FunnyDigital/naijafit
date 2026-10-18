import { createApp } from 'vue'

import '@fontsource-variable/inter'
import '@fontsource-variable/fraunces'
import './index.css'

import App from './App.vue'
import router from './router'
import { reveal } from './composables/useReveal'

createApp(App).use(router).directive('reveal', reveal).mount('#app')

// Installable app: register the service worker in production builds only, so
// `npm run dev` never serves a stale shell.
if (import.meta.env.PROD && 'serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {
      /* not fatal — the app works fine without it */
    })
  })
}
