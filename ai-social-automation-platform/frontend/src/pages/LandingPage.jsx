import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const LandingPage = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [currentTestimonial, setCurrentTestimonial] = useState(0);
  const [currentFAQ, setCurrentFAQ] = useState(null);
  const [animatedStats, setAnimatedStats] = useState({
    users: 0,
    posts: 0,
    uptime: 0,
    support: 24
  });

  // Animated counter effect
  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedStats({
        users: 25000,
        posts: 5200000,
        uptime: 99.9,
        support: 24
      });
    }, 500);
    return () => clearTimeout(timer);
  }, []);

  // Auto-rotate testimonials
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTestimonial((prev) => (prev + 1) % testimonials.length);
    }, 6000);
    return () => clearInterval(timer);
  }, []);

  const platforms = [
    { name: 'YouTube', icon: '🎥', color: 'bg-red-500', description: 'Automated video uploads, shorts, and community posts', users: '2B+' },
    { name: 'Instagram', icon: '📸', color: 'bg-gradient-to-r from-purple-500 to-pink-500', description: 'Posts, Reels, Stories, and IGTV automation', users: '2B+' },
    { name: 'Facebook', icon: '📘', color: 'bg-blue-600', description: 'Page posts, videos, and Facebook Groups management', users: '3B+' },
    { name: 'Twitter/X', icon: '🐦', color: 'bg-black', description: 'Tweets, threads, and engagement automation', users: '450M+' },
    { name: 'LinkedIn', icon: '💼', color: 'bg-blue-700', description: 'Professional posts, articles, and networking', users: '900M+' },
    { name: 'TikTok', icon: '🎵', color: 'bg-pink-600', description: 'Viral videos and trending content creation', users: '1B+' },
    { name: 'Pinterest', icon: '📌', color: 'bg-red-600', description: 'Pin creation and board management', users: '450M+' },
    { name: 'Reddit', icon: '🤖', color: 'bg-orange-600', description: 'Community engagement and content sharing', users: '430M+' }
  ];

  const contentDomains = [
    {
      name: 'Memes & Humor',
      icon: '😂',
      description: 'AI-generated memes, funny captions, and viral humor content',
      examples: ['Trending meme formats', 'Funny observations', 'Relatable humor', 'Pop culture jokes'],
      color: 'bg-yellow-100',
      popularity: '95%'
    },
    {
      name: 'Tech News & Reviews',
      icon: '📱',
      description: 'Latest technology updates, product reviews, and industry insights',
      examples: ['Product launches', 'Tech tutorials', 'Industry analysis', 'Gadget reviews'],
      color: 'bg-blue-100',
      popularity: '89%'
    },
    {
      name: 'Coding & Development',
      icon: '💻',
      description: 'Programming tips, code snippets, and developer resources',
      examples: ['Code tutorials', 'Best practices', 'Framework guides', 'Debugging tips'],
      color: 'bg-green-100',
      popularity: '78%'
    },
    {
      name: 'Business & Entrepreneurship',
      icon: '📊',
      description: 'Business strategies, startup advice, and entrepreneurial insights',
      examples: ['Growth hacking', 'Leadership tips', 'Market analysis', 'Success stories'],
      color: 'bg-purple-100',
      popularity: '92%'
    },
    {
      name: 'Lifestyle & Wellness',
      icon: '🌟',
      description: 'Health tips, lifestyle advice, and personal development content',
      examples: ['Fitness routines', 'Mental health', 'Productivity hacks', 'Life balance'],
      color: 'bg-pink-100',
      popularity: '85%'
    },
    {
      name: 'Finance & Crypto',
      icon: '💰',
      description: 'Investment advice, cryptocurrency updates, and financial literacy',
      examples: ['Market trends', 'Crypto analysis', 'Investment tips', 'Financial planning'],
      color: 'bg-orange-100',
      popularity: '88%'
    },
    {
      name: 'Travel & Adventure',
      icon: '✈️',
      description: 'Travel guides, destination reviews, and adventure stories',
      examples: ['Hidden gems', 'Travel tips', 'Cultural insights', 'Budget travel'],
      color: 'bg-indigo-100',
      popularity: '82%'
    },
    {
      name: 'Food & Cooking',
      icon: '🍳',
      description: 'Recipes, cooking tips, and culinary adventures',
      examples: ['Quick recipes', 'Cooking hacks', 'Food photography', 'Restaurant reviews'],
      color: 'bg-red-100',
      popularity: '90%'
    }
  ];

  const features = [
    {
      icon: '🤖',
      title: 'AI-Powered Content Generation',
      description: 'Advanced AI using Mistral and Groq APIs creates engaging, platform-optimized content automatically.',
      details: ['Natural language generation', 'Context-aware content', 'Brand voice matching', 'Trending topic integration'],
      category: 'AI Technology'
    },
    {
      icon: '📅',
      title: 'Smart Scheduling & Automation',
      description: 'Post at optimal times with AI-analyzed audience behavior and engagement patterns.',
      details: ['Optimal timing analysis', 'Timezone optimization', 'Audience behavior tracking', 'Automated queue management'],
      category: 'Automation'
    },
    {
      icon: '🔐',
      title: 'Enterprise-Grade Security',
      description: 'Bank-grade encryption protects your social media credentials with zero-knowledge architecture.',
      details: ['End-to-end encryption', 'Secure credential storage', '2FA support', 'Regular security audits'],
      category: 'Security'
    },
    {
      icon: '🎯',
      title: 'Multi-Platform Optimization',
      description: 'Automatically adapts content format, length, and style for each social media platform.',
      details: ['Platform-specific formatting', 'Character limit optimization', 'Hashtag generation', 'Media optimization'],
      category: 'Optimization'
    },
    {
      icon: '📊',
      title: 'Advanced Analytics Dashboard',
      description: 'Track performance, engagement, and growth across all platforms with detailed insights.',
      details: ['Real-time analytics', 'Engagement tracking', 'Growth metrics', 'ROI calculation'],
      category: 'Analytics'
    },
    {
      icon: '⚡',
      title: 'Velocity Workflows',
      description: 'Set up complex automation rules for content creation, posting, and engagement at maximum speed.',
      details: ['Custom automation rules', 'Trigger-based actions', 'Workflow templates', 'Bulk operations'],
      category: 'Workflows'
    },
    {
      icon: '🖼️',
      title: 'AI Visual Content Creation',
      description: 'Create stunning visuals, memes, and videos using DALL-E and advanced AI tools.',
      details: ['Automatic image generation', 'Meme creation', 'Video thumbnails', 'Brand-consistent visuals'],
      category: 'Content Creation'
    },
    {
      icon: '💬',
      title: 'Intelligent Engagement',
      description: 'AI responds to comments and messages maintaining your brand voice and personality.',
      details: ['Automated responses', 'Sentiment analysis', 'Brand voice consistency', 'Escalation rules'],
      category: 'Engagement'
    },
    {
      icon: '🔄',
      title: 'Content Repurposing Engine',
      description: 'Transform one piece of content into multiple platform-specific variations automatically.',
      details: ['Cross-platform adaptation', 'Format conversion', 'Length optimization', 'Style adjustment'],
      category: 'Content Strategy'
    }
  ];

  const pricingPlans = [
    {
      name: 'Velocity Starter',
      price: '$29',
      period: '/month',
      description: 'Perfect for individuals and small creators getting started',
      popular: false,
      features: [
        '3 Social Media Platforms',
        '100 AI-Generated Posts/Month',
        '3 Content Domains',
        'Basic Analytics Dashboard',
        'Standard Support (48h response)',
        'Content Library Access',
        '2 GB Media Storage',
        'Basic Automation Rules'
      ],
      buttonText: 'Start Free Trial',
      savings: null,
      badge: null
    },
    {
      name: 'Velocity Pro',
      price: '$79',
      period: '/month',
      description: 'Ideal for growing businesses and serious content creators',
      popular: true,
      features: [
        '8 Social Media Platforms',
        '1,000 AI-Generated Posts/Month',
        'All Content Domains',
        'Advanced Analytics & Reports',
        'Priority Support (12h response)',
        'Custom Content Templates',
        'Team Collaboration (5 users)',
        'API Access',
        '25 GB Media Storage',
        'A/B Testing Tools',
        'White-label Options',
        'Advanced Automation Rules'
      ],
      buttonText: 'Start Free Trial',
      savings: 'Save $240/year',
      badge: 'Most Popular'
    },
    {
      name: 'Velocity Agency',
      price: '$299',
      period: '/month',
      description: 'For agencies and enterprises managing multiple clients',
      popular: false,
      features: [
        'Unlimited Social Media Accounts',
        'Unlimited AI-Generated Posts',
        'Complete White-label Solutions',
        'Dedicated Account Manager',
        'Custom Integrations & APIs',
        'Advanced Team Management (25 users)',
        'Priority API Access',
        'Custom Analytics Dashboard',
        'Client Management Portal',
        'Unlimited Media Storage',
        'Custom Branding & Domain',
        '99.9% SLA Guarantee',
        'Advanced Security Features',
        'Custom AI Training'
      ],
      buttonText: 'Contact Sales',
      savings: 'Save $720/year',
      badge: 'Enterprise'
    }
  ];

  const testimonials = [
    {
      name: 'Sarah Johnson',
      role: 'Digital Marketing Manager',
      company: 'TechCorp Inc.',
      image: '👩‍💼',
      content: 'VelocityPost.ai transformed our social media strategy completely. We increased engagement by 300% in just 2 months. The AI content is incredibly relevant and our audience loves it. We went from struggling to post 2-3 times per week to having daily, high-quality content across all platforms.',
      metrics: { engagement: '+300%', followers: '+150%', time_saved: '25hrs/week' },
      rating: 5
    },
    {
      name: 'Mike Chen',
      role: 'Content Creator & YouTuber',
      company: '@mikecreates',
      image: '👨‍💻',
      content: 'As a solo creator, VelocityPost.ai is absolutely revolutionary. It saves me 20+ hours per week on content creation and scheduling. The automated posting and analytics help me focus on what I do best - creating videos. My follower growth has been exponential across all platforms.',
      metrics: { time_saved: '+20hrs/week', growth: '+500%', platforms: '6 platforms' },
      rating: 5
    },
    {
      name: 'Jessica Rodriguez',
      role: 'Agency Owner',
      company: 'SocialGrow Agency',
      image: '👩‍🚀',
      content: 'We manage 75+ client accounts effortlessly with VelocityPost.ai. The white-label solution helped us scale our agency 5x in one year. Our clients see consistent, measurable results and we can take on more accounts without increasing overhead costs.',
      metrics: { clients: '75+ accounts', growth: '5x scale', revenue: '+450%' },
      rating: 5
    },
    {
      name: 'David Park',
      role: 'E-commerce Founder',
      company: 'TrendyTech Store',
      image: '👨‍💼',
      content: 'Our social media was completely inconsistent before VelocityPost.ai. Now we have daily, engaging posts across Instagram, Facebook, and Twitter that drive real traffic to our store. Sales from social media increased by 280% in just 3 months.',
      metrics: { sales: '+280%', traffic: '+200%', conversion: '+52%' },
      rating: 5
    },
    {
      name: 'Emily Thompson',
      role: 'Fitness Influencer',
      company: '@FitWithEmily',
      image: '👩‍🏋️',
      content: 'The AI understands my fitness niche perfectly. It creates workout tips, motivation posts, and even generates relevant images that match my brand. I went from 15K to 150K followers in 8 months while spending less time on content creation.',
      metrics: { followers: '15K → 150K', engagement: '+320%', time_saved: '15hrs/week' },
      rating: 5
    }
  ];

  const automationWorkflow = [
    {
      step: 1,
      title: 'Connect Your Accounts',
      description: 'Securely link your social media accounts with bank-grade encryption',
      icon: '🔗',
      details: ['One-click OAuth integration', 'Support for 2FA accounts', 'Secure credential storage', 'Easy account switching'],
      time: '2 minutes'
    },
    {
      step: 2,
      title: 'Choose Content Domains',
      description: 'Select from 15+ specialized content categories tailored to your audience',
      icon: '🎯',
      details: ['AI-powered recommendations', 'Custom domain creation', 'Trending topic integration', 'Audience analysis'],
      time: '1 minute'
    },
    {
      step: 3,
      title: 'Set Velocity Rules',
      description: 'Configure posting schedules, frequency, and engagement preferences',
      icon: '⚙️',
      details: ['Smart scheduling', 'Frequency optimization', 'Engagement automation', 'Content approval workflow'],
      time: '2 minutes'
    },
    {
      step: 4,
      title: 'AI Takes Over',
      description: 'Our AI agents generate, optimize, and post content automatically at velocity',
      icon: '🚀',
      details: ['24/7 content generation', 'Platform optimization', 'Real-time adaptation', 'Performance monitoring'],
      time: 'Continuous'
    }
  ];

  const aiCapabilities = [
    {
      title: 'Content Intelligence Engine',
      description: 'Our AI analyzes trending topics, audience preferences, and engagement patterns to create viral-worthy content at velocity.',
      features: ['Trend analysis', 'Sentiment optimization', 'Viral prediction', 'Audience targeting'],
      icon: '🧠'
    },
    {
      title: 'Brand Voice Learning',
      description: 'AI learns your unique brand voice and maintains consistency across all platforms and content types.',
      features: ['Voice analysis', 'Tone matching', 'Style consistency', 'Brand guidelines'],
      icon: '🎭'
    },
    {
      title: 'Platform Optimization',
      description: 'Automatically adapts content for each platform\'s best practices, algorithms, and audience behavior.',
      features: ['Algorithm optimization', 'Format adaptation', 'Timing optimization', 'Hashtag generation'],
      icon: '🎛️'
    },
    {
      title: 'Performance Learning',
      description: 'Continuously improves content quality based on engagement data and performance metrics.',
      features: ['Performance tracking', 'A/B testing', 'Content optimization', 'Strategy refinement'],
      icon: '📈'
    }
  ];

  const stats = [
    { number: animatedStats.users.toLocaleString() + '+', label: 'Active Users', icon: '👥', description: 'Growing daily' },
    { number: (animatedStats.posts / 1000000).toFixed(1) + 'M+', label: 'Posts Generated', icon: '📝', description: 'High-velocity content' },
    { number: animatedStats.uptime + '%', label: 'Uptime', icon: '⚡', description: 'Always available' },
    { number: animatedStats.support + '/7', label: 'Support', icon: '🛟', description: 'Round-the-clock help' }
  ];

  const integrations = [
    { name: 'YouTube Data API', type: 'Video Platform', status: 'Official API', icon: '🎥' },
    { name: 'Facebook Graph API', type: 'Social Network', status: 'Official API', icon: '📘' },
    { name: 'Instagram Graph API', type: 'Photo Sharing', status: 'Official API', icon: '📸' },
    { name: 'Twitter API v2', type: 'Microblogging', status: 'Official API', icon: '🐦' },
    { name: 'LinkedIn API', type: 'Professional Network', status: 'Official API', icon: '💼' },
    { name: 'TikTok Business API', type: 'Short Video', status: 'Beta Access', icon: '🎵' },
    { name: 'Pinterest API', type: 'Discovery Platform', status: 'Official API', icon: '📌' },
    { name: 'Reddit API', type: 'Community Platform', status: 'Official API', icon: '🤖' }
  ];

  const faqs = [
    {
      question: "How does VelocityPost.ai's AI content generation work?",
      answer: "Our AI uses advanced language models (Mistral AI and Groq) to generate human-like content based on your selected domains. It analyzes trending topics, your audience preferences, and engagement patterns to create relevant, engaging posts tailored to each platform. The AI learns from your brand voice and continuously improves content quality based on performance data."
    },
    {
      question: "Is my social media data and credentials secure?",
      answer: "Absolutely. We use enterprise-grade encryption (AES-256) to protect your credentials. Our zero-knowledge architecture ensures that even our team cannot access your passwords. We comply with SOC 2 Type II, GDPR, and other international security standards. Your data is stored in secure, encrypted databases with regular security audits."
    },
    {
      question: "Can I control what content gets posted to my accounts?",
      answer: "Yes, you have complete control! You can set approval workflows, content filters, posting schedules, and brand guidelines. You can review content before it goes live or let the AI post automatically based on your preferences. You can also pause, edit, or delete any content at any time."
    },
    {
      question: "How does the pricing work and what's included?",
      answer: "Our pricing is based on the number of platforms, posts per month, and features you need. All plans include a 14-day free trial with no credit card required. You can upgrade, downgrade, or cancel anytime. Each plan includes AI content generation, scheduling, analytics, and customer support."
    },
    {
      question: "Which social media platforms does VelocityPost.ai support?",
      answer: "We support 8+ major platforms including YouTube, Instagram, Facebook, Twitter/X, LinkedIn, TikTok, Pinterest, and Reddit. We use official APIs where available and secure automation for others. We're constantly adding new platforms based on user demand and API availability."
    },
    {
      question: "Do you offer API access for developers and agencies?",
      answer: "Yes! Pro and Agency plans include comprehensive API access so you can integrate our AI content generation into your existing tools and workflows. We provide detailed documentation, SDKs, and developer support to help you build custom integrations."
    },
    {
      question: "How quickly can I see results with VelocityPost.ai?",
      answer: "Most users see immediate improvements in posting consistency and content quality within the first week. Significant engagement and follower growth typically occurs within 2-4 weeks as the AI learns your audience and optimizes content. The platform is designed for velocity - fast setup, fast results."
    },
    {
      question: "What kind of customer support do you provide?",
      answer: "We offer 24/7 customer support through multiple channels including live chat, email, and phone. Pro plans get priority support with 12-hour response times, while Agency plans include a dedicated account manager. We also provide comprehensive documentation, video tutorials, and onboarding assistance."
    }
  ];

  const successStories = [
    {
      company: 'TechStartup Inc.',
      industry: 'Technology',
      result: 'Grew from 500 to 50K followers in 6 months',
      metric: '10,000% growth',
      challenge: 'No time for content creation',
      solution: 'Automated tech news and industry insights'
    },
    {
      company: 'FitLife Coaching',
      industry: 'Fitness',
      result: 'Increased client inquiries by 400%',
      metric: '400% more leads',
      challenge: 'Inconsistent social media presence',
      solution: 'Daily fitness tips and motivational content'
    },
    {
      company: 'Digital Marketing Agency',
      industry: 'Marketing',
      result: 'Scaled to 100+ clients without hiring',
      metric: '5x agency growth',
      challenge: 'Client content management overhead',
      solution: 'White-label automation for all clients'
    }
  ];

  const toggleFAQ = (index) => {
    setCurrentFAQ(currentFAQ === index ? null : index);
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-white/95 backdrop-blur-md shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            {/* Logo */}
            <div className="flex items-center">
              <div className="relative">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                  <span className="text-white text-xl font-bold">V</span>
                </div>
                <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full animate-ping"></div>
              </div>
              <div className="ml-3">
                <h1 className="text-xl font-bold text-gray-900">VelocityPost.ai</h1>
                <p className="text-xs text-gray-600">Social Media at Light Speed</p>
              </div>
            </div>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex space-x-8">
              <a href="#features" className="text-gray-600 hover:text-blue-600 transition-colors font-medium">Features</a>
              <a href="#platforms" className="text-gray-600 hover:text-blue-600 transition-colors font-medium">Platforms</a>
              <a href="#pricing" className="text-gray-600 hover:text-blue-600 transition-colors font-medium">Pricing</a>
              <a href="#testimonials" className="text-gray-600 hover:text-blue-600 transition-colors font-medium">Reviews</a>
              <a href="#faq" className="text-gray-600 hover:text-blue-600 transition-colors font-medium">FAQ</a>
            </nav>

            {/* Auth Buttons */}
            <div className="hidden md:flex items-center space-x-4">
              <Link
                to="/login"
                className="text-gray-600 hover:text-blue-600 font-medium transition-colors"
              >
                Login
              </Link>
              <Link
                to="/register"
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 py-2 rounded-lg font-medium transition-all duration-300 transform hover:scale-105 shadow-lg"
              >
                Start Free Trial
              </Link>
            </div>

            {/* Mobile menu button */}
            <button
              className="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={isMenuOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"} />
              </svg>
            </button>
          </div>

          {/* Mobile Navigation */}
          {isMenuOpen && (
            <div className="md:hidden py-4 border-t">
              <div className="flex flex-col space-y-4">
                <a href="#features" className="text-gray-600 hover:text-blue-600 transition-colors" onClick={() => setIsMenuOpen(false)}>Features</a>
                <a href="#platforms" className="text-gray-600 hover:text-blue-600 transition-colors" onClick={() => setIsMenuOpen(false)}>Platforms</a>
                <a href="#pricing" className="text-gray-600 hover:text-blue-600 transition-colors" onClick={() => setIsMenuOpen(false)}>Pricing</a>
                <a href="#testimonials" className="text-gray-600 hover:text-blue-600 transition-colors" onClick={() => setIsMenuOpen(false)}>Reviews</a>
                <a href="#faq" className="text-gray-600 hover:text-blue-600 transition-colors" onClick={() => setIsMenuOpen(false)}>FAQ</a>
                <div className="flex flex-col space-y-2 pt-4 border-t">
                  <Link to="/login" className="text-gray-600 hover:text-blue-600 transition-colors" onClick={() => setIsMenuOpen(false)}>Login</Link>
                  <Link to="/register" className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg text-center font-medium transition-all" onClick={() => setIsMenuOpen(false)}>
                    Start Free Trial
                  </Link>
                </div>
              </div>
            </div>
          )}
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-20 overflow-hidden">
        {/* Background Animation */}
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-10 left-10 w-72 h-72 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl animate-pulse"></div>
          <div className="absolute top-10 right-10 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl animate-pulse animation-delay-2000"></div>
          <div className="absolute -bottom-8 left-20 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl animate-pulse animation-delay-4000"></div>
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="inline-flex items-center px-4 py-2 bg-gradient-to-r from-blue-100 to-purple-100 rounded-full text-blue-800 text-sm font-medium mb-6 animate-bounce">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
              Join 25,000+ creators posting at AI velocity
            </div>
            
            <h1 className="text-4xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
              Social Media at
              <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent block">
                Light Speed
              </span>
            </h1>
            
            <p className="text-xl md:text-2xl text-gray-600 mb-8 max-w-4xl mx-auto leading-relaxed">
              Enter your social credentials, select your niches, and watch our AI agents
              <span className="font-semibold text-blue-600"> generate and post viral content</span> across all platforms 24/7.
              <span className="block mt-2 text-lg text-gray-500">Pure velocity. Zero manual work. Maximum growth.</span>
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
              <Link
                to="/register"
                className="group bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-4 rounded-xl text-lg font-semibold transition-all duration-300 transform hover:scale-105 shadow-2xl inline-flex items-center justify-center"
              >
                Start Free 14-Day Trial
                <svg className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </Link>
              <button className="group border-2 border-gray-300 hover:border-gray-400 text-gray-700 px-8 py-4 rounded-xl text-lg font-semibold transition-all duration-300 hover:shadow-lg inline-flex items-center justify-center">
                <svg className="mr-2 h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                </svg>
                Watch Demo (2 min)
              </button>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center text-sm text-gray-500 mb-12">
              <div className="flex items-center justify-center">
                <svg className="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                No credit card required
              </div>
              <div className="flex items-center justify-center">
                <svg className="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Setup in 5 minutes
              </div>
              <div className="flex items-center justify-center">
                <svg className="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Cancel anytime
              </div>
              <div className="flex items-center justify-center">
                <svg className="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                24/7 Support
              </div>
            </div>

            {/* Animated Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              {stats.map((stat, index) => (
                <div key={index} className="bg-white/70 backdrop-blur-sm rounded-2xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105">
                  <div className="text-3xl mb-2">{stat.icon}</div>
                  <div className="text-3xl md:text-4xl font-bold text-blue-600 mb-2">
                    {stat.number}
                  </div>
                  <div className="text-gray-600 font-medium">{stat.label}</div>
                  <div className="text-xs text-gray-500 mt-1">{stat.description}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* How It Works - Velocity Workflow */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-4">
              From Zero to
              <span className="text-blue-600"> Velocity</span> in Minutes
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our streamlined setup gets you posting at AI velocity faster than any other platform.
              No complex configurations, no learning curve - just pure speed.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {automationWorkflow.map((step, index) => (
              <div key={index} className="relative group">
                <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-8 h-full border border-blue-100 hover:border-blue-200 transition-all duration-300 group-hover:shadow-xl">
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center text-white font-bold text-lg">
                      {step.step}
                    </div>
                    <span className="text-sm font-medium text-blue-600 bg-blue-100 px-3 py-1 rounded-full">
                      {step.time}
                    </span>
                  </div>
                  <div className="text-4xl mb-4">{step.icon}</div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-3">{step.title}</h3>
                  <p className="text-gray-600 mb-4">{step.description}</p>
                  <ul className="space-y-2">
                    {step.details.map((detail, detailIndex) => (
                      <li key={detailIndex} className="flex items-center text-sm text-gray-500">
                        <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mr-2"></div>
                        {detail}
                      </li>
                    ))}
                  </ul>
                </div>
                {index < automationWorkflow.length - 1 && (
                  <div className="hidden lg:block absolute top-1/2 -right-4 w-8 h-0.5 bg-gradient-to-r from-blue-300 to-purple-300"></div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Supported Platforms Section */}
      <section id="platforms" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-4">
              Post at Velocity Across
              <span className="text-blue-600"> All Platforms</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Connect all your social accounts and let our AI agents adapt content for each platform's
              unique audience, algorithm, and best practices automatically.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16">
            {platforms.map((platform, index) => (
              <div key={index} className="group bg-white rounded-2xl p-6 shadow-lg hover:shadow-2xl transition-all duration-300 transform hover:scale-105 cursor-pointer">
                <div className={`w-16 h-16 ${platform.color} rounded-2xl flex items-center justify-center text-white text-2xl mb-4 group-hover:scale-110 transition-transform`}>
                  {platform.icon}
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{platform.name}</h3>
                <p className="text-sm text-gray-600 mb-3">{platform.description}</p>
                <div className="flex items-center justify-between">
                  <span className="text-xs text-blue-600 font-medium">{platform.users} users</span>
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                </div>
              </div>
            ))}
          </div>

          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-center text-white">
            <h3 className="text-2xl font-bold mb-4">Total Reach: 10+ Billion Users</h3>
            <p className="text-blue-100 mb-6">Your content can reach every corner of the social media universe</p>
            <Link
              to="/register"
              className="bg-white text-blue-600 hover:bg-gray-100 px-8 py-3 rounded-lg font-semibold transition-colors inline-flex items-center"
            >
              Connect Your Platforms
              <svg className="ml-2 h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Link>
          </div>
        </div>
      </section>

      {/* Content Domains Section */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-4">
              AI Content for
              <span className="text-blue-600"> Every Niche</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our specialized AI agents understand your industry and create content that resonates
              with your specific audience. Choose from proven high-engagement domains.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {contentDomains.map((domain, index) => (
              <div key={index} className={`${domain.color} rounded-2xl p-6 border border-gray-200 hover:border-blue-300 transition-all duration-300 hover:shadow-lg`}>
                <div className="flex items-center justify-between mb-4">
                  <div className="text-3xl">{domain.icon}</div>
                  <span className="text-sm font-medium text-blue-600 bg-white px-2 py-1 rounded-full">
                    {domain.popularity} popular
                  </span>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-3">{domain.name}</h3>
                <p className="text-sm text-gray-600 mb-4">{domain.description}</p>
                <div className="space-y-2">
                  <p className="text-xs font-medium text-gray-700">Popular content types:</p>
                  {domain.examples.map((example, exampleIndex) => (
                    <div key={exampleIndex} className="flex items-center text-xs text-gray-600">
                      <div className="w-1 h-1 bg-blue-500 rounded-full mr-2"></div>
                      {example}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-4">
              Everything You Need for
              <span className="text-blue-600"> Social Velocity</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Comprehensive AI-powered features designed to accelerate your social media growth
              while maintaining quality and authenticity.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div key={index} className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 group">
                <div className="flex items-center mb-4">
                  <div className="text-4xl mr-4">{feature.icon}</div>
                  <span className="text-xs font-medium text-blue-600 bg-blue-100 px-3 py-1 rounded-full">
                    {feature.category}
                  </span>
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3 group-hover:text-blue-600 transition-colors">
                  {feature.title}
                </h3>
                <p className="text-gray-600 mb-4">{feature.description}</p>
                <ul className="space-y-2">
                  {feature.details.map((detail, detailIndex) => (
                    <li key={detailIndex} className="flex items-center text-sm text-gray-500">
                      <svg className="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      {detail}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* AI Capabilities */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-4">
              Powered by
              <span className="text-blue-600"> Advanced AI</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our AI doesn't just generate content - it learns, adapts, and optimizes to deliver
              maximum velocity for your social media growth.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {aiCapabilities.map((capability, index) => (
              <div key={index} className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-2xl p-8 border border-blue-100">
                <div className="flex items-center mb-4">
                  <div className="text-3xl mr-4">{capability.icon}</div>
                  <h3 className="text-xl font-semibold text-gray-900">{capability.title}</h3>
                </div>
                <p className="text-gray-600 mb-6">{capability.description}</p>
                <div className="grid grid-cols-2 gap-4">
                  {capability.features.map((feature, featureIndex) => (
                    <div key={featureIndex} className="bg-white rounded-lg p-3 shadow-sm">
                      <div className="flex items-center">
                        <div className="w-2 h-2 bg-blue-500 rounded-full mr-2"></div>
                        <span className="text-sm font-medium text-gray-700">{feature}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-4">
              Velocity Pricing for
              <span className="text-blue-600"> Every Creator</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Start free, scale fast. Choose the plan that matches your social media velocity goals.
              All plans include our core AI features and 24/7 support.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {pricingPlans.map((plan, index) => (
              <div key={index} className={`rounded-2xl p-8 ${
                plan.popular 
                  ? 'bg-gradient-to-br from-blue-600 to-purple-600 text-white shadow-2xl transform scale-105 border-4 border-blue-200' 
                  : 'bg-white border-2 border-gray-200 hover:border-blue-300'
              } transition-all duration-300`}>
                {plan.badge && (
                  <div className="text-center mb-4">
                    <span className={`px-4 py-2 rounded-full text-sm font-semibold ${
                      plan.popular 
                        ? 'bg-white text-blue-600' 
                        : 'bg-blue-100 text-blue-600'
                    }`}>
                      {plan.badge}
                    </span>
                  </div>
                )}
                
                <div className="text-center mb-8">
                  <h3 className={`text-2xl font-bold mb-2 ${plan.popular ? 'text-white' : 'text-gray-900'}`}>
                    {plan.name}
                  </h3>
                  <div className="mb-4">
                    <span className={`text-5xl font-bold ${plan.popular ? 'text-white' : 'text-gray-900'}`}>
                      {plan.price}
                    </span>
                    <span className={`text-lg ${plan.popular ? 'text-blue-100' : 'text-gray-600'}`}>
                      {plan.period}
                    </span>
                  </div>
                  <p className={`${plan.popular ? 'text-blue-100' : 'text-gray-600'}`}>
                    {plan.description}
                  </p>
                  {plan.savings && (
                    <div className={`mt-2 text-sm font-medium ${plan.popular ? 'text-yellow-200' : 'text-green-600'}`}>
                      {plan.savings}
                    </div>
                  )}
                </div>

                <ul className="space-y-4 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-start">
                      <svg className={`h-5 w-5 mr-3 mt-0.5 flex-shrink-0 ${plan.popular ? 'text-blue-200' : 'text-green-500'}`} fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                      <span className={`text-sm ${plan.popular ? 'text-blue-100' : 'text-gray-600'}`}>
                        {feature}
                      </span>
                    </li>
                  ))}
                </ul>

                <Link
                  to="/register"
                  className={`w-full py-4 px-6 rounded-xl font-semibold text-center block transition-all duration-300 ${
                    plan.popular
                      ? 'bg-white text-blue-600 hover:bg-gray-50 shadow-lg'
                      : 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl'
                  }`}
                >
                  {plan.buttonText}
                </Link>
              </div>
            ))}
          </div>

          <div className="mt-12 text-center">
            <p className="text-gray-600 mb-4">All plans include:</p>
            <div className="flex flex-wrap justify-center gap-6 text-sm text-gray-500">
              <div className="flex items-center">
                <svg className="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                14-day free trial
              </div>
              <div className="flex items-center">
                <svg className="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                No setup fees
              </div>
              <div className="flex items-center">
                <svg className="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Cancel anytime
              </div>
              <div className="flex items-center">
                <svg className="w-4 h-4 text-green-500 mr-2" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Money-back guarantee
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section id="testimonials" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-4">
              Loved by Creators
              <span className="text-blue-600"> Worldwide</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              See how VelocityPost.ai is helping thousands of creators, businesses, and agencies
              achieve unprecedented social media growth.
            </p>
          </div>

          {/* Featured Testimonial */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white mb-12">
            <div className="max-w-4xl mx-auto text-center">
              <div className="flex justify-center mb-4">
                {[...Array(testimonials[currentTestimonial].rating)].map((_, i) => (
                  <svg key={i} className="w-6 h-6 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                ))}
              </div>
              <blockquote className="text-xl md:text-2xl font-medium mb-6">
                "{testimonials[currentTestimonial].content}"
              </blockquote>
              <div className="flex items-center justify-center space-x-4">
                <div className="text-4xl">{testimonials[currentTestimonial].image}</div>
                <div className="text-left">
                  <div className="font-semibold">{testimonials[currentTestimonial].name}</div>
                  <div className="text-blue-200">{testimonials[currentTestimonial].role}</div>
                  <div className="text-blue-100 text-sm">{testimonials[currentTestimonial].company}</div>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4 mt-6 max-w-md mx-auto">
                {Object.entries(testimonials[currentTestimonial].metrics).map(([key, value]) => (
                  <div key={key} className="text-center">
                    <div className="text-2xl font-bold text-yellow-300">{value}</div>
                    <div className="text-blue-200 text-xs capitalize">{key.replace('_', ' ')}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* All Testimonials Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className={`bg-gray-50 rounded-2xl p-6 transition-all duration-300 ${
                index === currentTestimonial ? 'ring-2 ring-blue-500 shadow-lg' : 'hover:shadow-md'
              }`}>
                <div className="flex justify-between items-start mb-4">
                  <div className="flex">
                    {[...Array(testimonial.rating)].map((_, i) => (
                      <svg key={i} className="w-4 h-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                      </svg>
                    ))}
                  </div>
                  <div className="text-2xl">{testimonial.image}</div>
                </div>
                <p className="text-gray-600 mb-4 text-sm leading-relaxed">"{testimonial.content.substring(0, 150)}..."</p>
                <div className="border-t pt-4">
                  <div className="font-semibold text-gray-900">{testimonial.name}</div>
                  <div className="text-blue-600 text-sm">{testimonial.role}</div>
                  <div className="text-gray-500 text-xs">{testimonial.company}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Success Stories */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-4">
              Real Results at
              <span className="text-blue-600"> Real Velocity</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Case studies from businesses that achieved extraordinary growth with VelocityPost.ai
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {successStories.map((story, index) => (
              <div key={index} className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300">
                <div className="text-center mb-6">
                  <div className="text-4xl font-bold text-blue-600 mb-2">{story.metric}</div>
                  <div className="text-gray-600 text-sm">{story.industry}</div>
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">{story.company}</h3>
                <p className="text-blue-600 font-medium mb-4">{story.result}</p>
                <div className="space-y-3">
                  <div>
                    <span className="text-xs font-medium text-gray-500">Challenge:</span>
                    <p className="text-sm text-gray-600">{story.challenge}</p>
                  </div>
                  <div>
                    <span className="text-xs font-medium text-gray-500">Solution:</span>
                    <p className="text-sm text-gray-600">{story.solution}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* API & Integrations */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-4">
              Enterprise-Grade
              <span className="text-blue-600"> Integrations</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Built on official APIs and secure connections for maximum reliability and performance.
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {integrations.map((integration, index) => (
              <div key={index} className="bg-gray-50 rounded-xl p-6 text-center hover:shadow-lg transition-all duration-300">
                <div className="text-3xl mb-3">{integration.icon}</div>
                <h3 className="font-semibold text-gray-900 mb-2">{integration.name}</h3>
                <p className="text-xs text-gray-600 mb-2">{integration.type}</p>
                <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                  integration.status === 'Official API' ? 'bg-green-100 text-green-700' : 'bg-blue-100 text-blue-700'
                }`}>
                  {integration.status}
                </span>
              </div>
            ))}
          </div>

          <div className="mt-12 text-center">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white">
              <h3 className="text-2xl font-bold mb-4">Need Custom Integrations?</h3>
              <p className="text-blue-100 mb-6">Our API allows you to build custom integrations and workflows</p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link
                  to="/register"
                  className="bg-white text-blue-600 hover:bg-gray-100 px-6 py-3 rounded-lg font-semibold transition-colors"
                >
                  View API Docs
                </Link>
                <button className="border-2 border-white text-white hover:bg-white hover:text-blue-600 px-6 py-3 rounded-lg font-semibold transition-colors">
                  Contact Sales
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-20 bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-4">
              Frequently Asked
              <span className="text-blue-600"> Questions</span>
            </h2>
            <p className="text-xl text-gray-600">
              Everything you need to know about VelocityPost.ai
            </p>
          </div>

          <div className="space-y-4">
            {faqs.map((faq, index) => (
              <div key={index} className="bg-white rounded-xl shadow-sm border border-gray-200">
                <button
                  className="w-full px-6 py-4 text-left flex justify-between items-center hover:bg-gray-50 transition-colors"
                  onClick={() => toggleFAQ(index)}
                >
                  <span className="font-semibold text-gray-900 pr-4">{faq.question}</span>
                  <svg
                    className={`w-5 h-5 text-gray-500 transform transition-transform ${
                      currentFAQ === index ? 'rotate-180' : ''
                    }`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                {currentFAQ === index && (
                  <div className="px-6 pb-4">
                    <p className="text-gray-600 leading-relaxed">{faq.answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="mt-12 text-center">
            <p className="text-gray-600 mb-4">Still have questions?</p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition-colors">
                Contact Support
              </button>
              <button className="border-2 border-gray-300 hover:border-gray-400 text-gray-700 px-6 py-3 rounded-lg font-semibold transition-colors">
                Schedule Demo
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">
            Ready to Experience
            <span className="block">Social Media Velocity?</span>
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-3xl mx-auto">
            Join 25,000+ creators who've already discovered the power of AI-driven social media automation.
            Start your velocity journey today - no credit card required.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
            <Link
              to="/register"
              className="group bg-white text-blue-600 hover:bg-gray-100 px-8 py-4 rounded-xl text-lg font-semibold transition-all duration-300 transform hover:scale-105 shadow-2xl inline-flex items-center justify-center"
            >
              Start Free 14-Day Trial
              <svg className="ml-2 h-5 w-5 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Link>
            <button className="border-2 border-white text-white hover:bg-white hover:text-blue-600 px-8 py-4 rounded-xl text-lg font-semibold transition-all duration-300">
              Schedule Personal Demo
            </button>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center text-sm text-blue-100 max-w-2xl mx-auto">
            <div className="flex items-center justify-center">
              <svg className="w-4 h-4 text-green-300 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Free 14-day trial
            </div>
            <div className="flex items-center justify-center">
              <svg className="w-4 h-4 text-green-300 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              5-minute setup
            </div>
            <div className="flex items-center justify-center">
              <svg className="w-4 h-4 text-green-300 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              Cancel anytime
            </div>
            <div className="flex items-center justify-center">
              <svg className="w-4 h-4 text-green-300 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
              24/7 support
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* Company Info */}
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center mb-4">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center mr-3">
                  <span className="text-white text-xl font-bold">V</span>
                </div>
                <div>
                  <h3 className="text-xl font-bold">VelocityPost.ai</h3>
                  <p className="text-gray-400">Social Media at Light Speed</p>
                </div>
              </div>
              <p className="text-gray-400 mb-4 max-w-md">
                The most powerful AI-driven social media automation platform. 
                Generate content, schedule posts, and grow your audience at velocity.
              </p>
              <div className="flex space-x-4">
                <a href="#" className="text-gray-400 hover:text-white text-2xl transition-colors">📧</a>
                <a href="#" className="text-gray-400 hover:text-white text-2xl transition-colors">🐦</a>
                <a href="#" className="text-gray-400 hover:text-white text-2xl transition-colors">📘</a>
                <a href="#" className="text-gray-400 hover:text-white text-2xl transition-colors">📸</a>
                <a href="#" className="text-gray-400 hover:text-white text-2xl transition-colors">💼</a>
              </div>
            </div>

            {/* Product Links */}
            <div>
              <h4 className="text-lg font-semibold mb-4">Product</h4>
              <ul className="space-y-2">
                <li><a href="#features" className="text-gray-400 hover:text-white transition-colors">Features</a></li>
                <li><a href="#platforms" className="text-gray-400 hover:text-white transition-colors">Platforms</a></li>
                <li><a href="#pricing" className="text-gray-400 hover:text-white transition-colors">Pricing</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">API Documentation</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Integrations</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Security</a></li>
              </ul>
            </div>

            {/* Support Links */}
            <div>
              <h4 className="text-lg font-semibold mb-4">Support</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Help Center</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Contact Support</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Community</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Status Page</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white transition-colors">Terms of Service</a></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 mt-12 pt-8">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <p className="text-gray-400 text-sm">
                © 2024 VelocityPost.ai - AI Social Media Automation Platform. All rights reserved.
              </p>
              <div className="flex items-center space-x-4 mt-4 md:mt-0">
                <span className="text-gray-400 text-sm">Powered by</span>
                <div className="flex items-center space-x-2">
                  <span className="text-blue-400 font-medium">Mistral AI</span>
                  <span className="text-gray-500">•</span>
                  <span className="text-purple-400 font-medium">Groq</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </footer>

      {/* Custom CSS for animations */}
      <style jsx>{`
        @keyframes blob {
          0% {
            transform: translate(0px, 0px) scale(1);
          }
          33% {
            transform: translate(30px, -50px) scale(1.1);
          }
          66% {
            transform: translate(-20px, 20px) scale(0.9);
          }
          100% {
            transform: translate(0px, 0px) scale(1);
          }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
        .animate-fade-in {
          animation: fadeIn 0.3s ease-in-out;
        }
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
      `}</style>
    </div>
  );
};

export default LandingPage;