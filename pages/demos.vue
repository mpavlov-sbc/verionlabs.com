<template>
  <div>
    <!-- Hero Section -->
    <UISection background="blue" padding="lg">
      <UIContainer>
        <div class="text-center max-w-3xl mx-auto">
          <h1 class="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Project Showcase
          </h1>
          <p class="text-xl text-gray-600">
            Explore our portfolio of innovative solutions that have transformed businesses across various industries.
          </p>
        </div>
      </UIContainer>
    </UISection>

    <!-- Filter Section -->
    <UISection padding="md" background="white">
      <UIContainer>
        <div class="flex flex-wrap gap-4 justify-center">
          <UIButton
            v-for="tag in uniqueTags"
            :key="tag"
            :variant="selectedTag === tag ? 'primary' : 'ghost'"
            size="sm"
            @click="setFilter(tag)"
          >
            {{ tag }}
          </UIButton>
        </div>
      </UIContainer>
    </UISection>

    <!-- Projects Grid -->
    <UISection padding="lg" background="gray">
      <UIContainer>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <Transition
            v-for="demo in filteredDemos"
            :key="demo.title"
            appear
            enter-active-class="transition-all duration-500 ease-out"
            enter-from-class="opacity-0 scale-95"
            enter-to-class="opacity-100 scale-100"
          >
            <UICard
              :title="demo.title"
              :description="demo.description"
              :image="demo.image"
              :tags="demo.tags"
              hover
              class="h-full"
            >
              <template #actions>
                <div class="flex flex-col sm:flex-row gap-2 w-full">
                  <UIButton
                    :href="demo.liveDemo"
                    variant="primary"
                    size="sm"
                    icon="external-link"
                    icon-position="right"
                    class="flex-1"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Live Demo
                  </UIButton>
                  <UIButton
                    :href="demo.github"
                    variant="outline"
                    size="sm"
                    icon="code"
                    icon-position="left"
                    class="flex-1"
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    GitHub
                  </UIButton>
                </div>
              </template>
            </UICard>
          </Transition>
        </div>

        <!-- No results message -->
        <div v-if="filteredDemos.length === 0" class="text-center py-16">
          <UIIcon name="code" size="xl" class="text-gray-400 mx-auto mb-4" />
          <h3 class="text-xl font-semibold text-gray-900 mb-2">
            No projects found
          </h3>
          <p class="text-gray-600 mb-6">
            Try selecting a different technology filter to see more projects.
          </p>
          <UIButton
            variant="outline"
            @click="clearFilter"
          >
            Show All Projects
          </UIButton>
        </div>
      </UIContainer>
    </UISection>

    <!-- Technologies Section -->
    <UISection padding="lg" background="white">
      <UIContainer>
        <div class="text-center mb-16">
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            Technologies We Use
          </h2>
          <p class="text-lg text-gray-600 max-w-2xl mx-auto">
            Our projects leverage cutting-edge technologies and best practices to deliver exceptional results.
          </p>
        </div>

        <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-6">
          <div
            v-for="tech in popularTechnologies"
            :key="tech"
            class="flex flex-col items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors duration-200"
          >
            <div class="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center mb-2">
              <span class="text-white font-bold text-sm">{{ tech.charAt(0) }}</span>
            </div>
            <span class="text-sm font-medium text-gray-900">{{ tech }}</span>
          </div>
        </div>
      </UIContainer>
    </UISection>

    <!-- CTA Section -->
    <UISection padding="lg" background="blue">
      <UIContainer>
        <div class="text-center max-w-3xl mx-auto">
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            Have a Project in Mind?
          </h2>
          <p class="text-lg text-gray-600 mb-8">
            Let's collaborate to bring your vision to life with our expertise and innovative approach.
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <UIButton
              tag="NuxtLink"
              to="/contact"
              variant="primary"
              size="lg"
            >
              Discuss Your Project
            </UIButton>
            <UIButton
              tag="NuxtLink"
              to="/services"
              variant="outline"
              size="lg"
            >
              Explore Our Services
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
  title: `Project Demos - ${siteContent.company.name}`,
  meta: [
    {
      name: 'description',
      content: 'Explore our portfolio of innovative software solutions and see how we transform businesses with cutting-edge technology.'
    },
    {
      property: 'og:title',
      content: `Project Demos - ${siteContent.company.name}`
    },
    {
      property: 'og:description',
      content: 'Portfolio of innovative solutions that have transformed businesses across various industries.'
    },
    {
      property: 'og:type',
      content: 'website'
    },
    {
      property: 'og:url',
      content: `https://${siteContent.company.domain}/demos`
    }
  ]
})

// Filter state
const selectedTag = ref('All')

// Get all unique tags from demos
const uniqueTags = computed(() => {
  const allTags = siteContent.demos.flatMap(demo => demo.tags)
  const unique = [...new Set(allTags)].sort()
  return ['All', ...unique]
})

// Filter demos based on selected tag
const filteredDemos = computed(() => {
  if (selectedTag.value === 'All') {
    return siteContent.demos
  }
  return siteContent.demos.filter(demo => 
    demo.tags.includes(selectedTag.value)
  )
})

// Get popular technologies (most used across projects)
const popularTechnologies = computed(() => {
  const techCount = {}
  siteContent.demos.forEach(demo => {
    demo.tags.forEach(tag => {
      techCount[tag] = (techCount[tag] || 0) + 1
    })
  })
  
  return Object.entries(techCount)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 12)
    .map(([tech]) => tech)
})

// Filter functions
const setFilter = (tag: string) => {
  selectedTag.value = tag
}

const clearFilter = () => {
  selectedTag.value = 'All'
}

// Reset filter when component mounts
onMounted(() => {
  selectedTag.value = 'All'
})
</script>