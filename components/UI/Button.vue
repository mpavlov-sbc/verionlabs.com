<template>
  <component
    :is="tag"
    :class="buttonClasses"
    :disabled="disabled"
    :type="type"
    @click="$emit('click', $event)"
  >
    <Icon v-if="icon && iconPosition === 'left'" :name="icon" class="w-5 h-5 mr-2" />
    <slot />
    <Icon v-if="icon && iconPosition === 'right'" :name="icon" class="w-5 h-5 ml-2" />
  </component>
</template>

<script setup lang="ts">
interface Props {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  icon?: string
  iconPosition?: 'left' | 'right'
  tag?: 'button' | 'a' | 'NuxtLink'
  type?: 'button' | 'submit' | 'reset'
  to?: string
  href?: string
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'primary',
  size: 'md',
  disabled: false,
  iconPosition: 'left',
  tag: 'button',
  type: 'button'
})

defineEmits<{
  click: [event: Event]
}>()

const buttonClasses = computed(() => {
  const base = 'inline-flex items-center justify-center font-semibold rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed'
  
  const variants = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white focus:ring-blue-500',
    secondary: 'bg-gray-200 hover:bg-gray-300 text-gray-900 focus:ring-gray-500',
    outline: 'border-2 border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white focus:ring-blue-500',
    ghost: 'text-blue-600 hover:bg-blue-50 focus:ring-blue-500'
  }
  
  const sizes = {
    sm: 'py-2 px-4 text-sm',
    md: 'py-3 px-6 text-base',
    lg: 'py-4 px-8 text-lg'
  }
  
  return [base, variants[props.variant], sizes[props.size]].join(' ')
})
</script>