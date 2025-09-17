<template>
  <div :class="cardClasses">
    <div v-if="image" class="mb-4">
      <img
        :src="image"
        :alt="imageAlt || title"
        :class="imageClasses"
        loading="lazy"
      />
    </div>
    
    <div v-if="icon" class="mb-4">
      <Icon :name="icon" :class="iconClasses" />
    </div>
    
    <div class="flex-1">
      <h3 v-if="title" :class="titleClasses">
        {{ title }}
      </h3>
      
      <p v-if="description" :class="descriptionClasses">
        {{ description }}
      </p>
      
      <div v-if="tags && tags.length" class="flex flex-wrap gap-2 mt-4">
        <span
          v-for="tag in tags"
          :key="tag"
          class="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded"
        >
          {{ tag }}
        </span>
      </div>
      
      <div v-if="$slots.default" class="mt-4">
        <slot />
      </div>
      
      <div v-if="$slots.actions" class="mt-6 flex gap-3">
        <slot name="actions" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title?: string
  description?: string
  image?: string
  imageAlt?: string
  icon?: string
  tags?: string[]
  variant?: 'default' | 'bordered' | 'elevated'
  hover?: boolean
  padding?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'default',
  hover: true,
  padding: 'md'
})

const cardClasses = computed(() => {
  const base = 'bg-white rounded-lg flex flex-col'
  
  const variants = {
    default: 'shadow-md',
    bordered: 'border border-gray-200',
    elevated: 'shadow-lg'
  }
  
  const paddings = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8'
  }
  
  const hover = props.hover ? 'hover:shadow-lg transition-shadow duration-200' : ''
  
  return [base, variants[props.variant], paddings[props.padding], hover].filter(Boolean).join(' ')
})

const imageClasses = computed(() => {
  return 'w-full h-48 object-cover rounded-lg'
})

const iconClasses = computed(() => {
  return 'w-12 h-12 text-blue-600'
})

const titleClasses = computed(() => {
  return 'text-xl font-bold text-gray-900 mb-2'
})

const descriptionClasses = computed(() => {
  return 'text-gray-600 leading-relaxed'
})
</script>