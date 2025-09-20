<template>
  <div class="min-h-screen flex flex-col">
    <!-- Header -->
    <header class="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
      <UIContainer>
        <nav class="flex items-center justify-between h-16">
          <!-- Logo and Company Name -->
          <NuxtLink to="/" class="flex items-center space-x-3 hover:opacity-80 transition-opacity">
            <img
              src="/logo.svg"
              alt="VerionLabs Logo"
              class="h-8 w-8"
            />
            <span class="text-xl font-bold text-gray-900">{{ siteContent.company.name }}</span>
          </NuxtLink>

          <!-- Desktop Navigation -->
          <div class="hidden md:flex items-center space-x-8">
            <NuxtLink
              v-for="item in siteContent.navigation.items"
              :key="item.name"
              :to="item.href"
              class="text-gray-600 hover:text-gray-900 font-medium transition-colors duration-200"
              :class="{ 'text-blue-600': $route.path === item.href }"
            >
              {{ item.name }}
            </NuxtLink>
            
            <UIButton
              tag="NuxtLink"
              to="/contact"
              variant="primary"
              size="sm"
            >
              Contact Us
            </UIButton>
          </div>

          <!-- Mobile Menu Button -->
          <button
            @click="toggleMobileMenu"
            class="md:hidden p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500"
            :aria-expanded="isMobileMenuOpen"
            aria-label="Toggle navigation menu"
          >
            <UIIcon
              :name="isMobileMenuOpen ? 'x-mark' : 'menu'"
              size="md"
            />
          </button>
        </nav>

        <!-- Mobile Navigation -->
        <Transition
          enter-active-class="transition-all duration-300 ease-out"
          enter-from-class="opacity-0 -translate-y-2"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition-all duration-200 ease-in"
          leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 -translate-y-2"
        >
          <div v-if="isMobileMenuOpen" class="md:hidden border-t border-gray-200 bg-white">
            <div class="px-2 py-4 space-y-3">
              <NuxtLink
                v-for="item in siteContent.navigation.items"
                :key="item.name"
                :to="item.href"
                class="block px-3 py-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-50 font-medium transition-colors duration-200"
                :class="{ 'text-blue-600 bg-blue-50': $route.path === item.href }"
                @click="closeMobileMenu"
              >
                {{ item.name }}
              </NuxtLink>
              <div class="px-3 pt-2">
                <UIButton
                  tag="NuxtLink"
                  to="/contact"
                  variant="primary"
                  size="sm"
                  class="w-full"
                  @click="closeMobileMenu"
                >
                  Contact Us
                </UIButton>
              </div>
            </div>
          </div>
        </Transition>
      </UIContainer>
    </header>

    <!-- Development Progress Badge -->
    <div class="bg-gradient-to-r from-primary-600 to-accent-600 text-white py-2 px-4 text-center relative overflow-hidden">
      <div class="relative z-10 flex items-center justify-center space-x-2">
        <svg class="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
        </svg>
        <span class="text-sm font-medium">
          Development in Progress - Opening Soon!
        </span>
      </div>
      <!-- Animated background effect -->
      <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent animate-pulse"></div>
    </div>

    <!-- Main Content -->
    <main class="flex-1">
      <slot />
    </main>

    <!-- Footer -->
    <footer class="bg-gray-900 text-white">
      <UIContainer>
        <div class="py-12">
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <!-- Company Info -->
            <div class="lg:col-span-2">
              <div class="flex items-center space-x-3 mb-4">
                                  <img
                    src="/logo-white.svg"
                    alt="VerionLabs"
                    class="h-8 w-8"
                  />
                <span class="text-xl font-bold">{{ siteContent.company.name }}</span>
              </div>
              <p class="text-gray-300 max-w-md mb-4">
                {{ siteContent.company.description }}
              </p>
              <div class="flex space-x-4">
                <a
                  :href="siteContent.social.linkedin"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-gray-400 hover:text-white transition-colors duration-200"
                  aria-label="LinkedIn"
                >
                  <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.338 16.338H13.67V12.16c0-.995-.017-2.277-1.387-2.277-1.39 0-1.601 1.086-1.601 2.207v4.248H8.014v-8.59h2.559v1.174h.037c.356-.675 1.227-1.387 2.526-1.387 2.703 0 3.203 1.778 3.203 4.092v4.711zM5.005 6.575a1.548 1.548 0 11-.003-3.096 1.548 1.548 0 01.003 3.096zm-1.337 9.763H6.34v-8.59H3.667v8.59zM17.668 1H2.328C1.595 1 1 1.581 1 2.298v15.403C1 18.418 1.595 19 2.328 19h15.34c.734 0 1.332-.582 1.332-1.299V2.298C19 1.581 18.402 1 17.668 1z" clip-rule="evenodd" />
                  </svg>
                </a>
                <a
                  :href="siteContent.social.github"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-gray-400 hover:text-white transition-colors duration-200"
                  aria-label="GitHub"
                >
                  <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 0C4.477 0 0 4.484 0 10.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0020 10.017C20 4.484 15.522 0 10 0z" clip-rule="evenodd" />
                  </svg>
                </a>
                <a
                  :href="siteContent.social.twitter"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-gray-400 hover:text-white transition-colors duration-200"
                  aria-label="Twitter"
                >
                  <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M6.29 18.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0020 3.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.073 4.073 0 01.8 7.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 010 16.407a11.616 11.616 0 006.29 1.84" />
                  </svg>
                </a>
              </div>
            </div>

            <!-- Quick Links -->
            <div>
              <h3 class="text-lg font-semibold mb-4">Quick Links</h3>
              <ul class="space-y-2">
                <li v-for="item in siteContent.navigation.items" :key="item.name">
                  <NuxtLink
                    :to="item.href"
                    class="text-gray-300 hover:text-white transition-colors duration-200"
                  >
                    {{ item.name }}
                  </NuxtLink>
                </li>
              </ul>
            </div>

            <!-- Contact Info -->
            <div>
              <h3 class="text-lg font-semibold mb-4">Contact</h3>
              <div class="space-y-2 text-gray-300">
                <div class="flex items-center space-x-2">
                  <UIIcon name="envelope" size="sm" />
                  <a
                    :href="`mailto:${siteContent.company.email}`"
                    class="hover:text-white transition-colors duration-200"
                  >
                    {{ siteContent.company.email }}
                  </a>
                </div>
                <div class="flex items-start space-x-2">
                  <UIIcon name="map-pin" size="sm" class="mt-0.5" />
                  <span>{{ siteContent.company.address }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Copyright -->
        <div class="border-t border-gray-800 py-6">
          <div class="flex flex-col md:flex-row justify-between items-center">
            <p class="text-gray-400 text-sm">
              © {{ currentYear }} {{ siteContent.company.name }}. All rights reserved.
            </p>
            <div class="flex space-x-6 mt-4 md:mt-0">
              <a href="#" class="text-gray-400 hover:text-white text-sm transition-colors duration-200">
                Privacy Policy
              </a>
              <a href="#" class="text-gray-400 hover:text-white text-sm transition-colors duration-200">
                Terms of Service
              </a>
            </div>
          </div>
        </div>
      </UIContainer>
    </footer>
  </div>
</template>

<script setup>
import { siteContent } from '~/content/site'

// Mobile menu state
const isMobileMenuOpen = ref(false)

// Current year for copyright
const currentYear = new Date().getFullYear()

// Mobile menu functions
const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

const closeMobileMenu = () => {
  isMobileMenuOpen.value = false
}

// Close mobile menu when route changes
watch(() => useRoute().path, () => {
  closeMobileMenu()
})

// Close mobile menu when clicking outside
onMounted(() => {
  const handleClickOutside = (event) => {
    if (isMobileMenuOpen.value && !event.target.closest('nav')) {
      closeMobileMenu()
    }
  }
  
  document.addEventListener('click', handleClickOutside)
  
  onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside)
  })
})
</script>