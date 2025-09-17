<template>
  <div>
    <!-- Hero Section -->
    <UISection background="blue" padding="xl">
      <UIContainer>
        <div class="text-center max-w-4xl mx-auto relative">
          <!-- Floating Particles Background -->
          <div class="floating-particles" ref="particlesContainer"></div>
          
          <!-- Cursor Glow Effect -->
          <div class="cursor-glow" ref="cursorGlow"></div>
          
          <!-- Main Hero Title with Advanced Animations -->
          <div class="relative z-10">
            <h1 
              ref="heroTitle"
              class="hero-title magnetic-effect text-shadow-glow text-4xl md:text-6xl lg:text-7xl font-bold mb-6 leading-tight"
              @mouseenter="handleTitleHover"
              @mouseleave="handleTitleLeave"
              @mousemove="handleMouseMove"
            >
              <span 
                v-for="(word, index) in titleWords" 
                :key="index"
                :class="[
                  'word-reveal',
                  (word === 'Modern' || word === 'Business') ? 'accent-word' : ''
                ]"
                :style="{ 'animation-delay': `${index * 0.1}s` }"
              >
                {{ word }}
                <span v-if="index < titleWords.length - 1" class="mr-4"></span>
              </span>
            </h1>
            
            <!-- Typewriter Subtitle -->
            <div class="relative mb-8 min-h-16 md:min-h-20 flex items-center justify-center px-4">
              <p 
                ref="subtitle"
                class="typewriter text-xl md:text-2xl text-gray-600 max-w-4xl mx-auto text-center leading-relaxed"
                :class="{ 'typing-active': isTypingActive }"
              >
                {{ currentSubtitle }}
              </p>
            </div>
          </div>
          
          <!-- CTA Button with Pulse Effect -->
          <UIButton
            tag="NuxtLink"
            to="/services"
            variant="primary"
            size="lg"
            icon="arrow-right"
            icon-position="right"
            class="magnetic-effect transform hover:scale-105 transition-all duration-300 shadow-2xl hover:shadow-blue-500/25"
            @mouseenter="createRippleEffect"
          >
            {{ siteContent.homepage.hero.cta }}
          </UIButton>
        </div>
      </UIContainer>
    </UISection>

    <!-- Mission/Value Proposition Section -->
    <UISection padding="lg" background="white">
      <UIContainer>
        <div class="max-w-3xl mx-auto text-center">
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            {{ siteContent.homepage.mission.title }}
          </h2>
          <p class="text-lg text-gray-600 leading-relaxed">
            {{ siteContent.homepage.mission.content }}
          </p>
        </div>
      </UIContainer>
    </UISection>

    <!-- Services Overview Section -->
    <UISection padding="lg" background="gray">
      <UIContainer>
        <div class="text-center mb-16">
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Our Expertise
          </h2>
          <p class="text-lg text-gray-600 max-w-2xl mx-auto">
            Discover how our specialized services can transform your business with cutting-edge technology solutions.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-8">
          <UICard
            v-for="service in siteContent.services"
            :key="service.title"
            :title="service.title"
            :description="service.description"
            :icon="service.icon"
            hover
            class="text-center"
          >
            <template #actions>
              <UIButton
                tag="NuxtLink"
                to="/services"
                variant="outline"
                size="sm"
              >
                Learn More
              </UIButton>
            </template>
          </UICard>
        </div>
      </UIContainer>
    </UISection>

    <!-- Featured Demos Section -->
    <UISection padding="lg" background="white">
      <UIContainer>
        <div class="text-center mb-16">
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Featured Projects
          </h2>
          <p class="text-lg text-gray-600 max-w-2xl mx-auto">
            Explore some of our latest work showcasing innovative solutions across various industries.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-12">
          <UICard
            v-for="demo in featuredDemos"
            :key="demo.title"
            :title="demo.title"
            :description="demo.description"
            :image="demo.image"
            :tags="demo.tags"
            hover
          >
            <template #actions>
              <UIButton
                :href="demo.liveDemo"
                variant="outline"
                size="sm"
                icon="external-link"
                icon-position="right"
                class="mr-2"
              >
                Live Demo
              </UIButton>
              <UIButton
                :href="demo.github"
                variant="ghost"
                size="sm"
                icon="code"
                icon-position="left"
              >
                Code
              </UIButton>
            </template>
          </UICard>
        </div>

        <div class="text-center">
          <UIButton
            tag="NuxtLink"
            to="/demos"
            variant="outline"
            size="lg"
          >
            View All Projects
          </UIButton>
        </div>
      </UIContainer>
    </UISection>

    <!-- Contact CTA Section -->
    <UISection padding="lg" background="blue">
      <UIContainer>
        <div class="text-center max-w-3xl mx-auto">
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            {{ siteContent.homepage.contactCta.title }}
          </h2>
          <p class="text-lg text-gray-600 mb-8">
            {{ siteContent.homepage.contactCta.description }}
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <UIButton
              tag="NuxtLink"
              to="/contact"
              variant="primary"
              size="lg"
            >
              {{ siteContent.homepage.contactCta.buttonText }}
            </UIButton>
            <UIButton
              :href="`mailto:${siteContent.company.email}`"
              variant="outline"
              size="lg"
              icon="envelope"
              icon-position="left"
            >
              Send Email
            </UIButton>
          </div>
        </div>
      </UIContainer>
    </UISection>
  </div>
</template>

<script setup lang="ts">
import { siteContent } from '~/content/site'

