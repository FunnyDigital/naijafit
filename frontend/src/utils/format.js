import { computed } from 'vue'

import { profileState } from '../composables/useProfile'

const KG_TO_LB = 2.2046226218

export function round(value, decimals = 0) {
  const factor = 10 ** decimals
  return Math.round((Number(value) || 0) * factor) / factor
}

export function clamp(value, lo, hi) {
  return Math.min(hi, Math.max(lo, value))
}

export function kgToLb(kg) {
  return kg * KG_TO_LB
}

export function lbToKg(lb) {
  return lb / KG_TO_LB
}

export function cmToIn(cm) {
  return cm / 2.54
}

export function inToCm(inches) {
  return inches * 2.54
}

export function formatWeight(kg, units = 'metric', decimals = 1) {
  if (kg == null) return '—'
  if (units === 'imperial') return `${round(kgToLb(kg), decimals)} lb`
  return `${round(kg, decimals)} kg`
}

export function formatHeight(cm, units = 'metric') {
  if (cm == null) return '—'
  if (units === 'imperial') {
    const totalInches = cmToIn(cm)
    const feet = Math.floor(totalInches / 12)
    const inches = Math.round(totalInches - feet * 12)
    return `${feet}′ ${inches}″`
  }
  return `${round(cm, 0)} cm`
}

export function formatVolume(ml, units = 'metric') {
  if (units === 'imperial') return `${round(ml / 29.5735, 0)} fl oz`
  return `${round(ml / 1000, 2)} L`
}

export function useUnits() {
  const units = computed(() => profileState.profile?.units || 'metric')
  return {
    units,
    formatWeight: (kg) => formatWeight(kg, units.value),
    formatHeight: (cm) => formatHeight(cm, units.value),
    formatVolume: (ml) => formatVolume(ml, units.value),
  }
}
