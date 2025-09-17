// SEO composable for consistent meta tag management
import { siteContent } from '~/content/site'

export const useSEO = (options: {
    title?: string
    description?: string
    image?: string
    url?: string
    type?: string
    keywords?: string[]
}) => {

    const title = options.title || `${siteContent.company.name} - Innovative Software Solutions`
    const description = options.description || siteContent.company.description
    const image = options.image || '/og-image.jpg'
    const url = options.url || `https://${siteContent.company.domain}`
    const type = options.type || 'website'

    useHead({
        title,
        meta: [
            { name: 'description', content: description },
            { name: 'keywords', content: options.keywords?.join(', ') || 'software development, web applications, cloud architecture, AI, machine learning' },

            // Open Graph
            { property: 'og:title', content: title },
            { property: 'og:description', content: description },
            { property: 'og:image', content: image },
            { property: 'og:url', content: url },
            { property: 'og:type', content: type },
            { property: 'og:site_name', content: siteContent.company.name },

            // Twitter Card
            { name: 'twitter:card', content: 'summary_large_image' },
            { name: 'twitter:title', content: title },
            { name: 'twitter:description', content: description },
            { name: 'twitter:image', content: image },

            // Additional SEO meta tags
            { name: 'author', content: siteContent.company.name },
            { name: 'robots', content: 'index, follow' },
            { name: 'googlebot', content: 'index, follow' },
            { 'http-equiv': 'X-UA-Compatible', content: 'IE=edge' },
            { name: 'format-detection', content: 'telephone=no' }
        ],
        link: [
            { rel: 'canonical', href: url }
        ]
    })
}