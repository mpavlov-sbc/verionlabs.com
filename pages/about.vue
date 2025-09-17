<template>
  <div>
    <!-- Hero Section -->
    <UISection background="blue" padding="lg">
      <UIContainer>
        <div class="text-center max-w-3xl mx-auto">
          <h1 class="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            About VerionLabs
          </h1>
          <p class="text-xl text-gray-600">
            Meet the team behind innovative software solutions that transform businesses and drive technological advancement.
          </p>
        </div>
      </UIContainer>
    </UISection>

    <!-- Company Story Section -->
    <UISection padding="lg" background="white">
      <UIContainer>
        <div class="max-w-4xl mx-auto">
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-8 text-center">
            {{ siteContent.about.story.title }}
          </h2>
          <div class="space-y-6">
            <p
              v-for="paragraph in siteContent.about.story.content"
              :key="paragraph"
              class="text-lg text-gray-600 leading-relaxed"
            >
              {{ paragraph }}
            </p>
          </div>
        </div>
      </UIContainer>
    </UISection>

    <!-- Vision Section -->
    <UISection padding="lg" background="gray">
      <UIContainer>
        <div class="max-w-4xl mx-auto text-center">
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            {{ siteContent.about.vision.title }}
          </h2>
          <p class="text-xl text-gray-600 leading-relaxed">
            {{ siteContent.about.vision.content }}
          </p>
        </div>
      </UIContainer>
    </UISection>

    <!-- Values Section -->
    <UISection padding="lg" background="white">
      <UIContainer>
        <div class="text-center mb-16">
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            Our Values
          </h2>
          <p class="text-lg text-gray-600 max-w-2xl mx-auto">
            The principles that guide our work and define our commitment to excellence.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <UICard
            v-for="value in companyValues"
            :key="value.title"
            :title="value.title"
            :description="value.description"
            :icon="value.icon"
            variant="bordered"
            hover
            class="text-center"
          />
        </div>
      </UIContainer>
    </UISection>

    <!-- Team Section -->
    <UISection padding="xl" background="gray">
      <UIContainer>
        <div class="text-center mb-16">
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            Meet Our Team
          </h2>
          <p class="text-lg text-gray-600 max-w-2xl mx-auto">
            Our diverse team of experts brings together decades of experience in cutting-edge technologies and innovative problem-solving.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          <div
            v-for="member in siteContent.team"
            :key="member.name"
            class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 overflow-hidden"
          >
            <div class="aspect-square">
              <NuxtImg
                :src="member.image"
                :alt="`${member.name} - ${member.role}`"
                class="w-full h-full object-cover"
                format="webp"
                loading="lazy"
              />
            </div>
            
            <div class="p-6">
              <h3 class="text-xl font-bold text-gray-900 mb-1">
                {{ member.name }}
              </h3>
              <p class="text-blue-600 font-medium mb-3">
                {{ member.role }}
              </p>
              <p class="text-gray-600 text-sm leading-relaxed mb-4">
                {{ member.bio }}
              </p>
              
              <div class="flex space-x-3">
                <a
                  v-if="member.linkedin"
                  :href="member.linkedin"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-gray-400 hover:text-blue-600 transition-colors duration-200"
                  aria-label="LinkedIn Profile"
                >
                  <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.338 16.338H13.67V12.16c0-.995-.017-2.277-1.387-2.277-1.39 0-1.601 1.086-1.601 2.207v4.248H8.014v-8.59h2.559v1.174h.037c.356-.675 1.227-1.387 2.526-1.387 2.703 0 3.203 1.778 3.203 4.092v4.711zM5.005 6.575a1.548 1.548 0 11-.003-3.096 1.548 1.548 0 01.003 3.096zm-1.337 9.763H6.34v-8.59H3.667v8.59zM17.668 1H2.328C1.595 1 1 1.581 1 2.298v15.403C1 18.418 1.595 19 2.328 19h15.34c.734 0 1.332-.582 1.332-1.299V2.298C19 1.581 18.402 1 17.668 1z" clip-rule="evenodd" />
                  </svg>
                </a>
                <a
                  v-if="member.github"
                  :href="member.github"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="text-gray-400 hover:text-gray-900 transition-colors duration-200"
                  aria-label="GitHub Profile"
                >
                  <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M10 0C4.477 0 0 4.484 0 10.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0020 10.017C20 4.484 15.522 0 10 0z" clip-rule="evenodd" />
                  </svg>
                </a>
              </div>
            </div>
          </div>
        </div>
      </UIContainer>
    </UISection>

    <!-- Stats Section -->
    <UISection padding="lg" background="white">
      <UIContainer>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
          <div
            v-for="stat in companyStats"
            :key="stat.label"
            class="space-y-2"
          >
            <div class="text-3xl md:text-4xl font-bold text-blue-600">
              {{ stat.value }}
            </div>
            <div class="text-gray-600 font-medium">
              {{ stat.label }}
            </div>
          </div>
        </div>
      </UIContainer>
    </UISection>

    <!-- CTA Section -->
    <UISection padding="lg" background="blue">
      <UIContainer>
        <div class="text-center max-w-3xl mx-auto">
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            Join Our Journey
          </h2>
          <p class="text-lg text-gray-600 mb-8">
            Whether you're looking for innovative solutions for your business or want to be part of our growing team, we'd love to hear from you.
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <UIButton
              tag="NuxtLink"
              to="/contact"
              variant="primary"
              size="lg"
            >
              Work With Us
            </UIButton>
            <UIButton
              :href="`mailto:careers@${siteContent.company.domain.replace('www.', '')}`"
              variant="outline"
              size="lg"
            >
              Join Our Team
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
  title: `About Us - ${siteContent.company.name}`,
  meta: [
    {
      name: 'description',
      content: 'Learn about VerionLabs, our team of experts, and our mission to transform businesses with innovative software solutions.'
    },
    {
      property: 'og:title',
      content: `About Us - ${siteContent.company.name}`
    },
    {
      property: 'og:description',
      content: 'Meet the team behind innovative software solutions that transform businesses and drive technological advancement.'
    },
    {
      property: 'og:type',
      content: 'website'
    },
    {
      property: 'og:url',
      content: `https://${siteContent.company.domain}/about`
    }
  ]
})

// Company values data
const companyValues = [
  {
    title: 'Innovation',
    description: 'We continuously explore new technologies and methodologies to deliver cutting-edge solutions that drive business growth.',
    icon: 'brain'
  },
  {
    title: 'Quality',
    description: 'Every project we deliver meets the highest standards of quality, reliability, and performance through rigorous testing and best practices.',
    icon: 'code'
  },
  {
    title: 'Collaboration',
    description: 'We work closely with our clients as partners, ensuring transparent communication and shared success throughout every project.',
    icon: 'cloud'
  },
  {
    title: 'Expertise',
    description: 'Our team brings deep technical knowledge and industry experience to solve complex challenges with elegant solutions.',
    icon: 'brain'
  },
  {
    title: 'Scalability',
    description: 'We design solutions that grow with your business, ensuring long-term value and adaptability to changing needs.',
    icon: 'cloud'
  },
  {
    title: 'Security',
    description: 'Security is built into every solution we develop, protecting your data and ensuring compliance with industry standards.',
    icon: 'code'
  }
]

// Company statistics
const companyStats = [
  {
    value: '50+',
    label: 'Projects Delivered'
  },
  {
    value: '25+',
    label: 'Happy Clients'
  },
  {
    value: '5+',
    label: 'Years Experience'
  },
  {
    value: '99.9%',
    label: 'Uptime'
  }
]
</script>