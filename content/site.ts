// Centralized content configuration for VerionLabs website
// This file contains all text content, making it easy to update without touching Vue components

export interface TeamMember {
    name: string
    role: string
    bio: string
    image: string
    linkedin?: string
    github?: string
}

export interface Service {
    title: string
    description: string
    detailedDescription: string
    technologies: string[]
    icon: string
}

export interface Demo {
    title: string
    description: string
    image: string
    tags: string[]
    liveDemo: string
    github: string
    featured?: boolean
}

export interface SiteContent {
    company: {
        name: string
        domain: string
        email: string
        address: string
        phone?: string
        description: string
        mission: string
    }
    navigation: {
        items: Array<{ name: string; href: string }>
    }
    social: {
        linkedin: string
        github: string
        twitter: string
    }
    homepage: {
        hero: {
            headline: string
            subheadline: string
            cta: string
        }
        mission: {
            title: string
            content: string
        }
        contactCta: {
            title: string
            description: string
            buttonText: string
        }
    }
    about: {
        story: {
            title: string
            content: string[]
        }
        vision: {
            title: string
            content: string
        }
    }
    services: Service[]
    team: TeamMember[]
    demos: Demo[]
}

export const siteContent: SiteContent = {
    company: {
        name: "VerionLabs",
        domain: "verionlabs.com",
        email: "contact@verionlabs.com",
        address: "123 Innovation Drive, Tech Valley, CA 94000",
        description: "VerionLabs provides innovative software solutions for modern businesses, specializing in cloud architecture, AI & machine learning, and custom web applications.",
        mission: "We empower businesses with cutting-edge technology solutions that drive growth, efficiency, and innovation in the digital age."
    },

    navigation: {
        items: [
            { name: "Services", href: "/services" },
            { name: "Demos", href: "/demos" },
            { name: "About", href: "/about" },
            { name: "Contact", href: "/contact" }
        ]
    },

    social: {
        linkedin: "https://linkedin.com/company/verionlabs",
        github: "https://github.com/verionlabs",
        twitter: "https://twitter.com/verionlabs"
    },

    homepage: {
        hero: {
            headline: "Innovative Software Solutions for Modern Business",
            subheadline: "We transform ideas into powerful digital experiences that drive business growth and technological advancement.",
            cta: "Explore Our Services"
        },
        mission: {
            title: "Our Mission",
            content: "At VerionLabs, we believe technology should be a catalyst for business success. We partner with companies from startups to enterprises, delivering custom software solutions that solve real-world challenges and unlock new opportunities for growth."
        },
        contactCta: {
            title: "Ready to Transform Your Business?",
            description: "Let's discuss how our innovative solutions can help you achieve your goals and stay ahead of the competition.",
            buttonText: "Get Started Today"
        }
    },

    about: {
        story: {
            title: "Our Story",
            content: [
                "Founded with a vision to bridge the gap between cutting-edge technology and practical business solutions, VerionLabs has been at the forefront of digital innovation.",
                "Our team of expert developers, architects, and consultants brings decades of combined experience across various industries and technologies.",
                "We pride ourselves on delivering not just software, but comprehensive solutions that drive measurable business outcomes for our clients."
            ]
        },
        vision: {
            title: "Our Vision",
            content: "To be the trusted technology partner that empowers businesses to thrive in the digital future, one innovative solution at a time."
        }
    },

    services: [
        {
            title: "Cloud Architecture",
            description: "Scalable, secure, and cost-effective cloud solutions tailored to your business needs.",
            detailedDescription: "We design and implement robust cloud infrastructure solutions that scale with your business. From migration strategies to cloud-native application development, we ensure your systems are optimized for performance, security, and cost-efficiency.",
            technologies: ["AWS", "Azure", "Google Cloud", "Kubernetes", "Docker", "Terraform", "CloudFormation"],
            icon: "cloud"
        },
        {
            title: "AI & Machine Learning",
            description: "Intelligent solutions that automate processes and unlock insights from your data.",
            detailedDescription: "Harness the power of artificial intelligence and machine learning to transform your business operations. We develop custom AI solutions including predictive analytics, natural language processing, computer vision, and automated decision-making systems.",
            technologies: ["Python", "TensorFlow", "PyTorch", "Scikit-learn", "MLflow", "Apache Spark", "Jupyter"],
            icon: "brain"
        },
        {
            title: "Custom Web Applications",
            description: "Modern, responsive web applications built with the latest technologies and best practices.",
            detailedDescription: "From progressive web apps to complex enterprise platforms, we create custom web applications that deliver exceptional user experiences. Our solutions are built for performance, accessibility, and maintainability.",
            technologies: ["Vue.js", "React", "Node.js", "Python", "TypeScript", "GraphQL", "PostgreSQL", "MongoDB"],
            icon: "code"
        }
    ],

    team: [
        {
            name: "Alex Chen",
            role: "Lead Cloud Architect",
            bio: "With over 10 years of experience in cloud infrastructure, Alex specializes in designing scalable, secure cloud solutions for enterprise clients.",
            image: "https://picsum.photos/400/400?random=1",
            linkedin: "https://linkedin.com/in/alexchen",
            github: "https://github.com/alexchen"
        },
        {
            name: "Sarah Johnson",
            role: "AI/ML Engineering Lead",
            bio: "Sarah brings cutting-edge machine learning expertise to complex business problems, with a PhD in Computer Science and 8 years of industry experience.",
            image: "https://picsum.photos/400/400?random=2",
            linkedin: "https://linkedin.com/in/sarahjohnson",
            github: "https://github.com/sarahjohnson"
        },
        {
            name: "Marcus Rodriguez",
            role: "Senior Full-Stack Developer",
            bio: "Marcus is passionate about creating intuitive user experiences and robust backend systems, with expertise in modern web technologies.",
            image: "https://picsum.photos/400/400?random=3",
            linkedin: "https://linkedin.com/in/marcusrodriguez",
            github: "https://github.com/marcusrodriguez"
        },
        {
            name: "Emma Thompson",
            role: "DevOps Engineer",
            bio: "Emma ensures smooth deployments and reliable infrastructure, specializing in CI/CD pipelines and automated testing frameworks.",
            image: "https://picsum.photos/400/400?random=4",
            linkedin: "https://linkedin.com/in/emmathompson",
            github: "https://github.com/emmathompson"
        }
    ],

    demos: [
        {
            title: "E-Commerce Analytics Platform",
            description: "A comprehensive analytics dashboard for e-commerce businesses with real-time insights, predictive analytics, and automated reporting.",
            image: "/analytics_platform.jpg",
            tags: ["Vue.js", "Python", "PostgreSQL", "Machine Learning", "AWS"],
            liveDemo: "#",
            github: "#",
            featured: true
        },
        {
            title: "Cloud Migration Tool",
            description: "An automated tool for seamless cloud migration with minimal downtime and comprehensive data validation.",
            image: "/cloud_migration.jpg",
            tags: ["Node.js", "AWS", "Docker", "Kubernetes", "TypeScript"],
            liveDemo: "#",
            github: "#",
            featured: true
        },
        {
            title: "AI-Powered Chatbot",
            description: "An intelligent customer service chatbot with natural language processing and integration with existing CRM systems.",
            image: "/chat_bot.jpg",
            tags: ["Python", "TensorFlow", "React", "NLP", "Azure"],
            liveDemo: "#",
            github: "#",
            featured: true
        },
    ]
}