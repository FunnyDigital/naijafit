<template>
  <span class="inline-flex shrink-0" v-html="svg" />
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  name: { type: String, required: true },
  size: { type: [Number, String], default: 20 },
  strokeWidth: { type: [Number, String], default: 1.75 },
})

const ICONS = {
  // navigation
  home: '<path d="m3 10 9-7 9 7"/><path d="M5 9v12h14V9"/><path d="M10 21v-6h4v6"/>',
  dumbbell: '<path d="M4 9v6M7 7v10M17 7v10M20 9v6M7 12h10"/>',
  bowl: '<path d="M2 12h20"/><path d="M4 12a8 8 0 0 0 16 0"/><path d="M12 9V6"/>',
  chart: '<path d="M3 3v18h18"/><path d="m7 15 4-5 3 3 5-7"/>',
  user: '<circle cx="12" cy="8" r="4"/><path d="M4 21v-1a6 6 0 0 1 6-6h4a6 6 0 0 1 6 6v1"/>',
  leaf: '<path d="M11 20A7 7 0 0 1 4 13c0-6 6-9 16-9 0 10-4 15-9 16Z"/><path d="M4 20c3-3 6-5 10-6"/>',
  pulse: '<path d="M3 12h4l2-5 3 10 2-5h7"/>',

  // stats
  flame: '<path d="M12 3s5 4.5 5 9a5 5 0 0 1-10 0c0-2 1-3.5 2-4.5 0 1.5 1 2.5 2 2.5 1.5 0 2-1.5 1-7Z"/>',
  droplet: '<path d="M12 3s6 6.5 6 10.5a6 6 0 0 1-12 0C6 9.5 12 3 12 3Z"/>',
  timer: '<circle cx="12" cy="13" r="8"/><path d="M12 9v4l2 2"/><path d="M9 2h6"/>',
  target: '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/>',
  scale: '<rect x="3" y="6" width="18" height="15" rx="4"/><path d="M8 11h8"/><path d="M12 6V3"/>',
  trending: '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
  trophy: '<path d="M8 4h8v5a4 4 0 0 1-8 0V4Z"/><path d="M8 6H5a3 3 0 0 0 3 3"/><path d="M16 6h3a3 3 0 0 1-3 3"/><path d="M12 13v4M9 20h6"/>',

  // actions
  plus: '<path d="M12 5v14M5 12h14"/>',
  minus: '<path d="M5 12h14"/>',
  check: '<path d="m20 6-11 11-5-5"/>',
  close: '<path d="M18 6 6 18M6 6l12 12"/>',
  chevronLeft: '<path d="m15 18-6-6 6-6"/>',
  chevronRight: '<path d="m9 18 6-6-6-6"/>',
  chevronDown: '<path d="m6 9 6 6 6-6"/>',
  chevronUp: '<path d="m18 15-6-6-6 6"/>',
  arrowRight: '<path d="M5 12h14"/><path d="m13 6 6 6-6 6"/>',
  arrowLeft: '<path d="M19 12H5"/><path d="m11 18-6-6 6-6"/>',
  play: '<path d="M8 5v14l11-7z"/>',
  refresh: '<path d="M21 12a9 9 0 1 1-3-6.7"/><path d="M21 4v5h-5"/>',
  swap: '<path d="M16 3l4 4-4 4"/><path d="M20 7H9a5 5 0 0 0 0 10h6"/><path d="M8 21l-4-4 4-4"/><path d="M4 17h11a5 5 0 0 0 0-10h-1"/>',
  download: '<path d="M12 4v12"/><path d="m7 11 5 5 5-5"/><path d="M5 20h14"/>',
  upload: '<path d="M12 16V4"/><path d="m7 9 5-5 5 5"/><path d="M5 20h14"/>',
  trash: '<path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/>',
  edit: '<path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/>',
  filter: '<path d="M3 5h18l-7 8v6l-4-2v-4Z"/>',
  menu: '<path d="M4 6h16M4 12h16M4 18h16"/>',
  userPlus: '<circle cx="9" cy="8" r="4"/><path d="M2 21v-1a6 6 0 0 1 6-6h2a6 6 0 0 1 6 6v1"/><path d="M19 8v6M16 11h6"/>',
  bookmark: '<path d="M6 3h12a1 1 0 0 1 1 1v17l-7-4-7 4V4a1 1 0 0 1 1-1Z"/>',
  circleCheck: '<circle cx="12" cy="12" r="9"/><path d="m8.5 12.5 2.5 2.5 4.5-5"/>',
  logout: '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><path d="m16 17 5-5-5-5"/><path d="M21 12H9"/>',

  // info
  info: '<circle cx="12" cy="12" r="9"/><path d="M12 11v5M12 8h.01"/>',
  alert: '<path d="M12 3 2 20h20L12 3Z"/><path d="M12 10v4M12 17h.01"/>',
  sparkles: '<path d="M12 3l1.6 4.4L18 9l-4.4 1.6L12 15l-1.6-4.4L6 9l4.4-1.6L12 3Z"/><path d="M19 15l.8 2.2L22 18l-2.2.8L19 21l-.8-2.2L16 18l2.2-.8L19 15Z"/>',
  star: '<path d="m12 3 2.6 5.6 6 .8-4.4 4.2 1.1 6-5.3-2.9L6.7 19.6l1.1-6L3.4 9.4l6-.8Z"/>',
  heart: '<path d="M12 20s-7-4.6-9-9a4.5 4.5 0 0 1 8-3.2A4.5 4.5 0 0 1 21 11c-2 4.4-9 9-9 9Z"/>',
  egg: '<path d="M12 3c3.5 0 6 4.5 6 8.5A6 6 0 0 1 6 11.5C6 7.5 8.5 3 12 3Z"/>',
  apple: '<path d="M12 7c2-2 5-2 6.5.5 1.8 3-.3 8.3-2.9 11-1.3 1.4-2.6 1.4-3.6 1.4s-2.3 0-3.6-1.4C5.8 15.8 3.7 10.5 5.5 7.5 7 5 10 5 12 7Z"/><path d="M12 7V4"/><path d="M12 4c1-1.6 2.6-1.7 3.2-1.2"/>',
  fish: '<path d="M3 12c3-4 7-6 11-5 3 .7 5 3 7 5-2 2-4 4.3-7 5-4 1-8-1-11-5Z"/><path d="M3 12l4-3v6l-4-3Z"/><circle cx="16" cy="11" r="1"/>',
  utensils: '<path d="M4 3v7a3 3 0 0 0 6 0V3"/><path d="M7 10v11"/><path d="M18 3c-2 1.5-2 5.5 0 7v11"/>',
  clock: '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
  list: '<path d="M8 6h13M8 12h13M8 18h13"/><path d="M3 6h.01M3 12h.01M3 18h.01"/>',
}

const svg = computed(() => {
  const body = ICONS[props.name] || ICONS.info
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${props.size}" height="${props.size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="${props.strokeWidth}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${body}</svg>`
})
</script>
