<template>
  <div class="space-y-3">
    <div v-for="row in rows" :key="row" class="card flex items-center gap-3 p-3">
      <div class="h-12 w-12 shrink-0 animate-pulse rounded-2xl bg-line/60" />
      <div class="flex-1 space-y-2">
        <div class="h-3 w-2/5 animate-pulse rounded-full bg-line/60" />
        <div class="h-2.5 w-3/5 animate-pulse rounded-full bg-line/50" />
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  rows: { type: Number, default: 4 },
})
</script>
