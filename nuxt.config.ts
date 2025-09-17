// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
    devtools: { enabled: true },
    modules: [
        '@nuxtjs/tailwindcss',
        '@nuxt/image',
        '@nuxtjs/sitemap',
        '@nuxtjs/robots',
        '@vueuse/nuxt'
    ],

    // App configuration
    app: {
        head: {
            title: 'VerionLabs - Innovative Software Solutions',
            meta: [
                { charset: 'utf-8' },
                { name: 'viewport', content: 'width=device-width, initial-scale=1' },
                { name: 'description', content: 'VerionLabs provides innovative software solutions for modern businesses, specializing in cloud architecture, AI & machine learning, and custom web applications.' },
                { name: 'author', content: 'VerionLabs' },
                { property: 'og:type', content: 'website' },
                { property: 'og:title', content: 'VerionLabs - Innovative Software Solutions' },
                { property: 'og:description', content: 'Professional software solutions for startups to enterprise-level businesses.' },
                { property: 'og:url', content: 'https://verionlabs.com' },
                { name: 'twitter:card', content: 'summary_large_image' },
                { name: 'twitter:title', content: 'VerionLabs - Innovative Software Solutions' },
                { name: 'twitter:description', content: 'Professional software solutions for startups to enterprise-level businesses.' }
            ],
            link: [
                { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
            ]
        }
    },

    // SSG configuration for GitHub Pages
    nitro: {
        prerender: {
            routes: ['/', '/services', '/demos', '/about', '/contact']
        }
    },

    // Tailwind CSS configuration
    tailwindcss: {
        cssPath: '~/assets/css/main.css'
    },

    // Image optimization
    image: {
        // Configure for static generation
        provider: 'ipx'
    },

    // SEO modules configuration
    site: {
        url: 'https://verionlabs.com',
        name: 'VerionLabs'
    },

    sitemap: {
        hostname: 'https://verionlabs.com',
        gzip: true
    },

    robots: {
        UserAgent: '*',
        Allow: '/',
        Sitemap: 'https://verionlabs.com/sitemap.xml'
    },

    // Performance optimizations
    experimental: {
        payloadExtraction: false
    },

    // CSS configuration
    css: ['~/assets/css/main.css']
})