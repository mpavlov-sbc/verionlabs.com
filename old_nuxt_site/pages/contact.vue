<template>
  <div>
    <!-- Hero Section -->
    <UISection background="blue" padding="lg">
      <UIContainer>
        <div class="text-center max-w-3xl mx-auto">
          <h1 class="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Get In Touch
          </h1>
          <p class="text-xl text-gray-600">
            Ready to transform your business with innovative technology solutions? Let's start the conversation.
          </p>
        </div>
      </UIContainer>
    </UISection>

    <!-- Contact Form & Info Section -->
    <UISection padding="xl" background="white">
      <UIContainer>
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-16">
          <!-- Contact Form -->
          <div>
            <h2 class="text-2xl md:text-3xl font-bold text-gray-900 mb-6">
              Send Us a Message
            </h2>
            <p class="text-gray-600 mb-8">
              Fill out the form below and we'll get back to you within 24 hours to discuss your project requirements.
            </p>

            <form @submit.prevent="submitForm" class="space-y-6">
              <!-- Full Name -->
              <div>
                <label for="fullName" class="block text-sm font-medium text-gray-700 mb-2">
                  Full Name *
                </label>
                <input
                  id="fullName"
                  v-model="form.fullName"
                  type="text"
                  required
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
                  :class="{ 'border-red-500': errors.fullName }"
                  placeholder="Enter your full name"
                  @blur="validateField('fullName')"
                />
                <p v-if="errors.fullName" class="mt-1 text-sm text-red-600">
                  {{ errors.fullName }}
                </p>
              </div>

              <!-- Email -->
              <div>
                <label for="email" class="block text-sm font-medium text-gray-700 mb-2">
                  Email Address *
                </label>
                <input
                  id="email"
                  v-model="form.email"
                  type="email"
                  required
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
                  :class="{ 'border-red-500': errors.email }"
                  placeholder="Enter your email address"
                  @blur="validateField('email')"
                />
                <p v-if="errors.email" class="mt-1 text-sm text-red-600">
                  {{ errors.email }}
                </p>
              </div>

              <!-- Subject -->
              <div>
                <label for="subject" class="block text-sm font-medium text-gray-700 mb-2">
                  Subject *
                </label>
                <select
                  id="subject"
                  v-model="form.subject"
                  required
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200"
                  :class="{ 'border-red-500': errors.subject }"
                  @blur="validateField('subject')"
                >
                  <option value="">Select a subject</option>
                  <option value="cloud-architecture">Cloud Architecture</option>
                  <option value="ai-ml">AI & Machine Learning</option>
                  <option value="web-development">Custom Web Applications</option>
                  <option value="consultation">General Consultation</option>
                  <option value="partnership">Partnership Opportunity</option>
                  <option value="other">Other</option>
                </select>
                <p v-if="errors.subject" class="mt-1 text-sm text-red-600">
                  {{ errors.subject }}
                </p>
              </div>

              <!-- Message -->
              <div>
                <label for="message" class="block text-sm font-medium text-gray-700 mb-2">
                  Message *
                </label>
                <textarea
                  id="message"
                  v-model="form.message"
                  required
                  rows="5"
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors duration-200 resize-vertical"
                  :class="{ 'border-red-500': errors.message }"
                  placeholder="Tell us about your project, requirements, or questions..."
                  @blur="validateField('message')"
                />
                <p v-if="errors.message" class="mt-1 text-sm text-red-600">
                  {{ errors.message }}
                </p>
              </div>

              <!-- Submit Button -->
              <UIButton
                type="submit"
                variant="primary"
                size="lg"
                :disabled="isSubmitting"
                class="w-full"
              >
                <span v-if="isSubmitting">Sending...</span>
                <span v-else>Send Message</span>
              </UIButton>

              <!-- Success/Error Messages -->
              <div v-if="submitStatus.type" class="p-4 rounded-lg" :class="{
                'bg-green-50 text-green-800 border border-green-200': submitStatus.type === 'success',
                'bg-red-50 text-red-800 border border-red-200': submitStatus.type === 'error'
              }">
                {{ submitStatus.message }}
              </div>
            </form>
          </div>

          <!-- Contact Information -->
          <div>
            <h2 class="text-2xl md:text-3xl font-bold text-gray-900 mb-6">
              Contact Information
            </h2>
            <p class="text-gray-600 mb-8">
              Prefer to reach out directly? Here are all the ways you can get in touch with us.
            </p>

            <div class="space-y-6">
              <!-- Email -->
              <div class="flex items-start space-x-4">
                <div class="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg flex-shrink-0">
                  <UIIcon name="envelope" size="md" class="text-blue-600" />
                </div>
                <div>
                  <h3 class="text-lg font-semibold text-gray-900 mb-1">
                    Email
                  </h3>
                  <a
                    :href="`mailto:${siteContent.company.email}`"
                    class="text-blue-600 hover:text-blue-700 transition-colors duration-200"
                  >
                    {{ siteContent.company.email }}
                  </a>
                  <p class="text-gray-600 text-sm mt-1">
                    We typically respond within 24 hours
                  </p>
                </div>
              </div>

              <!-- Address -->
              <div class="flex items-start space-x-4">
                <div class="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg flex-shrink-0">
                  <UIIcon name="map-pin" size="md" class="text-blue-600" />
                </div>
                <div>
                  <h3 class="text-lg font-semibold text-gray-900 mb-1">
                    Address
                  </h3>
                  <p class="text-gray-600">
                    {{ siteContent.company.address }}
                  </p>
                </div>
              </div>

              <!-- Phone (if available) -->
              <div v-if="siteContent.company.phone" class="flex items-start space-x-4">
                <div class="flex items-center justify-center w-12 h-12 bg-blue-100 rounded-lg flex-shrink-0">
                  <UIIcon name="phone" size="md" class="text-blue-600" />
                </div>
                <div>
                  <h3 class="text-lg font-semibold text-gray-900 mb-1">
                    Phone
                  </h3>
                  <a
                    :href="`tel:${siteContent.company.phone}`"
                    class="text-blue-600 hover:text-blue-700 transition-colors duration-200"
                  >
                    {{ siteContent.company.phone }}
                  </a>
                </div>
              </div>
            </div>

            <!-- Social Links -->
            <div class="mt-8 pt-8 border-t border-gray-200">
              <h3 class="text-lg font-semibold text-gray-900 mb-4">
                Follow Us
              </h3>
              <div class="flex space-x-4">
                <a
                  :href="siteContent.social.linkedin"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="flex items-center justify-center w-10 h-10 bg-gray-100 text-gray-600 rounded-lg hover:bg-blue-100 hover:text-blue-600 transition-colors duration-200"
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
                  class="flex items-center justify-center w-10 h-10 bg-gray-100 text-gray-600 rounded-lg hover:bg-gray-900 hover:text-white transition-colors duration-200"
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
                  class="flex items-center justify-center w-10 h-10 bg-gray-100 text-gray-600 rounded-lg hover:bg-blue-400 hover:text-white transition-colors duration-200"
                  aria-label="Twitter"
                >
                  <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M6.29 18.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0020 3.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.073 4.073 0 01.8 7.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 010 16.407a11.616 11.616 0 006.29 1.84" />
                  </svg>
                </a>
              </div>
            </div>
          </div>
        </div>
      </UIContainer>
    </UISection>

    <!-- FAQ Section -->
    <UISection padding="lg" background="gray">
      <UIContainer>
        <div class="max-w-3xl mx-auto">
          <div class="text-center mb-12">
            <h2 class="text-3xl md:text-4xl font-bold text-gray-900 mb-6">
              Frequently Asked Questions
            </h2>
            <p class="text-lg text-gray-600">
              Get quick answers to common questions about our services and process.
            </p>
          </div>

          <div class="space-y-6">
            <div
              v-for="faq in faqs"
              :key="faq.question"
              class="bg-white rounded-lg shadow-sm"
            >
              <button
                @click="toggleFaq(faq.id)"
                class="w-full px-6 py-4 text-left flex items-center justify-between focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-lg"
              >
                <span class="text-lg font-semibold text-gray-900">
                  {{ faq.question }}
                </span>
                <UIIcon
                  name="chevron-down"
                  size="sm"
                  class="text-gray-500 transition-transform duration-200"
                  :class="{ 'rotate-180': openFaq === faq.id }"
                />
              </button>
              <Transition
                enter-active-class="transition-all duration-300 ease-out"
                enter-from-class="opacity-0 max-h-0"
                enter-to-class="opacity-100 max-h-96"
                leave-active-class="transition-all duration-200 ease-in"
                leave-from-class="opacity-100 max-h-96"
                leave-to-class="opacity-0 max-h-0"
              >
                <div v-if="openFaq === faq.id" class="px-6 pb-4 overflow-hidden">
                  <p class="text-gray-600 leading-relaxed">
                    {{ faq.answer }}
                  </p>
                </div>
              </Transition>
            </div>
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
  title: `Contact Us - ${siteContent.company.name}`,
  meta: [
    {
      name: 'description',
      content: 'Get in touch with VerionLabs to discuss your project requirements and discover how we can help transform your business with innovative technology solutions.'
    },
    {
      property: 'og:title',
      content: `Contact Us - ${siteContent.company.name}`
    },
    {
      property: 'og:description',
      content: 'Ready to transform your business with innovative technology solutions? Let\'s start the conversation.'
    },
    {
      property: 'og:type',
      content: 'website'
    },
    {
      property: 'og:url',
      content: `https://${siteContent.company.domain}/contact`
    }
  ]
})

