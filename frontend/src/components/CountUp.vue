<template>
  <span>{{ display }}<slot /></span>
</template>

<script setup>
import { onMounted, onUnmounted, ref, watch } from 'vue'

const props = defineProps({
  value: { type: Number, default: 0 },
  duration: { type: Number, default: 650 },
  decimals: { type: Number, default: 0 },
})

const display = ref(props.value)
let frame = null

function prefersReduced() {
  return (
    typeof window !== 'undefined' &&
    window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  )
}

function animate(to) {
  if (frame) cancelAnimationFrame(frame)
  const from = Number(display.value) || 0
  const target = Number(to) || 0

  if (prefersReduced() || from === target) {
    display.value = target.toFixed(props.decimals)
    return
  }

  const start = performance.now()
  const tick = (now) => {
    const progress = Math.min(1, (now - start) / props.duration)
    // easeOutCubic
    const eased = 1 - Math.pow(1 - progress, 3)
    const current = from + (target - from) * eased
    display.value = current.toFixed(props.decimals)
    if (progress < 1) frame = requestAnimationFrame(tick)
  }
  frame = requestAnimationFrame(tick)
}

watch(() => props.value, animate)
onMounted(() => animate(props.value))
onUnmounted(() => frame && cancelAnimationFrame(frame))
</script>
