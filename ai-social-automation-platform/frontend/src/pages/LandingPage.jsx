import React, { useState, useEffect } from 'react';
import { 
  ArrowRight, Bot, Zap, Shield, Check, Star, Play, Clock, Globe, Award,
  MessageSquare, ChevronDown, ChevronUp, Menu, X, ArrowUp, MapPin, 
  Calendar, Mail, Phone, Users, TrendingUp, BarChart3, Instagram,
  Facebook, Twitter, Linkedin, Youtube, Sparkles, Heart, Eye, Share2
} from 'lucide-react';

const LandingPage = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [currentTestimonial, setCurrentTestimonial] = useState(0);
  const [currentFAQ, setCurrentFAQ] = useState(null);
  const [showScrollTop, setShowScrollTop] = useState(false);
  const [animatedStats, setAnimatedStats] = useState({
    users: 0,
    posts: 0,
    countries: 0,
    satisfaction: 0
  });

  // Mock testimonials data
  const testimonials = [
    {
      name: 'Priya Sharma',
      role: 'Digital Marketing Manager', 
      company: 'TechVenture India',
      image: '👩‍💼',
      content: 'VelocityPost.ai completely transformed our social media strategy. We went from posting 2-3 times per week to having AI generate and post high-quality content across 6 platforms daily.',
      rating: 5
    },
    {
      name: 'Rajesh Kumar',
      role: 'Startup Founder',
      company: 'FoodieApp', 
      image: '👨‍💻',
      content: 'As a bootstrapped startup, we could not afford a social media team. VelocityPost.ai became our secret weapon, generating amazing food content automatically.',
      rating: 5
    },
    {
      name: 'Sarah Chen',
      role: 'E-commerce Manager',
      company: 'Fashion Forward',
      image: '👩‍🎨', 
      content: 'The AI understands our brand voice perfectly. It creates fashion content that gets 3x more engagement than our manual posts ever did.',
      rating: 5
    }
  ];

  const faqs = [
    {
      category: "Getting Started",
      questions: [
        {
          question: "How quickly can I start using VelocityPost.ai?",
          answer: "You can be up and running in under 5 minutes! Simply sign up, connect your social accounts using secure OAuth, and our AI starts working immediately."
        },
        {
          question: "Is my social media data safe?",
          answer: "Absolutely! We use enterprise-grade OAuth 2.0 security. We NEVER see or store your passwords. All data is encrypted with military-grade security."
        },
        {
          question: "How is this different from Buffer or Hootsuite?",
          answer: "Unlike Buffer which only schedules manually-created posts, our AI generates unlimited content automatically. You set it and forget it - no more writer's block!"
        }
      ]
    },
    {
      category: "AI & Content",
      questions: [
        {
          question: "How does the AI content generation work?",
          answer: "Our AI uses advanced language models combined with real-time trend analysis to create content tailored to each platform's best practices and your brand voice."
        },
        {
          question: "Can I customize the AI's writing style?",
          answer: "Yes! Our AI learns your brand voice and adapts to your preferred tone, style, and industry-specific terminology over time."
        }
      ]
    },
    {
      category: "Pricing & Plans",
      questions: [
        {
          question: "Is there really a free plan forever?",
          answer: "Yes! Our free plan includes 2 platforms and 2 AI-generated posts per day. Perfect for individuals and small businesses getting started."
        },
        {
          question: "Can I upgrade or downgrade anytime?",
          answer: "Absolutely! You can change your plan anytime. Upgrades take effect immediately, downgrades at the next billing cycle."
        }
      ]
    }
  ];

  const features = [
    {
      icon: Bot,
      title: "AI Content Generation",
      description: "Advanced AI creates engaging, brand-aligned content automatically across all platforms",
      highlight: "10x faster than manual",
      gradient: "from-blue-500 to-purple-500"
    },
    {
      icon: Zap,
      title: "Complete Automation", 
      description: "Zero manual work - AI handles creation, optimization, and posting 24/7",
      highlight: "Set & forget",
      gradient: "from-purple-500 to-pink-500"
    },
    {
      icon: Shield,
      title: "Enterprise Security",
      description: "Bank-grade OAuth 2.0 security - we never see your passwords",
      highlight: "Military-grade encryption",
      gradient: "from-green-500 to-teal-500"
    },
    {
      icon: TrendingUp,
      title: "Smart Optimization",
      description: "AI analyzes performance and optimizes content for maximum engagement", 
      highlight: "127% better results",
      gradient: "from-orange-500 to-red-500"
    },
    {
      icon: Globe,
      title: "Multi-Platform Mastery",
      description: "Optimized content for Instagram, Facebook, Twitter, LinkedIn, YouTube & more",
      highlight: "7 platforms supported", 
      gradient: "from-cyan-500 to-blue-500"
    },
    {
      icon: BarChart3,
      title: "Advanced Analytics",
      description: "Deep insights into what works, with AI recommendations for improvement",
      highlight: "Data-driven growth",
      gradient: "from-violet-500 to-purple-500"
    }
  ];

  const platforms = [
    { icon: Instagram, name: 'Instagram', color: 'bg-gradient-to-r from-purple-500 to-pink-500' },
    { icon: Facebook, name: 'Facebook', color: 'bg-blue-600' },
    { icon: Twitter, name: 'Twitter', color: 'bg-sky-500' },
    { icon: Linkedin, name: 'LinkedIn', color: 'bg-blue-700' },
    { icon: Youtube, name: 'YouTube', color: 'bg-red-600' }
  ];

  const pricingPlans = [
    {
      name: 'Free Forever',
      price: '₹0',
      period: 'forever',
      description: 'Perfect for individuals getting started',
      features: [
        '2 social media platforms',
        '2 AI posts per day',
        'Basic analytics',
        'Standard support',
        'Community access'
      ],
      popular: false,
      cta: 'Start Free Forever',
      gradient: 'from-gray-500 to-gray-600'
    },
    {
      name: 'Pro Velocity',
      price: '₹2,999',
      period: 'per month',
      originalPrice: '₹4,999',
      description: 'For growing businesses',
      features: [
        '5 social media platforms',
        '50 AI posts per day',
        'Advanced analytics',
        'Priority support',
        'Custom brand voice',
        'Performance optimization',
        'Content calendar'
      ],
      popular: true,
      cta: 'Start Pro Trial',
      gradient: 'from-blue-600 to-purple-600'
    },
    {
      name: 'Agency Power',
      price: '₹9,999', 
      period: 'per month',
      originalPrice: '₹14,999',
      description: 'For agencies & enterprises',
      features: [
        'Unlimited platforms',
        'Unlimited AI posts',
        'White-label solution',
        'Dedicated support',
        'Custom integrations',
        'Team collaboration',
        'Advanced reporting',
        'API access'
      ],
      popular: false,
      cta: 'Contact Sales',
      gradient: 'from-purple-600 to-pink-600'
    }
  ];

  // Animate statistics on mount
  useEffect(() => {
    const timer = setTimeout(() => {
      const interval = setInterval(() => {
        setAnimatedStats(prev => ({
          users: Math.min(prev.users + 500, 25000),
          posts: Math.min(prev.posts + 100000, 5200000), 
          countries: Math.min(prev.countries + 2, 150),
          satisfaction: Math.min(prev.satisfaction + 1, 98)
        }));
      }, 50);

      setTimeout(() => clearInterval(interval), 2000);
    }, 500);

    return () => clearTimeout(timer);
  }, []);

  // Auto-rotate testimonials
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTestimonial((prev) => (prev + 1) % testimonials.length);
    }, 6000);
    return () => clearInterval(timer);
  }, [testimonials.length]);

  // Handle scroll for back-to-top button
  useEffect(() => {
    const handleScroll = () => {
      setShowScrollTop(window.scrollY > 400);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const toggleFAQ = (categoryIndex, questionIndex) => {
    const faqKey = `${categoryIndex}-${questionIndex}`;
    setCurrentFAQ(currentFAQ === faqKey ? null : faqKey);
  };

  const scrollToSection = (sectionId) => {
    const element = document.getElementById(sectionId);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
    setIsMenuOpen(false);
  };

  const handleLoginClick = () => {
    window.location.href = '#login';
  };

  const handleRegisterClick = () => {
    window.location.href = '#register';
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Header */}
      <header className="bg-white/95 backdrop-blur-md shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <div className="relative">
                <div className="w-12 h-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl flex items-center justify-center">
                  <Bot className="w-6 h-6 text-white" />
                </div>
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full animate-ping"></div>
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-500 rounded-full"></div>
              </div>
              <div className="ml-4">
                <h1 className="text-2xl font-bold text-gray-900">
                  VelocityPost<span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">.ai</span>
                </h1>
                <p className="text-xs text-gray-600 font-medium">AI Social Media Automation</p>
              </div>
            </div>

            <nav className="hidden md:flex space-x-8">
              <button onClick={() => scrollToSection('features')} className="text-gray-600 hover:text-blue-600 transition-colors font-medium">Features</button>
              <button onClick={() => scrollToSection('pricing')} className="text-gray-600 hover:text-blue-600 transition-colors font-medium">Pricing</button>
              <button onClick={() => scrollToSection('testimonials')} className="text-gray-600 hover:text-blue-600 transition-colors font-medium">Success Stories</button>
              <button onClick={() => scrollToSection('faq')} className="text-gray-600 hover:text-blue-600 transition-colors font-medium">FAQ</button>
            </nav>

            <div className="hidden md:flex items-center space-x-4">
              <button 
                onClick={handleLoginClick}
                className="text-gray-600 hover:text-blue-600 font-medium transition-colors px-4 py-2 rounded-lg hover:bg-gray-50"
              >
                Login
              </button>
              <button 
                onClick={handleRegisterClick}
                className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-6 py-2 rounded-xl font-medium transition-all duration-300 transform hover:scale-105 shadow-lg inline-flex items-center space-x-2"
              >
                <span>Start Free</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>

            <button
              className="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>

          {isMenuOpen && (
            <div className="md:hidden py-4 border-t bg-white shadow-lg rounded-b-lg">
              <div className="flex flex-col space-y-4">
                <button onClick={() => scrollToSection('features')} className="text-gray-600 hover:text-blue-600 transition-colors text-left py-2">Features</button>
                <button onClick={() => scrollToSection('pricing')} className="text-gray-600 hover:text-blue-600 transition-colors text-left py-2">Pricing</button>
                <button onClick={() => scrollToSection('testimonials')} className="text-gray-600 hover:text-blue-600 transition-colors text-left py-2">Success Stories</button>
                <button onClick={() => scrollToSection('faq')} className="text-gray-600 hover:text-blue-600 transition-colors text-left py-2">FAQ</button>
                <div className="flex flex-col space-y-3 pt-4 border-t">
                  <button 
                    onClick={handleLoginClick}
                    className="text-gray-600 hover:text-blue-600 transition-colors py-2 text-left"
                  >
                    Login
                  </button>
                  <button 
                    onClick={handleRegisterClick}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-3 rounded-xl text-center font-medium transition-all"
                  >
                    Start Free Trial
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 py-20 overflow-hidden">
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-10 left-10 w-72 h-72 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse"></div>
          <div className="absolute top-10 right-10 w-72 h-72 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse"></div>
          <div className="absolute -bottom-8 left-20 w-72 h-72 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse"></div>
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <div className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-blue-100 to-purple-100 rounded-full text-blue-800 text-sm font-medium mb-8 animate-bounce">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-3 animate-ping"></span>
              🎉 Join 25,000+ creators posting at AI velocity - Limited time: 40% OFF Pro plans!
            </div>
            
            <h1 className="text-4xl md:text-7xl font-bold text-gray-900 mb-6 leading-tight">
              Social Media at
              <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent block mt-2 animate-pulse">
                AI Velocity
              </span>
            </h1>
            
            <p className="text-xl md:text-2xl text-gray-600 mb-4 max-w-4xl mx-auto leading-relaxed">
              Stop manually creating content. Our AI agents <span className="font-semibold text-blue-600">generate and post viral content</span> 
              across all your social platforms 24/7.
            </p>
            
            <p className="text-lg text-gray-500 mb-8 max-w-3xl mx-auto">
              ✨ <strong>Pure automation.</strong> ⚡ <strong>Zero manual work.</strong> 📈 <strong>Maximum growth.</strong> 
              🚀 <strong>10x faster than Buffer.</strong>
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <button 
                onClick={handleRegisterClick}
                className="group bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white px-8 py-4 rounded-xl text-xl font-semibold transition-all duration-300 transform hover:scale-105 shadow-2xl inline-flex items-center justify-center animate-pulse"
              >
                🚀 Start Free Forever
                <ArrowRight className="ml-3 h-6 w-6 group-hover:translate-x-1 transition-transform" />
              </button>
              <button className="group border-2 border-gray-300 hover:border-blue-500 text-gray-700 hover:text-blue-600 px-8 py-4 rounded-xl text-xl font-semibold transition-all duration-300 hover:shadow-lg inline-flex items-center justify-center">
                <Play className="mr-3 h-6 w-6 group-hover:scale-110 transition-transform" />
                Watch 2-Min Demo
              </button>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center text-sm text-gray-500 mb-12">
              <div className="flex items-center justify-center space-x-2">
                <Shield className="w-5 h-5 text-green-500" />
                <span className="font-medium">No credit card required</span>
              </div>
              <div className="flex items-center justify-center space-x-2">
                <Clock className="w-5 h-5 text-blue-500" />
                <span className="font-medium">5-minute setup</span>
              </div>
              <div className="flex items-center justify-center space-x-2">
                <Zap className="w-5 h-5 text-purple-500" />
                <span className="font-medium">Cancel anytime</span>
              </div>
              <div className="flex items-center justify-center space-x-2">
                <Award className="w-5 h-5 text-yellow-500" />
                <span className="font-medium">24/7 Support</span>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105">
                <div className="text-4xl mb-3">👥</div>
                <div className="text-3xl md:text-4xl font-bold text-blue-600 mb-2 transition-all duration-1000">
                  {animatedStats.users.toLocaleString()}+
                </div>
                <div className="text-gray-600 font-medium">Active Users</div>
                <div className="text-xs text-gray-500 mt-1">Growing daily</div>
              </div>
              
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105">
                <div className="text-4xl mb-3">📝</div>
                <div className="text-3xl md:text-4xl font-bold text-purple-600 mb-2 transition-all duration-1000">
                  {(animatedStats.posts / 1000000).toFixed(1)}M+
                </div>
                <div className="text-gray-600 font-medium">Posts Generated</div>
                <div className="text-xs text-gray-500 mt-1">AI-powered content</div>
              </div>
              
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105">
                <div className="text-4xl mb-3">🌍</div>
                <div className="text-3xl md:text-4xl font-bold text-green-600 mb-2 transition-all duration-1000">
                  {animatedStats.countries}+
                </div>
                <div className="text-gray-600 font-medium">Countries</div>
                <div className="text-xs text-gray-500 mt-1">Global reach</div>
              </div>
              
              <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-xl hover:shadow-2xl transition-all duration-300 transform hover:scale-105">
                <div className="text-4xl mb-3">⭐</div>
                <div className="text-3xl md:text-4xl font-bold text-yellow-600 mb-2 transition-all duration-1000">
                  {animatedStats.satisfaction}%
                </div>
                <div className="text-gray-600 font-medium">Satisfaction</div>
                <div className="text-xs text-gray-500 mt-1">Customer happiness</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-6">
              Everything You Need for <span className="text-blue-600">Social Velocity</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Comprehensive AI-powered features designed to accelerate your social media growth
              while maintaining quality and authenticity.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => {
              const IconComponent = feature.icon;
              return (
                <div key={index} className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-2xl transition-all duration-300 group border border-gray-200 hover:border-blue-300 transform hover:scale-105">
                  <div className="flex items-center mb-6">
                    <div className={`w-16 h-16 bg-gradient-to-r ${feature.gradient} rounded-2xl flex items-center justify-center mr-4 group-hover:scale-110 transition-transform shadow-lg`}>
                      <IconComponent className="w-8 h-8 text-white" />
                    </div>
                    <span className="text-xs font-semibold text-white bg-gradient-to-r from-green-500 to-emerald-500 px-3 py-1 rounded-full">
                      {feature.highlight}
                    </span>
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-3 group-hover:text-blue-600 transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 mb-6">{feature.description}</p>
                  <button className="text-blue-600 hover:text-blue-700 font-medium inline-flex items-center group">
                    Learn More <ArrowRight className="w-4 h-4 ml-2 group-hover:translate-x-1 transition-transform" />
                  </button>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Supported Platforms */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-6">
              Works with <span className="text-blue-600">All Major Platforms</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Connect once, post everywhere. Our AI optimizes content for each platform automatically.
            </p>
          </div>

          <div className="flex flex-wrap justify-center items-center gap-8">
            {platforms.map((platform, index) => {
              const IconComponent = platform.icon;
              return (
                <div key={index} className="flex flex-col items-center group">
                  <div className={`w-20 h-20 ${platform.color} rounded-2xl flex items-center justify-center mb-4 shadow-lg group-hover:scale-110 transition-all duration-300`}>
                    <IconComponent className="w-10 h-10 text-white" />
                  </div>
                  <span className="text-gray-700 font-medium group-hover:text-blue-600 transition-colors">{platform.name}</span>
                </div>
              );
            })}
            <div className="flex flex-col items-center group">
              <div className="w-20 h-20 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mb-4 shadow-lg group-hover:scale-110 transition-all duration-300">
                <span className="text-white font-bold text-lg">+2</span>
              </div>
              <span className="text-gray-700 font-medium group-hover:text-blue-600 transition-colors">More</span>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-6">
              Choose Your <span className="text-blue-600">Velocity Plan</span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
              Start free, scale fast. Choose the plan that matches your social media velocity goals.
            </p>
            <div className="inline-flex items-center px-6 py-3 bg-gradient-to-r from-green-100 to-emerald-100 rounded-full text-green-800 text-sm font-medium">
              <span className="w-2 h-2 bg-green-500 rounded-full mr-3 animate-pulse"></span>
              💰 Limited Time: 40% OFF on all paid plans!
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {pricingPlans.map((plan, index) => (
              <div key={index} className={`bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 border-2 ${plan.popular ? 'border-blue-500 transform scale-105' : 'border-gray-200'} relative`}>
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-full text-sm font-bold">
                      ⭐ Most Popular
                    </span>
                  </div>
                )}
                
                <div className="text-center mb-8">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                  {plan.originalPrice && (
                    <div className="text-lg line-through text-gray-400 mb-1">{plan.originalPrice}</div>
                  )}
                  <div className="flex items-baseline justify-center">
                    <span className="text-5xl font-bold text-gray-900">{plan.price}</span>
                    <span className="text-lg ml-1 text-gray-600">/{plan.period}</span>
                  </div>
                  <p className="text-gray-600 mt-2">{plan.description}</p>
                </div>
                
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center">
                      <Check className="h-5 w-5 text-green-500 mr-3 flex-shrink-0" />
                      <span className="text-sm text-gray-600">{feature}</span>
                    </li>
                  ))}
                </ul>
                
                <button 
                  onClick={handleRegisterClick}
                  className={`w-full py-4 rounded-xl font-semibold transition-all duration-300 ${
                    plan.popular 
                      ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700 shadow-lg' 
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {plan.cta}
                </button>
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <p className="text-gray-600 mb-4">Need something custom? We've got you covered.</p>
            <button className="text-blue-600 hover:text-blue-700 font-medium inline-flex items-center">
              Contact our sales team <ArrowRight className="w-4 h-4 ml-2" />
            </button>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-6">
              Loved by Creators <span className="text-blue-600">Worldwide</span>
            </h2>
            <p className="text-xl text-gray-600">
              Join thousands of businesses already growing with AI-powered social media automation.
            </p>
          </div>

          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white mb-12 relative overflow-hidden">
            <div className="relative max-w-4xl mx-auto text-center">
              <div className="flex justify-center mb-6">
                {[...Array(testimonials[currentTestimonial].rating)].map((_, i) => (
                  <Star key={i} className="w-8 h-8 text-yellow-400 fill-current" />
                ))}
              </div>
              
              <blockquote className="text-xl md:text-2xl font-medium mb-8 leading-relaxed">
                "{testimonials[currentTestimonial].content}"
              </blockquote>
              
              <div className="flex items-center justify-center space-x-6">
                <div className="text-5xl">{testimonials[currentTestimonial].image}</div>
                <div className="text-left">
                  <div className="font-bold text-xl">{testimonials[currentTestimonial].name}</div>
                  <div className="text-blue-200 text-lg">{testimonials[currentTestimonial].role}</div>
                  <div className="text-blue-100">{testimonials[currentTestimonial].company}</div>
                </div>
              </div>
            </div>

            <div className="flex justify-center mt-6 space-x-2">
              {testimonials.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentTestimonial(index)}
                  className={`w-3 h-3 rounded-full transition-all ${
                    index === currentTestimonial ? 'bg-white' : 'bg-white/50'
                  }`}
                />
              ))}
            </div>
          </div>

          {/* Customer Logos */}
          <div className="text-center">
            <p className="text-gray-600 mb-8">Trusted by innovative companies worldwide</p>
            <div className="flex justify-center items-center space-x-12 opacity-60">
              <div className="text-2xl font-bold text-gray-400">TechCorp</div>
              <div className="text-2xl font-bold text-gray-400">StartupXYZ</div>
              <div className="text-2xl font-bold text-gray-400">GrowthCo</div>
              <div className="text-2xl font-bold text-gray-400">InnovateInc</div>
              <div className="text-2xl font-bold text-gray-400">FutureApp</div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-20 bg-white">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-5xl font-bold text-gray-900 mb-6">
              Frequently Asked <span className="text-blue-600">Questions</span>
            </h2>
            <p className="text-xl text-gray-600">
              Everything you need to know about VelocityPost.ai and AI-powered social media automation
            </p>
          </div>

          <div className="space-y-6">
            {faqs.map((category, categoryIndex) => (
              <div key={categoryIndex}>
                <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mr-3"></div>
                  {category.category}
                </h3>
                
                <div className="space-y-3 mb-8">
                  {category.questions.map((faq, questionIndex) => {
                    const faqKey = `${categoryIndex}-${questionIndex}`;
                    const isOpen = currentFAQ === faqKey;
                    
                    return (
                      <div key={questionIndex} className="bg-gray-50 rounded-lg overflow-hidden">
                        <button
                          onClick={() => toggleFAQ(categoryIndex, questionIndex)}
                          className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-gray-100 transition-colors"
                        >
                          <span className="font-medium text-gray-900">{faq.question}</span>
                          {isOpen ? (
                            <ChevronUp className="w-5 h-5 text-gray-500" />
                          ) : (
                            <ChevronDown className="w-5 h-5 text-gray-500" />
                          )}
                        </button>
                        {isOpen && (
                          <div className="px-6 pb-4 text-gray-600 leading-relaxed">
                            {faq.answer}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <p className="text-gray-600 mb-4">Still have questions?</p>
            <button className="text-blue-600 hover:text-blue-700 font-medium inline-flex items-center">
              Contact our support team <ArrowRight className="w-4 h-4 ml-2" />
            </button>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="text-white">
            <h2 className="text-3xl md:text-5xl font-bold mb-6">
              Ready to Go <span className="text-yellow-300">Viral</span> with AI?
            </h2>
            <p className="text-xl md:text-2xl mb-8 text-blue-100">
              Join thousands of creators who've already automated their social media success.
              Start your free account today - no credit card required!
            </p>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
              <button 
                onClick={handleRegisterClick}
                className="bg-white text-blue-600 px-8 py-4 rounded-xl text-xl font-semibold hover:bg-gray-100 transition-all duration-300 transform hover:scale-105 shadow-lg inline-flex items-center justify-center"
              >
                🚀 Start Free Forever
                <ArrowRight className="ml-3 h-6 w-6" />
              </button>
              <button className="border-2 border-white text-white px-8 py-4 rounded-xl text-xl font-semibold hover:bg-white hover:text-blue-600 transition-all duration-300 inline-flex items-center justify-center">
                <Play className="mr-3 h-6 w-6" />
                Watch Demo
              </button>
            </div>

            <div className="flex items-center justify-center space-x-8 text-sm text-blue-100">
              <div className="flex items-center space-x-2">
                <Shield className="w-4 h-4" />
                <span>No credit card required</span>
              </div>
              <div className="flex items-center space-x-2">
                <Clock className="w-4 h-4" />
                <span>Setup in 5 minutes</span>
              </div>
              <div className="flex items-center space-x-2">
                <Award className="w-4 h-4" />
                <span>Cancel anytime</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center mb-4">
                <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center mr-3">
                  <Bot className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-white">
                  VelocityPost<span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">.ai</span>
                </h3>
              </div>
              <p className="text-gray-400 mb-6 max-w-md">
                AI-powered social media automation that helps businesses grow their online presence 
                with zero manual work. Join thousands of creators posting at AI velocity.
              </p>
              <div className="flex space-x-4">
                <button className="bg-gray-800 p-3 rounded-lg hover:bg-gray-700 transition-colors">
                  <Twitter className="w-5 h-5" />
                </button>
                <button className="bg-gray-800 p-3 rounded-lg hover:bg-gray-700 transition-colors">
                  <Linkedin className="w-5 h-5" />
                </button>
                <button className="bg-gray-800 p-3 rounded-lg hover:bg-gray-700 transition-colors">
                  <Youtube className="w-5 h-5" />
                </button>
                <button className="bg-gray-800 p-3 rounded-lg hover:bg-gray-700 transition-colors">
                  <Instagram className="w-5 h-5" />
                </button>
              </div>
            </div>

            <div>
              <h4 className="text-white font-semibold mb-4">Product</h4>
              <ul className="space-y-2">
                <li><button className="hover:text-white transition-colors">Features</button></li>
                <li><button className="hover:text-white transition-colors">Pricing</button></li>
                <li><button className="hover:text-white transition-colors">Integrations</button></li>
                <li><button className="hover:text-white transition-colors">API</button></li>
                <li><button className="hover:text-white transition-colors">Changelog</button></li>
              </ul>
            </div>

            <div>
              <h4 className="text-white font-semibold mb-4">Company</h4>
              <ul className="space-y-2">
                <li><button className="hover:text-white transition-colors">About</button></li>
                <li><button className="hover:text-white transition-colors">Blog</button></li>
                <li><button className="hover:text-white transition-colors">Careers</button></li>
                <li><button className="hover:text-white transition-colors">Contact</button></li>
                <li><button className="hover:text-white transition-colors">Privacy</button></li>
                <li><button className="hover:text-white transition-colors">Terms</button></li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 pt-8 mt-12">
            <div className="flex flex-col md:flex-row justify-between items-center">
              <p className="text-gray-400 text-sm">
                © 2024 VelocityPost.ai. All rights reserved. Made with ❤️ for creators worldwide.
              </p>
              <div className="flex items-center space-x-6 mt-4 md:mt-0">
                <div className="flex items-center space-x-2 text-sm text-gray-400">
                  <MapPin className="w-4 h-4" />
                  <span>Aizawl, Mizoram, India</span>
                </div>
                <div className="flex items-center space-x-2 text-sm text-gray-400">
                  <Mail className="w-4 h-4" />
                  <span>hello@velocitypost.ai</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </footer>

      {/* Back to Top Button */}
      {showScrollTop && (
        <button
          onClick={scrollToTop}
          className="fixed bottom-8 right-8 bg-gradient-to-r from-blue-600 to-purple-600 text-white p-3 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-110 z-50"
        >
          <ArrowUp className="w-6 h-6" />
        </button>
      )}
    </div>
  );
};

export default LandingPage;