// Form state
const form = reactive({
  fullName: '',
  email: '',
  subject: '',
  message: ''
})

// Form validation errors
const errors = reactive({
  fullName: '',
  email: '',
  subject: '',
  message: ''
})

// Form submission state
const isSubmitting = ref(false)
const submitStatus = reactive({
  type: '',
  message: ''
})

// FAQ state
const openFaq = ref(null)

// Form validation
const validateField = (field: string) => {
  errors[field] = ''
  
  switch (field) {
    case 'fullName':
      if (!form.fullName.trim()) {
        errors.fullName = 'Full name is required'
      } else if (form.fullName.trim().length < 2) {
        errors.fullName = 'Full name must be at least 2 characters'
      }
      break
      
    case 'email':
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!form.email.trim()) {
        errors.email = 'Email is required'
      } else if (!emailRegex.test(form.email)) {
        errors.email = 'Please enter a valid email address'
      }
      break
      
    case 'subject':
      if (!form.subject) {
        errors.subject = 'Please select a subject'
      }
      break
      
    case 'message':
      if (!form.message.trim()) {
        errors.message = 'Message is required'
      } else if (form.message.trim().length < 10) {
        errors.message = 'Message must be at least 10 characters'
      }
      break
  }
}

// Validate entire form
const validateForm = () => {
  Object.keys(form).forEach(field => validateField(field))
  return Object.values(errors).every(error => !error)
}

