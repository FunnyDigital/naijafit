<template>
  <div class="mx-auto flex min-h-full w-full max-w-lg flex-col items-center justify-center px-6 py-10 text-center">
    <span class="flex h-14 w-14 items-center justify-center rounded-full bg-accent-50 text-accent-700">
      <Icon name="search" :size="26" />
    </span>
    <h1 class="mt-4 font-display text-2xl font-semibold tracking-tight">Page not found</h1>
    <p class="mt-1 text-sm text-ink-muted">
      That link doesn’t go anywhere. Let’s get you back to today.
    </p>
    <RouterLink to="/" class="btn-primary mt-6">
      <Icon name="home" :size="16" /> Back to today
    </RouterLink>
  </div>
</template>

<script setup>
import Icon from '../components/Icon.vue'
</script>
