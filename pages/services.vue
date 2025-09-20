<template>
  <div>
    <!-- Hero Section -->
    <UISection background="blue" padding="lg">
      <UIContainer>
        <div class="text-center max-w-3xl mx-auto">
          <h1 class="text-4xl md:text-5xl font-bold text-neutral-800 mb-6">
            Our Services
          </h1>
          <p class="text-xl text-neutral-600">
            Comprehensive technology solutions designed to drive your business forward with innovation, efficiency, and expertise.
          </p>
        </div>
      </UIContainer>
    </UISection>

    <!-- Services Section -->
    <UISection padding="xl" background="white">
      <UIContainer>
        <div class="space-y-20">
          <div
            v-for="(service, index) in siteContent.services"
            :key="service.title"
            class="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center"
            :class="{ 'lg:grid-flow-col-dense': index % 2 === 1 }"
          >
            <!-- Service Content -->
            <div :class="{ 'lg:col-start-2': index % 2 === 1 }">
              <div class="flex items-center mb-6">
                <div class="flex items-center justify-center w-16 h-16 bg-accent-100 rounded-lg mr-4">
                  <UIIcon
                    :name="service.icon"
                    size="lg"
                    class="text-accent-600"
                  />
                </div>
                <h2 class="text-3xl md:text-4xl font-bold text-neutral-800">
                  {{ service.title }}
                </h2>
              </div>
              
              <p class="text-lg text-neutral-600 mb-6 leading-relaxed">
                {{ service.detailedDescription }}
              </p>
              
              <div class="mb-8">
                <h3 class="text-lg font-semibold text-neutral-800 mb-4">
                  Technologies & Tools
                </h3>
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="tech in service.technologies"
                    :key="tech"
                    class="px-3 py-1 bg-neutral-100 text-neutral-700 rounded-full text-sm font-medium"
                  >
                    {{ tech }}
                  </span>
                </div>
              </div>
              
              <UIButton
                tag="NuxtLink"
                to="/contact"
                variant="primary"
                size="md"
              >
                Get Started
              </UIButton>
            </div>

            <!-- Service Image/Illustration -->
            <div :class="{ 'lg:col-start-1 lg:row-start-1': index % 2 === 1 }">
              <div class="relative">
                <img
                  :src="`https://picsum.photos/600/400?random=${index + 20}`"
                  :alt="`${service.title} illustration`"
                  class="w-full h-80 object-cover rounded-lg shadow-lg"
                  loading="lazy"
                />
                <div class="absolute inset-0 bg-gradient-to-br from-blue-500/20 to-purple-600/20 rounded-lg"></div>
              </div>
            </div>
          </div>
        </div>
      </UIContainer>
    </UISection>

    <!-- Process Section -->
    <UISection padding="lg" background="gray">
      <UIContainer>
        <div class="text-center mb-16">
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            Our Process
          </h2>
          <p class="text-lg text-gray-600 max-w-2xl mx-auto">
            We follow a proven methodology to ensure successful project delivery and client satisfaction.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          <div
            v-for="(step, index) in processSteps"
            :key="step.title"
            class="text-center"
          >
            <div class="flex items-center justify-center w-16 h-16 bg-primary-600 text-white rounded-full mx-auto mb-4 text-xl font-bold">
              {{ index + 1 }}
            </div>
            <h3 class="text-xl font-semibold text-gray-900 mb-3">
              {{ step.title }}
            </h3>
            <p class="text-gray-600">
              {{ step.description }}
            </p>
          </div>
        </div>
      </UIContainer>
    </UISection>

    <!-- Why Choose Us Section -->
    <UISection padding="lg" background="white">
      <UIContainer>
        <div class="text-center mb-16">
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            Why Choose VerionLabs?
          </h2>
          <p class="text-lg text-gray-600 max-w-2xl mx-auto">
            Our commitment to excellence and innovation sets us apart in the competitive technology landscape.
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <UICard
            v-for="benefit in benefits"
            :key="benefit.title"
            :title="benefit.title"
            :description="benefit.description"
            :icon="benefit.icon"
            variant="bordered"
            hover
            class="text-center"
          />
        </div>
      </UIContainer>
    </UISection>

    <!-- CTA Section -->
    <UISection padding="lg" background="blue">
      <UIContainer>
        <div class="text-center max-w-3xl mx-auto">
          <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
            Ready to Get Started?
          </h2>
          <p class="text-lg text-gray-600 mb-8">
            Let's discuss your project requirements and explore how we can help transform your business with technology.
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <UIButton
              tag="NuxtLink"
              to="/contact"
              variant="primary"
              size="lg"
            >
              Start Your Project
            </UIButton>
            <UIButton
              tag="NuxtLink"
              to="/demos"
              variant="outline"
              size="lg"
            >
              View Our Work
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
  title: `Services - ${siteContent.company.name}`,
  meta: [
    {
      name: 'description',
      content: 'Explore our comprehensive technology services including cloud architecture, AI & machine learning, and custom web application development.'
    },
    {
      property: 'og:title',
      content: `Services - ${siteContent.company.name}`
    },
    {
      property: 'og:description',
      content: 'Comprehensive technology solutions designed to drive your business forward with innovation, efficiency, and expertise.'
    },
    {
      property: 'og:type',
      content: 'website'
    },
    {
      property: 'og:url',
      content: `https://${siteContent.company.domain}/services`
    }
  ]
})

// Process steps data
const processSteps = [
  {
    title: 'Discovery',
    description: 'We analyze your business needs, technical requirements, and project goals to create a comprehensive strategy.'
  },
  {
    title: 'Design',
    description: 'Our team designs the architecture, user experience, and technical specifications for your solution.'
  },
  {
    title: 'Development',
    description: 'We build your solution using best practices, modern technologies, and agile development methodologies.'
  },
  {
    title: 'Deployment',
    description: 'We deploy, test, and optimize your solution to ensure smooth operation and maximum performance.'
  }
]

// Benefits data
const benefits = [
  {
    title: 'Expert Team',
    description: 'Our experienced developers and architects bring deep expertise across multiple technologies and industries.',
    icon: 'brain'
  },
  {
    title: 'Proven Process',
    description: 'We follow industry best practices and agile methodologies to ensure successful project delivery.',
    icon: 'code'
  },
  {
    title: 'Scalable Solutions',
    description: 'Our solutions are designed to grow with your business, ensuring long-term value and flexibility.',
    icon: 'cloud'
  },
  {
    title: 'Quality Assurance',
    description: 'Rigorous testing and quality control processes ensure reliable, secure, and high-performing solutions.',
    icon: 'code'
  },
  {
    title: 'Ongoing Support',
    description: 'We provide continuous support and maintenance to keep your systems running smoothly.',
    icon: 'cloud'
  },
  {
    title: 'Innovation Focus',
    description: 'We stay at the forefront of technology trends to deliver cutting-edge solutions for our clients.',
    icon: 'brain'
  }
]
</script>