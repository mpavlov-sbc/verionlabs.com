# VerionLabs Website

A professional, modern corporate website built with Nuxt 3, Tailwind CSS, and deployed as a static site optimized for GitHub Pages.

## 🚀 Features

- **Modern Tech Stack**: Built with Nuxt 3, Vue 3, and Tailwind CSS
- **SEO Optimized**: Comprehensive meta tags, sitemap, and robots.txt
- **Responsive Design**: Mobile-first responsive design that works on all devices
- **Performance Focused**: Optimized for high Google Lighthouse scores
- **Component-Based**: Reusable UI components for maintainable code
- **Type-Safe**: TypeScript support for better development experience
- **Accessibility**: WCAG compliant with proper semantic HTML and ARIA labels
- **Contact Form**: Integrated contact form with client-side validation
- **Content Management**: Centralized content configuration for easy updates

## 📁 Project Structure

```
verionlabs-website/
├── assets/
│   └── css/
│       └── main.css          # Global styles and Tailwind directives
├── components/
│   └── UI/                   # Reusable UI components
│       ├── Button.vue
│       ├── Card.vue
│       ├── Container.vue
│       ├── Icon.vue
│       └── Section.vue
├── composables/
│   └── useSEO.ts            # SEO composable for meta tags
├── content/
│   └── site.ts              # Centralized content configuration
├── layouts/
│   └── default.vue          # Default layout with header and footer
├── pages/
│   ├── index.vue            # Homepage
│   ├── services.vue         # Services page
│   ├── demos.vue            # Project demos page
│   ├── about.vue            # About page
│   └── contact.vue          # Contact page
├── public/                  # Static assets
│   ├── robots.txt
│   ├── site.webmanifest
│   └── favicon.ico
├── nuxt.config.ts           # Nuxt configuration
├── tailwind.config.js       # Tailwind CSS configuration
└── package.json             # Dependencies and scripts
```

## 🛠️ Installation & Setup

### Prerequisites

- Node.js 18+ 
- npm or yarn

### 1. Clone and Install Dependencies

```bash
# Clone the repository
git clone <repository-url>
cd verionlabs-website

# Install dependencies
npm install
```

### 2. Environment Setup

The project is configured to work out of the box. All content is managed through the `content/site.ts` file.

### 3. Development

```bash
# Start development server
npm run dev

# Open http://localhost:3000 in your browser
```

### 4. Build for Production

```bash
# Generate static site
npm run generate

# Preview production build
npm run preview
```

## 📝 Content Management

All website content is centralized in `content/site.ts`. This includes:

- Company information
- Team member profiles
- Service descriptions
- Project demos
- Navigation items
- Social media links

To update content, simply edit the appropriate sections in this file.

### Adding Team Members

```typescript
// In content/site.ts
team: [
  {
    name: "Your Name",
    role: "Your Role",
    bio: "Your bio...",
    image: "https://picsum.photos/400/400?random=5",
    linkedin: "https://linkedin.com/in/yourprofile",
    github: "https://github.com/yourusername"
  }
]
```

### Adding Services

```typescript
// In content/site.ts
services: [
  {
    title: "Service Name",
    description: "Brief description",
    detailedDescription: "Detailed description...",
    technologies: ["Tech1", "Tech2", "Tech3"],
    icon: "icon-name"
  }
]
```

## 🎨 Customization

### Colors and Branding

Update the brand colors in `tailwind.config.js`:

```javascript
theme: {
  extend: {
    colors: {
      primary: {
        // Update these values
        500: '#3b82f6',
        600: '#2563eb',
        700: '#1d4ed8',
      }
    }
  }
}
```

### Fonts

The project uses Inter font from Google Fonts. To change:

1. Update the font import in `app.html`
2. Update the font family in `tailwind.config.js`

### Logo

Replace the logo files in the `public/` directory:
- `logo.svg` - Main logo
- `logo-white.svg` - White version for dark backgrounds
- `favicon.ico` - Favicon
- `apple-touch-icon.png` - Apple touch icon

## 📧 Contact Form Setup

The contact form is configured to work with Formspree.io:

1. Sign up at [Formspree.io](https://formspree.io)
2. Create a new form and get your form ID
3. Replace `YOUR_FORM_ID` in `pages/contact.vue` with your actual form ID:

```typescript
const response = await fetch('https://formspree.io/f/YOUR_ACTUAL_FORM_ID', {
  // ... rest of the configuration
})
```

## 🚀 Deployment

### GitHub Pages

1. Build the static site:
```bash
npm run generate
```

2. The generated files will be in the `dist` folder

3. Deploy to GitHub Pages:
   - Push the `dist` folder contents to your `gh-pages` branch
   - Or use GitHub Actions for automatic deployment

### GitHub Actions (Recommended)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          
      - name: Install dependencies
        run: npm ci
        
      - name: Generate static site
        run: npm run generate
        
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./dist
```

### Other Hosting Platforms

The generated static site in the `dist` folder can be deployed to:
- Netlify
- Vercel
- AWS S3 + CloudFront
- Any static hosting service

## 🔧 Configuration

### SEO Configuration

Update SEO settings in `nuxt.config.ts`:

```typescript
site: {
  url: 'https://your-domain.com',
  name: 'Your Company Name'
},

sitemap: {
  hostname: 'https://your-domain.com'
}
```

### Analytics

To add Google Analytics or other tracking:

1. Install the Nuxt Google Analytics module:
```bash
npm install @nuxtjs/google-analytics
```

2. Add to `nuxt.config.ts`:
```typescript
modules: [
  '@nuxtjs/google-analytics'
],

googleAnalytics: {
  id: 'GA_MEASUREMENT_ID'
}
```

## 🎯 Performance Optimization

The site is optimized for performance with:

- **Image Optimization**: Uses Nuxt Image with WebP format
- **Code Splitting**: Automatic code splitting by Nuxt
- **Lazy Loading**: Images and components load lazily
- **Minification**: CSS and JS are minified in production
- **Tree Shaking**: Unused code is removed
- **Critical CSS**: Above-the-fold CSS is inlined

### Lighthouse Scores Target

The site is optimized to achieve:
- Performance: 95+
- Accessibility: 95+
- Best Practices: 95+
- SEO: 95+

## 🐛 Troubleshooting

### Common Issues

1. **Build Errors**: Ensure all dependencies are installed with `npm install`
2. **Image Loading**: Check that placeholder images from Picsum are accessible
3. **Form Submission**: Verify Formspree form ID is correctly configured
4. **Styling Issues**: Clear browser cache and ensure Tailwind CSS is building correctly

### Development Issues

```bash
# Clear Nuxt cache
rm -rf .nuxt

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Restart development server
npm run dev
```

## 📖 Documentation

- [Nuxt 3 Documentation](https://nuxt.com/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Vue 3 Documentation](https://vuejs.org/guide/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support or questions about this template:
- Create an issue in the repository
- Contact: contact@verionlabs.com

---

Built with ❤️ by VerionLabs