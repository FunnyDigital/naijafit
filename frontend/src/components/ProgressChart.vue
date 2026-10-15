<template>
  <div>
    <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" :style="{ height: `${height}px` }">
      <line
        v-if="goalY !== null"
        :x1="PAD"
        :y1="goalY"
        :x2="W - PAD"
        :y2="goalY"
        stroke="#a8a29e"
        stroke-width="1"
        stroke-dasharray="4 4"
      />

      <template v-if="type === 'bar'">
        <rect
          v-for="(point, index) in points"
          :key="index"
          :x="barX(index)"
          :y="y(point.value)"
          :width="barWidth"
          :height="Math.max(1, H - PAD - y(point.value))"
          rx="3"
          :fill="color"
          :opacity="point.value >= (goal ?? 0) ? 1 : 0.45"
        />
      </template>

      <template v-else>
        <path v-if="points.length > 1" :d="areaPath" :fill="color" opacity="0.12" />
        <path
          v-if="points.length > 1"
          :d="linePath"
          fill="none"
          :stroke="color"
          stroke-width="2.5"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <circle
          v-for="(point, index) in points"
          :key="index"
          :cx="x(index)"
          :cy="y(point.value)"
          r="3"
          :fill="color"
        />
      </template>
    </svg>

    <div v-if="points.length" class="mt-2 flex justify-between text-[11px] text-ink-faint">
      <span>{{ points[0].label }}</span>
      <span v-if="points.length > 2">{{ points[Math.floor(points.length / 2)].label }}</span>
      <span>{{ points[points.length - 1].label }}</span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  points: { type: Array, default: () => [] },
  type: { type: String, default: 'line' }, // line | bar
  height: { type: Number, default: 150 },
  color: { type: String, default: '#10b981' },
  goal: { type: Number, default: null },
})

const W = 320
const H = 140
const PAD = 12

const values = computed(() => props.points.map((point) => Number(point.value) || 0))

const bounds = computed(() => {
  if (!values.value.length) return { lo: 0, hi: 1 }
  let lo = Math.min(...values.value)
  let hi = Math.max(...values.value)
  if (props.goal != null) {
    lo = Math.min(lo, props.goal)
    hi = Math.max(hi, props.goal)
  }
  if (hi === lo) {
    hi += 1
    lo -= 1
  }
  const span = hi - lo
  return { lo: lo - span * 0.1, hi: hi + span * 0.1 }
})

function x(index) {
  const n = props.points.length
  if (n <= 1) return W / 2
  return PAD + (index / (n - 1)) * (W - PAD * 2)
}

function y(value) {
  const { lo, hi } = bounds.value
  const span = hi - lo || 1
  return H - PAD - ((Number(value) - lo) / span) * (H - PAD * 2)
}

const goalY = computed(() => (props.goal != null ? y(props.goal) : null))

const linePath = computed(() =>
  props.points.map((point, index) => `${index === 0 ? 'M' : 'L'} ${x(index)} ${y(point.value)}`).join(' '),
)

const areaPath = computed(
  () => `${linePath.value} L ${x(props.points.length - 1)} ${H - PAD} L ${x(0)} ${H - PAD} Z`,
)

const barWidth = computed(() => {
  const n = props.points.length || 1
  return Math.max(3, ((W - PAD * 2) / n) * 0.55)
})

function barX(index) {
  const n = props.points.length || 1
  const slot = (W - PAD * 2) / n
  return PAD + slot * index + (slot - barWidth.value) / 2
}
</script>