// SEO Meta tags
useHead({
  title: `${siteContent.company.name} - ${siteContent.homepage.hero.headline}`,
  meta: [
    {
      name: 'description',
      content: siteContent.company.description
    },
    {
      property: 'og:title',
      content: `${siteContent.company.name} - ${siteContent.homepage.hero.headline}`
    },
    {
      property: 'og:description',
      content: siteContent.company.description
    },
    {
      property: 'og:type',
      content: 'website'
    },
    {
      property: 'og:url',
      content: `https://${siteContent.company.domain}`
    },
    {
      name: 'twitter:card',
      content: 'summary_large_image'
    },
    {
      name: 'twitter:title',
      content: `${siteContent.company.name} - ${siteContent.homepage.hero.headline}`
    },
    {
      name: 'twitter:description',
      content: siteContent.company.description
    }
  ]
})

// Get featured demos (limit to 3)
const featuredDemos = computed(() => {
  return siteContent.demos.filter(demo => demo.featured).slice(0, 3)
})

// Hero animation refs and state
const heroTitle = ref<HTMLElement>()
const subtitle = ref<HTMLElement>()
const particlesContainer = ref<HTMLElement>()
const cursorGlow = ref<HTMLElement>()

// Animation state
const isTypingActive = ref(false)
const currentSubtitle = ref('')
const subtitleTexts = [
  'Your vision, our expertise, endless possibilities',
  'Transform ideas into powerful digital experiences.',
  'Drive business growth with modern technology.',
  'Unlock new opportunities for innovation.'
]
let subtitleIndex = 0

// Title words for individual animation
const titleWords = computed(() => {
  return siteContent.homepage.hero.headline.split(' ')
})

// Typewriter effect for subtitle
const typewriterEffect = () => {
  const text = subtitleTexts[subtitleIndex]
  let charIndex = 0
  
  currentSubtitle.value = ''
  isTypingActive.value = true
  
  const typeInterval = setInterval(() => {
    if (charIndex < text.length) {
      currentSubtitle.value += text.charAt(charIndex)
      charIndex++
    } else {
      clearInterval(typeInterval)
      isTypingActive.value = false
      setTimeout(() => {
        // Wait 2.5 seconds then start erasing
        const eraseInterval = setInterval(() => {
          if (currentSubtitle.value.length > 0) {
            currentSubtitle.value = currentSubtitle.value.slice(0, -1)
          } else {
            clearInterval(eraseInterval)
            subtitleIndex = (subtitleIndex + 1) % subtitleTexts.length
            setTimeout(typewriterEffect, 500)
          }
        }, 25) // Slightly faster erasing
      }, 2500) // Shorter display time to accommodate longer text
    }
  }, 40) // Slightly faster typing for longer text
}

// Particle system
const createParticle = () => {
  if (!particlesContainer.value) return
  
  const particle = document.createElement('div')
  particle.className = 'particle'
  
  const size = Math.random() * 6 + 2
  particle.style.width = `${size}px`
  particle.style.height = `${size}px`
  particle.style.left = `${Math.random() * 100}%`
  particle.style.animationDuration = `${Math.random() * 3 + 4}s`
  particle.style.animationDelay = `${Math.random() * 2}s`
  
  particlesContainer.value.appendChild(particle)
  
  // Remove particle after animation
  setTimeout(() => {
    if (particle.parentNode) {
      particle.parentNode.removeChild(particle)
    }
  }, 7000)
}

// Cursor glow effect
const handleMouseMove = (event: MouseEvent) => {
  if (!cursorGlow.value) return
  
  const rect = heroTitle.value?.getBoundingClientRect()
  if (!rect) return
  
  const x = event.clientX - rect.left - 100
  const y = event.clientY - rect.top - 100
  
  cursorGlow.value.style.transform = `translate(${x}px, ${y}px)`
}

const handleTitleHover = () => {
  if (cursorGlow.value) {
    cursorGlow.value.style.opacity = '1'
  }
}

const handleTitleLeave = () => {
  if (cursorGlow.value) {
    cursorGlow.value.style.opacity = '0'
  }
}

// Ripple effect for button
const createRippleEffect = (event: Event) => {
  const button = event.currentTarget as HTMLElement
  const ripple = document.createElement('span')
  const rect = button.getBoundingClientRect()
  const size = Math.max(rect.width, rect.height)
  
  ripple.style.width = ripple.style.height = `${size}px`
  ripple.style.left = `${(event as MouseEvent).clientX - rect.left - size / 2}px`
  ripple.style.top = `${(event as MouseEvent).clientY - rect.top - size / 2}px`
  ripple.classList.add('ripple')
  
  // Add ripple styles
  ripple.style.position = 'absolute'
  ripple.style.borderRadius = '50%'
  ripple.style.background = 'rgba(255, 255, 255, 0.6)'
  ripple.style.transform = 'scale(0)'
  ripple.style.animation = 'ripple 0.6s linear'
  ripple.style.pointerEvents = 'none'
  
  button.style.position = 'relative'
  button.style.overflow = 'hidden'
  button.appendChild(ripple)
  
  setTimeout(() => {
    ripple.remove()
  }, 600)
}

// Initialize animations on mount
onMounted(() => {
  // Start typewriter effect
  setTimeout(() => {
    typewriterEffect()
  }, 1000)
  
  // Start particle system
  const particleInterval = setInterval(() => {
    createParticle()
  }, 300)
  
  // Cleanup on unmount
  onUnmounted(() => {
    clearInterval(particleInterval)
  })
  
  // Add ripple animation to CSS
  const style = document.createElement('style')
  style.textContent = `
    @keyframes ripple {
      to {
        transform: scale(4);
        opacity: 0;
      }
    }
  `
  document.head.appendChild(style)
})
</script>