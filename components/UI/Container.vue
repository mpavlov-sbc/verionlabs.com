<template>
  <div :class="containerClasses">
    <slot />
  </div>
</template>

<script setup lang="ts">
interface Props {
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  padding?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'lg',
  padding: true
})

const containerClasses = computed(() => {
  const sizes = {
    sm: 'max-w-2xl',
    md: 'max-w-4xl',
    lg: 'max-w-7xl',
    xl: 'max-w-8xl',
    full: 'max-w-full'
  }
  
  const base = 'mx-auto'
  const padding = props.padding ? 'px-4 sm:px-6 lg:px-8' : ''
  
  return [base, sizes[props.size], padding].filter(Boolean).join(' ')
})
</script>