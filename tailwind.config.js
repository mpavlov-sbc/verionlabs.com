/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./components/**/*.{js,vue,ts}",
        "./layouts/**/*.vue",
        "./pages/**/*.vue",
        "./plugins/**/*.{js,ts}",
        "./nuxt.config.{js,ts}",
        "./app.vue"
    ],
    safelist: [
        // Primary colors
        'bg-primary-50', 'bg-primary-100', 'bg-primary-200', 'bg-primary-300', 'bg-primary-400', 'bg-primary-500', 'bg-primary-600', 'bg-primary-700', 'bg-primary-800', 'bg-primary-900',
        'text-primary-50', 'text-primary-100', 'text-primary-200', 'text-primary-300', 'text-primary-400', 'text-primary-500', 'text-primary-600', 'text-primary-700', 'text-primary-800', 'text-primary-900',
        'border-primary-50', 'border-primary-100', 'border-primary-200', 'border-primary-300', 'border-primary-400', 'border-primary-500', 'border-primary-600', 'border-primary-700', 'border-primary-800', 'border-primary-900',
        'hover:bg-primary-600', 'hover:bg-primary-700', 'hover:text-primary-600', 'focus:ring-primary-500',
        // Accent colors
        'bg-accent-50', 'bg-accent-100', 'bg-accent-200', 'bg-accent-300', 'bg-accent-400', 'bg-accent-500', 'bg-accent-600', 'bg-accent-700', 'bg-accent-800', 'bg-accent-900',
        'text-accent-50', 'text-accent-100', 'text-accent-200', 'text-accent-300', 'text-accent-400', 'text-accent-500', 'text-accent-600', 'text-accent-700', 'text-accent-800', 'text-accent-900',
        'border-accent-50', 'border-accent-100', 'border-accent-200', 'border-accent-300', 'border-accent-400', 'border-accent-500', 'border-accent-600', 'border-accent-700', 'border-accent-800', 'border-accent-900',
        'hover:bg-accent-600', 'hover:text-accent-600',
        // Neutral colors
        'bg-neutral-50', 'bg-neutral-100', 'bg-neutral-200', 'bg-neutral-300', 'bg-neutral-400', 'bg-neutral-500', 'bg-neutral-600', 'bg-neutral-700', 'bg-neutral-800', 'bg-neutral-900',
        'text-neutral-50', 'text-neutral-100', 'text-neutral-200', 'text-neutral-300', 'text-neutral-400', 'text-neutral-500', 'text-neutral-600', 'text-neutral-700', 'text-neutral-800', 'text-neutral-900',
        'border-neutral-50', 'border-neutral-100', 'border-neutral-200', 'border-neutral-300', 'border-neutral-400', 'border-neutral-500', 'border-neutral-600', 'border-neutral-700', 'border-neutral-800', 'border-neutral-900',
        'hover:bg-neutral-300', 'hover:text-neutral-800', 'focus:ring-neutral-500'
    ],
    theme: {
        extend: {
            colors: {
                primary: {
                    50: '#f8fafc',
                    100: '#f1f5f9',
                    200: '#e2e8f0',
                    300: '#cbd5e1',
                    400: '#94a3b8',
                    500: '#475569',
                    600: '#334155',
                    700: '#1e293b',
                    800: '#0f172a',
                    900: '#020617',
                },
                accent: {
                    50: '#f0f9ff',
                    100: '#e0f2fe',
                    200: '#bae6fd',
                    300: '#7dd3fc',
                    400: '#38bdf8',
                    500: '#0ea5e9',
                    600: '#0284c7',
                    700: '#0369a1',
                    800: '#075985',
                    900: '#0c4a6e',
                },
                neutral: {
                    50: '#fafafa',
                    100: '#f5f5f5',
                    200: '#e5e5e5',
                    300: '#d4d4d4',
                    400: '#a3a3a3',
                    500: '#737373',
                    600: '#525252',
                    700: '#404040',
                    800: '#262626',
                    900: '#171717',
                },
                success: {
                    50: '#f0fdf4',
                    100: '#dcfce7',
                    500: '#22c55e',
                    600: '#16a34a',
                    700: '#15803d',
                },
                warning: {
                    50: '#fffbeb',
                    100: '#fef3c7',
                    500: '#f59e0b',
                    600: '#d97706',
                    700: '#b45309',
                },
                error: {
                    50: '#fef2f2',
                    100: '#fee2e2',
                    500: '#ef4444',
                    600: '#dc2626',
                    700: '#b91c1c',
                }
            },
            fontFamily: {
                sans: ['Inter', 'ui-sans-serif', 'system-ui', 'sans-serif'],
            },
            animation: {
                'fade-in': 'fadeIn 0.5s ease-in-out',
                'slide-up': 'slideUp 0.5s ease-out',
            },
            keyframes: {
                fadeIn: {
                    '0%': { opacity: '0' },
                    '100%': { opacity: '1' },
                },
                slideUp: {
                    '0%': { transform: 'translateY(20px)', opacity: '0' },
                    '100%': { transform: 'translateY(0)', opacity: '1' },
                },
            },
        },
    },
    plugins: [],
}