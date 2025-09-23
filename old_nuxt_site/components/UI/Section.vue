<template>
  <section :class="sectionClasses">
    <slot />
  </section>
</template>

<script setup lang="ts">
interface Props {
  padding?: 'sm' | 'md' | 'lg' | 'xl' | 'none'
  background?: 'white' | 'gray' | 'blue' | 'transparent'
  id?: string
}

const props = withDefaults(defineProps<Props>(), {
  padding: 'lg',
  background: 'transparent'
})

const sectionClasses = computed(() => {
  const paddings = {
    none: '',
    sm: 'py-8 md:py-12',
    md: 'py-12 md:py-16',
    lg: 'py-16 md:py-24',
    xl: 'py-24 md:py-32'
  }
  
  const backgrounds = {
    transparent: '',
    white: 'bg-white',
    gray: 'bg-gray-50',
    blue: 'bg-slate-50'
  }
  
  return [paddings[props.padding], backgrounds[props.background]].filter(Boolean).join(' ')
})
</script>