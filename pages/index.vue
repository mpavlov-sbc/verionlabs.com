<template>
  <div>
    <!-- Hero Section -->
    <UISection background="blue" padding="xl">
      <UIContainer>
        <div class="text-center max-w-4xl mx-auto">
          <h1 class="text-4xl md:text-6xl font-bold text-gray-900 mb-6 animate-fade-in">
            {{ siteContent.homepage.hero.headline }}
          </h1>
          <p class="text-xl md:text-2xl text-gray-600 mb-8 animate-slide-up">
            {{ siteContent.homepage.hero.subheadline }}
          </p>
          <UIButton
            tag="NuxtLink"
            to="/services"
            variant="primary"
            size="lg"
            icon="arrow-right"
            icon-position="right"
            class="animate-slide-up"
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
</script>