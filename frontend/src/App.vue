<template>
  <div class="flex h-full flex-col overflow-hidden bg-canvas">
    <AppHeader v-if="!route.meta.bare" />
    <main
      class="relative flex-1 overflow-y-auto overscroll-contain"
      :class="{ 'pb-24 md:pb-10': !route.meta.bare }"
    >
      <RouterView />
    </main>
    <TabBar v-if="!route.meta.bare" />
    <ToastHost />
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
import AppHeader from './components/AppHeader.vue'
import TabBar from './components/TabBar.vue'
import ToastHost from './components/ToastHost.vue'

const route = useRoute()
</script>
