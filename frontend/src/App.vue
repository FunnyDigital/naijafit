<template>
  <div class="flex h-full flex-col overflow-hidden bg-canvas">
    <AppHeader v-if="!route.meta.bare" />

    <main
      class="relative flex-1 overflow-y-auto overscroll-contain"
      :class="{ 'pb-24 md:pb-10': !route.meta.bare }"
    >
      <RouterView v-slot="{ Component }">
        <Transition :name="transitionName" mode="out-in">
          <component :is="Component" :key="route.path" />
        </Transition>
      </RouterView>
    </main>

    <TabBar v-if="!route.meta.bare" />
    <ToastHost />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import AppHeader from './components/AppHeader.vue'
import TabBar from './components/TabBar.vue'
import ToastHost from './components/ToastHost.vue'

const route = useRoute()

// Onboarding and login own the whole screen, so they get a plain fade.
const transitionName = computed(() => (route.meta.bare ? 'fade' : 'page'))
</script>