// Submit form
const submitForm = async () => {
  if (!validateForm()) {
    return
  }
  
  isSubmitting.value = true
  submitStatus.type = ''
  submitStatus.message = ''
  
  try {
    // TODO: Replace with your actual Formspree endpoint
    // Sign up at https://formspree.io and replace 'YOUR_FORM_ID' with your actual form ID
    const response = await fetch('https://formspree.io/f/YOUR_FORM_ID', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: form.fullName,
        email: form.email,
        subject: form.subject,
        message: form.message,
        _replyto: form.email
      })
    })
    
    if (response.ok) {
      submitStatus.type = 'success'
      submitStatus.message = 'Thank you for your message! We\'ll get back to you within 24 hours.'
      
      // Reset form
      Object.keys(form).forEach(key => {
        form[key] = ''
      })
    } else {
      throw new Error('Failed to send message')
    }
  } catch (error) {
    submitStatus.type = 'error'
    submitStatus.message = 'Sorry, there was an error sending your message. Please try again or contact us directly at ' + siteContent.company.email
  } finally {
    isSubmitting.value = false
  }
}

// FAQ toggle
const toggleFaq = (id: number) => {
  openFaq.value = openFaq.value === id ? null : id
}

// FAQ data
const faqs = [
  {
    id: 1,
    question: 'How long does a typical project take?',
    answer: 'Project timelines vary depending on complexity and scope. Simple web applications may take 4-8 weeks, while complex enterprise solutions can take 3-6 months. We provide detailed timelines during the discovery phase.'
  },
  {
    id: 2,
    question: 'Do you provide ongoing support and maintenance?',
    answer: 'Yes, we offer comprehensive support and maintenance packages to ensure your solution continues to run smoothly. This includes security updates, bug fixes, performance monitoring, and feature enhancements.'
  },
  {
    id: 3,
    question: 'What technologies do you specialize in?',
    answer: 'We specialize in modern web technologies (Vue.js, React, Node.js), cloud platforms (AWS, Azure, Google Cloud), AI/ML frameworks (Python, TensorFlow), and enterprise solutions. Our team stays current with the latest industry trends.'
  },
  {
    id: 4,
    question: 'Can you work with our existing team?',
    answer: 'Absolutely! We frequently collaborate with in-house teams, providing expertise in specific areas or augmenting your development capacity. We adapt to your preferred communication tools and workflows.'
  },
  {
    id: 5,
    question: 'How do you ensure project success?',
    answer: 'We follow agile methodologies with regular check-ins, transparent communication, and iterative development. Our experienced project managers ensure deadlines are met and requirements are clearly understood throughout the process.'
  }
]
</script>