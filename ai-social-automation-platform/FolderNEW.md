# VelocityPost.ai - AI Social Media Automation Platform
## Complete Project Structure

This document outlines the complete directory structure for VelocityPost.ai, an AI-powered social media automation platform that generates content using AI and auto-posts to multiple social platforms.

## Project Overview
- **Frontend**: React + Vite + TailwindCSS
- **Backend**: Python Flask + MongoDB + Celery + Redis
- **AI Services**: Mistral AI + Groq + OpenAI
- **Social Media APIs**: OAuth 2.0 integration with all major platforms
- **Payment**: Stripe + Razorpay (UPI for India)

## Directory Structure

```
velocitypost-ai/
├── README.md
├── .gitignore
├── docker-compose.yml
├── LICENSE
│
├── frontend/                                    # React Frontend Application
│   ├── public/
│   │   ├── index.html
│   │   ├── favicon.ico
│   │   ├── logo.svg
│   │   ├── manifest.json
│   │   └── robots.txt
│   │
│   ├── src/
│   │   ├── main.jsx                            # React entry point
│   │   ├── App.jsx                             # Main app component with routing
│   │   ├── index.css                           # Global styles
│   │   │
│   │   ├── components/                         # Reusable components
│   │   │   ├── common/                         # Common UI components
│   │   │   │   ├── Header.jsx
│   │   │   │   ├── Sidebar.jsx
│   │   │   │   ├── Footer.jsx
│   │   │   │   ├── LoadingSpinner.jsx
│   │   │   │   ├── Modal.jsx
│   │   │   │   ├── Toast.jsx
│   │   │   │   ├── ErrorBoundary.jsx
│   │   │   │   └── SEOHead.jsx
│   │   │   │
│   │   │   ├── layout/                         # Layout components
│   │   │   │   ├── Layout.jsx
│   │   │   │   ├── DashboardLayout.jsx
│   │   │   │   ├── AuthLayout.jsx
│   │   │   │   ├── LandingLayout.jsx
│   │   │   │   └── PublicLayout.jsx
│   │   │   │
│   │   │   ├── ui/                             # UI components (shadcn/ui style)
│   │   │   │   ├── Button.jsx
│   │   │   │   ├── Input.jsx
│   │   │   │   ├── Card.jsx
│   │   │   │   ├── Badge.jsx
│   │   │   │   ├── Avatar.jsx
│   │   │   │   ├── Dropdown.jsx
│   │   │   │   ├── Tabs.jsx
│   │   │   │   ├── Dialog.jsx
│   │   │   │   ├── Switch.jsx
│   │   │   │   ├── Slider.jsx
│   │   │   │   ├── Table.jsx
│   │   │   │   └── Progress.jsx
│   │   │   │
│   │   │   ├── landing/                        # Landing page components
│   │   │   │   ├── HeroSection.jsx
│   │   │   │   ├── FeaturesSection.jsx
│   │   │   │   ├── PlatformsSection.jsx
│   │   │   │   ├── PricingSection.jsx
│   │   │   │   ├── TestimonialsSection.jsx
│   │   │   │   ├── HowItWorksSection.jsx
│   │   │   │   ├── FAQSection.jsx
│   │   │   │   ├── CTASection.jsx
│   │   │   │   ├── StatsSection.jsx
│   │   │   │   ├── IntegrationsSection.jsx
│   │   │   │   └── DemoSection.jsx
│   │   │   │
│   │   │   ├── auth/                           # Authentication components
│   │   │   │   ├── LoginForm.jsx
│   │   │   │   ├── RegisterForm.jsx
│   │   │   │   ├── ForgotPasswordForm.jsx
│   │   │   │   ├── ResetPasswordForm.jsx
│   │   │   │   ├── ProtectedRoute.jsx
│   │   │   │   ├── PublicRoute.jsx
│   │   │   │   ├── OAuthButtons.jsx
│   │   │   │   └── OAuthCallback.jsx           # 🔥 NEW: OAuth callback handler
│   │   │   │
│   │   │   ├── dashboard/                      # Dashboard components
│   │   │   │   ├── MetricsCard.jsx
│   │   │   │   ├── ActivityFeed.jsx
│   │   │   │   ├── QuickActions.jsx
│   │   │   │   ├── RecentPosts.jsx
│   │   │   │   ├── PlatformStatus.jsx
│   │   │   │   ├── VelocityScore.jsx
│   │   │   │   └── GrowthChart.jsx
│   │   │   │
│   │   │   ├── platforms/                      # Platform connection components
│   │   │   │   ├── PlatformCard.jsx
│   │   │   │   ├── ConnectButton.jsx
│   │   │   │   ├── StatusBadge.jsx
│   │   │   │   ├── ConnectionModal.jsx
│   │   │   │   └── PlatformGrid.jsx
│   │   │   │
│   │   │   ├── credentials/                    # Credential management
│   │   │   │   ├── CredentialForm.jsx
│   │   │   │   ├── ConnectionTest.jsx
│   │   │   │   ├── SecurityBadge.jsx
│   │   │   │   └── TwoFactorSetup.jsx
│   │   │   │
│   │   │   ├── domains/                        # Content domain selection
│   │   │   │   ├── DomainSelector.jsx
│   │   │   │   ├── DomainCard.jsx
│   │   │   │   ├── ContentPreview.jsx
│   │   │   │   ├── PostingSchedule.jsx
│   │   │   │   └── NicheSettings.jsx
│   │   │   │
│   │   │   ├── content/                        # Content management
│   │   │   │   ├── ContentCard.jsx
│   │   │   │   ├── ContentEditor.jsx
│   │   │   │   ├── ContentFilter.jsx
│   │   │   │   ├── ContentCalendar.jsx
│   │   │   │   ├── ContentTemplates.jsx
│   │   │   │   ├── BulkActions.jsx
│   │   │   │   └── FileUpload.jsx              # 🔥 NEW: Multi-format file upload
│   │   │   │
│   │   │   ├── automation/                     # Automation components
│   │   │   │   ├── AutoReplySetup.jsx
│   │   │   │   ├── WorkflowBuilder.jsx
│   │   │   │   ├── RuleBuilder.jsx
│   │   │   │   ├── ScheduleManager.jsx
│   │   │   │   ├── AutomationStatus.jsx
│   │   │   │   └── VelocityControls.jsx
│   │   │   │
│   │   │   ├── analytics/                      # Analytics components
│   │   │   │   ├── Chart.jsx
│   │   │   │   ├── MetricsTable.jsx
│   │   │   │   ├── ExportData.jsx
│   │   │   │   ├── EngagementChart.jsx
│   │   │   │   ├── GrowthMetrics.jsx
│   │   │   │   ├── PlatformBreakdown.jsx
│   │   │   │   └── ReportGenerator.jsx
│   │   │   │
│   │   │   ├── messaging/                      # Messaging components
│   │   │   │   ├── MessageCenter.jsx
│   │   │   │   ├── AutoReplyTemplates.jsx
│   │   │   │   ├── ConversationView.jsx
│   │   │   │   ├── WhatsAppSetup.jsx
│   │   │   │   └── EmailTemplates.jsx
│   │   │   │
│   │   │   ├── reviews/                        # Review management
│   │   │   │   ├── ReviewCard.jsx
│   │   │   │   ├── ResponseTemplates.jsx
│   │   │   │   ├── SentimentAnalysis.jsx
│   │   │   │   ├── ReviewMonitor.jsx
│   │   │   │   └── ReputationScore.jsx
│   │   │   │
│   │   │   ├── ecommerce/                      # E-commerce integration
│   │   │   │   ├── ShopifyIntegration.jsx
│   │   │   │   ├── ProductSync.jsx
│   │   │   │   ├── OrderNotifications.jsx
│   │   │   │   └── InventoryAlerts.jsx
│   │   │   │
│   │   │   ├── billing/                        # Billing components
│   │   │   │   ├── PlanSelector.jsx
│   │   │   │   ├── UsageTracker.jsx
│   │   │   │   ├── PaymentMethod.jsx
│   │   │   │   ├── InvoiceHistory.jsx
│   │   │   │   └── UpgradeModal.jsx
│   │   │   │
│   │   │   └── settings/                       # Settings components
│   │   │       ├── ProfileSettings.jsx
│   │   │       ├── BusinessInfo.jsx
│   │   │       ├── NotificationSettings.jsx
│   │   │       ├── SecuritySettings.jsx
│   │   │       ├── IntegrationSettings.jsx
│   │   │       └── TeamManagement.jsx
│   │   │
│   │   ├── pages/                              # Page components
│   │   │   ├── public/                         # Public pages
│   │   │   │   ├── LandingPage.jsx
│   │   │   │   ├── AboutPage.jsx
│   │   │   │   ├── FeaturesPage.jsx
│   │   │   │   ├── PricingPage.jsx
│   │   │   │   ├── ContactPage.jsx
│   │   │   │   ├── BlogPage.jsx
│   │   │   │   ├── DocumentationPage.jsx
│   │   │   │   ├── PrivacyPage.jsx
│   │   │   │   └── TermsPage.jsx
│   │   │   │
│   │   │   ├── auth/                           # Authentication pages
│   │   │   │   ├── Login.jsx
│   │   │   │   ├── Register.jsx
│   │   │   │   ├── ForgotPassword.jsx
│   │   │   │   ├── ResetPassword.jsx
│   │   │   │   ├── VerifyEmail.jsx
│   │   │   │   └── TwoFactorAuth.jsx
│   │   │   │
│   │   │   ├── onboarding/                     # Onboarding flow
│   │   │   │   ├── Welcome.jsx
│   │   │   │   ├── PlanSelection.jsx
│   │   │   │   ├── BusinessSetup.jsx
│   │   │   │   ├── PlatformConnection.jsx
│   │   │   │   ├── DomainSelection.jsx
│   │   │   │   ├── AutomationSetup.jsx
│   │   │   │   └── Complete.jsx
│   │   │   │
│   │   │   ├── dashboard/                      # Dashboard pages
│   │   │   │   ├── Dashboard.jsx
│   │   │   │   ├── Overview.jsx
│   │   │   │   └── QuickStart.jsx
│   │   │   │
│   │   │   ├── platforms/                      # Platform management
│   │   │   │   ├── Platforms.jsx               # 🔥 NEW: OAuth platform connections
│   │   │   │   ├── SocialMedia.jsx
│   │   │   │   ├── Messaging.jsx
│   │   │   │   ├── Reviews.jsx
│   │   │   │   ├── Ecommerce.jsx
│   │   │   │   └── ContentPlatforms.jsx
│   │   │   │
│   │   │   ├── autoposting/                    # 🔥 NEW: Auto-posting pages
│   │   │   │   ├── AutoPostingCenter.jsx       # Main auto-posting hub
│   │   │   │   ├── PostingScheduler.jsx        # Schedule configuration
│   │   │   │   └── ContentGenerator.jsx        # AI content generation
│   │   │   │
│   │   │   ├── automation/                     # Automation management
│   │   │   │   ├── AutomationHub.jsx
│   │   │   │   ├── Workflows.jsx
│   │   │   │   ├── AutoReplies.jsx
│   │   │   │   ├── ContentScheduler.jsx
│   │   │   │   ├── ReviewManager.jsx
│   │   │   │   └── VelocityControl.jsx
│   │   │   │
│   │   │   ├── content/                        # Content management
│   │   │   │   ├── ContentLibrary.jsx
│   │   │   │   ├── CreateContent.jsx
│   │   │   │   ├── Templates.jsx
│   │   │   │   ├── Calendar.jsx
│   │   │   │   └── Domains.jsx
│   │   │   │
│   │   │   ├── analytics/                      # Analytics pages
│   │   │   │   ├── Analytics.jsx
│   │   │   │   ├── Reports.jsx
│   │   │   │   ├── Insights.jsx
│   │   │   │   └── Performance.jsx
│   │   │   │
│   │   │   ├── messaging/                      # Messaging pages
│   │   │   │   ├── MessageCenter.jsx
│   │   │   │   ├── WhatsAppBusiness.jsx
│   │   │   │   ├── EmailAutomation.jsx
│   │   │   │   └── InstagramDMs.jsx
│   │   │   │
│   │   │   ├── reviews/                        # Review management
│   │   │   │   ├── ReviewDashboard.jsx
│   │   │   │   ├── GoogleBusiness.jsx
│   │   │   │   ├── YelpManagement.jsx
│   │   │   │   └── ReputationManagement.jsx
│   │   │   │
│   │   │   ├── ecommerce/                      # E-commerce pages
│   │   │   │   ├── EcommerceDashboard.jsx
│   │   │   │   ├── ShopifyIntegration.jsx
│   │   │   │   ├── AmazonSeller.jsx
│   │   │   │   └── OrderManagement.jsx
│   │   │   │
│   │   │   ├── billing/                        # Billing pages
│   │   │   │   ├── BillingDashboard.jsx
│   │   │   │   ├── Subscription.jsx
│   │   │   │   ├── Usage.jsx
│   │   │   │   └── Invoices.jsx
│   │   │   │
│   │   │   ├── settings/                       # Settings pages
│   │   │   │   ├── Settings.jsx
│   │   │   │   ├── Profile.jsx
│   │   │   │   ├── Business.jsx
│   │   │   │   ├── Team.jsx
│   │   │   │   ├── Security.jsx
│   │   │   │   ├── Integrations.jsx
│   │   │   │   └── Notifications.jsx
│   │   │   │
│   │   │   └── error/                          # Error pages
│   │   │       ├── NotFound.jsx
│   │   │       ├── ServerError.jsx
│   │   │       ├── Unauthorized.jsx
│   │   │       └── Maintenance.jsx
│   │   │
│   │   ├── hooks/                              # Custom React hooks
│   │   │   ├── useAuth.js
│   │   │   ├── useAPI.js
│   │   │   ├── usePlatforms.js
│   │   │   ├── useAnalytics.js
│   │   │   ├── useAutomation.js
│   │   │   ├── useContent.js
│   │   │   ├── useMessaging.js
│   │   │   ├── useReviews.js
│   │   │   ├── useEcommerce.js
│   │   │   ├── useBilling.js
│   │   │   ├── useSettings.js
│   │   │   ├── useToast.js
│   │   │   ├── useLocalStorage.js
│   │   │   ├── useDebounce.js
│   │   │   └── useWebSocket.js
│   │   │
│   │   ├── context/                            # React Context providers
│   │   │   ├── AuthContext.jsx
│   │   │   ├── ThemeContext.jsx
│   │   │   ├── BusinessContext.jsx
│   │   │   ├── AutomationContext.jsx
│   │   │   ├── PlatformContext.jsx
│   │   │   └── NotificationContext.jsx
│   │   │
│   │   ├── services/                           # API services
│   │   │   ├── api.js                          # Main API client
│   │   │   ├── authService.js                  # Authentication service
│   │   │   ├── platformService.js              # Platform management
│   │   │   ├── contentService.js               # Content management
│   │   │   ├── analyticsService.js             # Analytics service
│   │   │   ├── automationService.js            # Automation service
│   │   │   ├── messagingService.js             # Messaging service
│   │   │   ├── reviewService.js                # Review service
│   │   │   ├── ecommerceService.js             # E-commerce service
│   │   │   ├── billingService.js               # Billing service
│   │   │   ├── aiService.js                    # AI service
│   │   │   ├── websocketService.js             # WebSocket service
│   │   │   ├── oauthService.js                 # 🔥 NEW: OAuth service
│   │   │   ├── autoPostingService.js           # 🔥 NEW: Auto-posting service
│   │   │   ├── contentGeneratorService.js      # 🔥 NEW: Content generation
│   │   │   └── schedulerService.js             # 🔥 NEW: Scheduler service
│   │   │
│   │   ├── utils/                              # Utility functions
│   │   │   ├── formatters.js
│   │   │   ├── validators.js
│   │   │   ├── constants.js
│   │   │   ├── helpers.js
│   │   │   ├── dateUtils.js
│   │   │   ├── apiHelpers.js
│   │   │   ├── errorHandlers.js
│   │   │   ├── analytics.js
│   │   │   ├── encryption.js
│   │   │   └── urlUtils.js
│   │   │
│   │   ├── lib/                                # Library configurations
│   │   │   ├── axios.js
│   │   │   ├── queryClient.js
│   │   │   ├── auth.js
│   │   │   ├── websocket.js
│   │   │   └── analytics.js
│   │   │
│   │   ├── assets/                             # Static assets
│   │   │   ├── images/
│   │   │   └── icons/
│   │   │
│   │   └── styles/                             # Style files
│   │       ├── globals.css
│   │       ├── components.css
│   │       ├── animations.css
│   │       └── utilities.css
│   │
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── eslint.config.js
│   ├── .env.example
│   ├── .env.local
│   └── .gitignore
│
├── backend/                                     # Flask Backend Application
│   ├── app.py                                  # Main Flask application
│   ├── config.py                               # Configuration settings
│   ├── requirements.txt                        # Python dependencies
│   ├── .env.example                            # Environment variables template
│   ├── celery_app.py                           # Celery configuration
│   ├── run.py                                  # Development server
│   ├── wsgi.py                                 # WSGI entry point
│   │
│   ├── app/                                    # Application package
│   │   ├── __init__.py                         # App factory
│   │   ├── extensions.py                       # Flask extensions
│   │   │
│   │   ├── models/                             # Database models
│   │   │   ├── __init__.py
│   │   │   ├── user.py                         # User model
│   │   │   ├── business.py                     # Business model
│   │   │   ├── platform_connection.py          # Platform connections
│   │   │   ├── content.py                      # Content model
│   │   │   ├── content_domain.py               # Content domains
│   │   │   ├── automation_rule.py              # Automation rules
│   │   │   ├── post.py                         # Post model
│   │   │   ├── analytics.py                    # Analytics model
│   │   │   ├── subscription.py                 # Subscription model
│   │   │   ├── billing.py                      # Billing model
│   │   │   ├── automation_log.py               # Automation logs
│   │   │   ├── message.py                      # Message model
│   │   │   ├── review.py                       # Review model
│   │   │   ├── workflow.py                     # Workflow model
│   │   │   └── template.py                     # Template model
│   │   │
│   │   ├── routes/                             # API routes
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                         # Authentication routes
│   │   │   ├── oauth.py                        # 🔥 NEW: OAuth routes
│   │   │   ├── platforms.py                    # Platform management
│   │   │   ├── content.py                      # Content management
│   │   │   ├── domains.py                      # Content domains
│   │   │   ├── automation.py                   # Automation routes
│   │   │   ├── reviews.py                      # Review management
│   │   │   ├── messaging.py                    # Messaging routes
│   │   │   ├── analytics.py                    # Analytics routes
│   │   │   ├── billing.py                      # Billing routes
│   │   │   ├── ecommerce.py                    # E-commerce routes
│   │   │   ├── webhooks.py                     # Webhook handlers
│   │   │   └── admin.py                        # Admin routes
│   │   │
│   │   ├── services/                           # Business logic services
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── auth/                           # Authentication services
│   │   │   │   ├── auth_service.py
│   │   │   │   ├── jwt_service.py
│   │   │   │   └── oauth_service.py            # 🔥 NEW: OAuth service
│   │   │   │
│   │   │   ├── social_media/                   # Social media services
│   │   │   │   ├── facebook_service.py
│   │   │   │   ├── instagram_service.py
│   │   │   │   ├── youtube_service.py
│   │   │   │   ├── twitter_service.py
│   │   │   │   ├── linkedin_service.py
│   │   │   │   ├── pinterest_service.py
│   │   │   │   ├── tiktok_service.py
│   │   │   │   └── reddit_service.py
│   │   │   │
│   │   │   ├── reviews/                        # Review services
│   │   │   │   ├── google_business.py
│   │   │   │   ├── yelp_service.py
│   │   │   │   ├── trustpilot_service.py
│   │   │   │   ├── tripadvisor_service.py
│   │   │   │   ├── app_store_service.py
│   │   │   │   └── glassdoor_service.py
│   │   │   │
│   │   │   ├── ecommerce/                      # E-commerce services
│   │   │   │   ├── shopify_service.py
│   │   │   │   ├── woocommerce_service.py
│   │   │   │   ├── amazon_service.py
│   │   │   │   ├── etsy_service.py
│   │   │   │   ├── ebay_service.py
│   │   │   │   └── bigcommerce_service.py
│   │   │   │
│   │   │   ├── messaging/                      # Messaging services
│   │   │   │   ├── whatsapp_business.py
│   │   │   │   ├── telegram_service.py
│   │   │   │   ├── email_service.py
│   │   │   │   ├── sms_service.py
│   │   │   │   ├── messenger_service.py
│   │   │   │   └── slack_service.py
│   │   │   │
│   │   │   ├── content_platforms/              # Content platform services
│   │   │   │   ├── wordpress_service.py
│   │   │   │   ├── medium_service.py
│   │   │   │   ├── substack_service.py
│   │   │   │   ├── ghost_service.py
│   │   │   │   └── blogger_service.py
│   │   │   │
│   │   │   ├── qna_platforms/                  # Q&A platform services
│   │   │   │   ├── quora_service.py
│   │   │   │   ├── reddit_service.py
│   │   │   │   ├── stackoverflow_service.py
│   │   │   │   └── discord_service.py
│   │   │   │
│   │   │   ├── automation/                     # Automation services
│   │   │   │   ├── workflow_service.py
│   │   │   │   ├── scheduler_service.py
│   │   │   │   ├── rule_engine.py
│   │   │   │   └── velocity_service.py
│   │   │   │
│   │   │   ├── analytics/                      # Analytics services
│   │   │   │   ├── analytics_service.py
│   │   │   │   ├── engagement_tracker.py
│   │   │   │   ├── growth_analyzer.py
│   │   │   │   └── report_generator.py
│   │   │   │
│   │   │   └── billing/                        # Billing services
│   │   │       ├── subscription_service.py
│   │   │       ├── payment_service.py
│   │   │       ├── usage_tracker.py
│   │   │       └── invoice_service.py
│   │   │
│   │   ├── ai/                                 # AI Services
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── content_generators/             # AI content generation
│   │   │   │   ├── mistral_generator.py        # 🔥 NEW: Mistral AI integration
│   │   │   │   ├── groq_generator.py           # 🔥 NEW: Groq AI integration
│   │   │   │   ├── openai_generator.py         # OpenAI integration
│   │   │   │   └── base_generator.py           # Base generator class
│   │   │   │
│   │   │   ├── domain_specialists/             # Domain-specific AI
│   │   │   │   ├── memes_specialist.py
│   │   │   │   ├── tech_news_specialist.py
│   │   │   │   ├── coding_tips_specialist.py
│   │   │   │   ├── lifestyle_specialist.py
│   │   │   │   ├── business_specialist.py
│   │   │   │   ├── finance_specialist.py
│   │   │   │   ├── travel_specialist.py
│   │   │   │   └── food_specialist.py
│   │   │   │
│   │   │   ├── platform_optimizers/            # Platform-specific optimization
│   │   │   │   ├── instagram_optimizer.py
│   │   │   │   ├── facebook_optimizer.py
│   │   │   │   ├── youtube_optimizer.py
│   │   │   │   ├── twitter_optimizer.py
│   │   │   │   ├── linkedin_optimizer.py
│   │   │   │   ├── tiktok_optimizer.py
│   │   │   │   └── pinterest_optimizer.py
│   │   │   │
│   │   │   ├── image_generators/               # Image generation
│   │   │   │   ├── meme_image_generator.py
│   │   │   │   ├── quote_image_generator.py
│   │   │   │   ├── news_image_finder.py
│   │   │   │   └── dalle_generator.py
│   │   │   │
│   │   │   ├── sentiment_analysis/             # Sentiment analysis
│   │   │   │   ├── review_analyzer.py
│   │   │   │   ├── comment_analyzer.py
│   │   │   │   └── brand_monitor.py
│   │   │   │
│   │   │   ├── voice_analysis/                 # Voice analysis
│   │   │   │   ├── brand_voice_analyzer.py
│   │   │   │   └── tone_matcher.py
│   │   │   │
│   │   │   └── file_processors/                # 🔥 NEW: File processing
│   │   │       ├── pdf_processor.py            # PDF text extraction
│   │   │       ├── docx_processor.py           # Word document processing
│   │   │       ├── pptx_processor.py           # PowerPoint processing
│   │   │       ├── image_processor.py          # Image OCR
│   │   │       ├── text_processor.py           # Text analysis
│   │   │       └── document_analyzer.py        # Context extraction
│   │   │
│   │   ├── automation/                         # Automation Engine
│   │   │   ├── __init__.py
│   │   │   │
│   │   │   ├── platforms/                      # Platform automation
│   │   │   │   ├── youtube_automator.py
│   │   │   │   ├── facebook_automator.py
│   │   │   │   ├── instagram_automator.py
│   │   │   │   ├── twitter_automator.py
│   │   │   │   ├── linkedin_automator.py
│   │   │   │   ├── tiktok_automator.py
│   │   │   │   └── pinterest_automator.py
│   │   │   │
│   │   │   ├── browsers/                       # Browser automation
│   │   │   │   ├── selenium_driver.py
│   │   │   │   ├── playwright_driver.py
│   │   │   │   └── base_browser.py
│   │   │   │
│   │   │   ├── schedulers/                     # Scheduling systems
│   │   │   │   ├── post_scheduler.py
│   │   │   │   ├── content_scheduler.py
│   │   │   │   ├── analytics_scheduler.py
│   │   │   │   └── velocity_scheduler.py
│   │   │   │
│   │   │   └── workflows/                      # Workflow automation
│   │   │       ├── content_workflow.py
│   │   │       ├── engagement_workflow.py
│   │   │       └── review_workflow.py
│   │   │
│   │   ├── workers/                            # Background workers (Celery)
│   │   │   ├── __init__.py
│   │   │   ├── content_generation_worker.py    # AI content generation
│   │   │   ├── auto_posting_worker.py          # Auto-posting tasks
│   │   │   ├── analytics_collection_worker.py  # Analytics data collection
│   │   │   ├── credential_verification_worker.py # OAuth verification
│   │   │   ├── review_monitoring_worker.py     # Review monitoring
│   │   │   ├── message_processing_worker.py    # Message processing
│   │   │   ├── velocity_optimization_worker.py # Performance optimization
│   │   │   └── file_processing_worker.py       # 🔥 NEW: File processing
│   │   │
│   │   └── utils/                              # Utility functions
│   │       ├── __init__.py
│   │       ├── encryption.py                   # Data encryption
│   │       ├── validators.py                   # Input validation
│   │       ├── rate_limiter.py                 # Rate limiting
│   │       ├── error_handlers.py               # Error handling
│   │       ├── logger.py                       # Logging utilities
│   │       ├── helpers.py                      # General helpers
│   │       ├── auth_helpers.py                 # Auth utilities
│   │       ├── formatters.py                   # Data formatters
│   │       ├── date_utils.py                   # Date utilities
│   │       ├── email_utils.py                  # Email utilities
│   │       ├── image_utils.py                  # Image utilities
│   │       └── file_utils.py                   # 🔥 NEW: File utilities
│   │
│   ├── storage/                                # File storage
│   │   ├── generated_content/                  # AI-generated content
│   │   ├── images/                             # Image files
│   │   ├── videos/                             # Video files
│   │   ├── templates/                          # Content templates
│   │   ├── exports/                            # Exported data
│   │   ├── temp/                               # Temporary files
│   │   └── uploads/                            # 🔥 NEW: User uploads
│   │       ├── documents/                      # PDF, DOCX, PPTX files
│   │       ├── images/                         # Image uploads
│   │       └── processed/                      # Processed files
│   │
│   └── tests/                                  # Test suite
│       ├── __init__.py
│       ├── conftest.py                         # Test configuration
│       │
│       ├── unit/                               # Unit tests
│       │   ├── test_auth.py
│       │   ├── test_platforms.py
│       │   ├── test_automation.py
│       │   ├── test_workers.py
│       │   ├── test_ai_services.py
│       │   └── test_file_processors.py         # 🔥 NEW: File processing tests
│       │
│       ├── integration/                        # Integration tests
│       │   ├── test_api_endpoints.py
│       │   ├── test_platform_integrations.py
│       │   ├── test_automation_workflows.py
│       │   └── test_oauth_flows.py             # 🔥 NEW: OAuth integration tests
│       │
│       └── fixtures/                           # Test fixtures
│           ├── user_fixtures.py
│           ├── platform_fixtures.py
│           ├── content_fixtures.py
│           └── file_fixtures.py                # 🔥 NEW: File test fixtures
│
├── shared/                                     # Shared utilities
│   ├── schemas/                                # Data schemas
│   │   ├── user_schema.py
│   │   ├── platform_schema.py
│   │   ├── content_schema.py
│   │   ├── automation_schema.py
│   │   └── analytics_schema.py
│   │
│   ├── constants/                              # Application constants
│   │   ├── platforms.py
│   │   ├── content_types.py
│   │   ├── error_codes.py
│   │   └── ai_prompts.py
│   │
│   ├── utils/                                  # Shared utilities
│   │   ├── encryption.py
│   │   ├── validators.py
│   │   └── formatters.py
│   │
│   └── types/                                  # Type definitions
│       ├── platform_types.py
│       └── content_types.py
│
├── automation/                                 # Browser automation scripts
│   ├── playwright_scripts/                     # Playwright automation
│   │   ├── tiktok_poster.py
│   │   ├── pinterest_automation.py
│   │   ├── instagram_story_poster.py
│   │   ├── linkedin_automation.py
│   │   └── reddit_automation.py
│   │
│   ├── selenium_scripts/                       # Selenium automation
│   │   ├── facebook_groups.py
│   │   ├── youtube_automation.py
│   │   └── twitter_automation.py
│   │
│   ├── browser_profiles/                       # Browser profiles
│   └── extensions/                             # Browser extensions
│
├── docs/                                       # Documentation
│   ├── README.md
│   ├── CONTRIBUTING.md
│   ├── CHANGELOG.md
│   │
│   ├── api/                                    # API documentation
│   │   ├── authentication.md
│   │   ├── platforms.md
│   │   ├── automation.md
│   │   ├── content.md
│   │   ├── analytics.md
│   │   ├── oauth.md                            # 🔥 NEW: OAuth documentation
│   │   └── webhooks.md
│   │
│   ├── setup/                                  # Setup guides
│   │   ├── installation.md
│   │   ├── platform_setup.md
│   │   ├── environment_setup.md
│   │   ├── database_setup.md
│   │   └── api_keys_setup.md                   # 🔥 NEW: API keys setup guide
│   │
│   ├── architecture/                           # Architecture documentation
│   │   ├── overview.md
│   │   ├── database_design.md
│   │   ├── api_design.md
│   │   ├── security.md
│   │   ├── scaling.md
│   │   └── ai_integration.md                   # 🔥 NEW: AI integration guide
│   │
│   ├── user_guides/                            # User guides
│   │   ├── getting_started.md
│   │   ├── platform_connection.md
│   │   ├── automation_setup.md
│   │   ├── content_creation.md
│   │   ├── analytics.md
│   │   ├── file_upload_guide.md                # 🔥 NEW: File upload guide
│   │   └── troubleshooting.md
│   │
│   ├── development/                            # Development guides
│   │   ├── contributing.md
│   │   ├── coding_standards.md
│   │   ├── testing.md
│   │   └── debugging.md
│   │
│   └── deployment/                             # Deployment guides
│       ├── docker.md
│       ├── aws.md
│       ├── monitoring.md
│       └── production_checklist.md             # 🔥 NEW: Production checklist
│
├── scripts/                                    # Utility scripts
│   ├── deployment/                             # Deployment scripts
│   │   ├── deploy.sh
│   │   ├── rollback.sh
│   │   └── health_check.sh
│   │
│   ├── database/                               # Database scripts
│   │   ├── migrations/
│   │   ├── seed_data.py
│   │   ├── backup.sh
│   │   └── restore.sh
│   │
│   ├── setup/                                  # Setup scripts
│   │   ├── install_dependencies.sh
│   │   ├── setup_environment.py
│   │   └── create_admin.py
│   │
│   └── maintenance/                            # Maintenance scripts
│       ├── cleanup_temp_files.py
│       ├── update_analytics.py
│       └── optimize_database.py
│
├── config/                                     # Configuration files
│   ├── production.py                           # Production config
│   ├── development.py                          # Development config
│   ├── testing.py                              # Testing config
│   ├── docker-compose.yml                      # Docker configuration
│   ├── nginx.conf                              # Nginx configuration
│   ├── celery.conf                             # Celery configuration
│   └── redis.conf                              # Redis configuration
│
└── deployment/                                 # Deployment files
    ├── Dockerfile.backend                      # Backend Docker file
    ├── Dockerfile.frontend                     # Frontend Docker file
    ├── docker-compose.production.yml           # Production Docker compose
    ├── kubernetes/                             # Kubernetes manifests
    │   ├── namespace.yaml
    │   ├── deployment.yaml
    │   ├── service.yaml
    │   └── ingress.yaml
    │
    ├── terraform/                              # Infrastructure as code
    │   ├── main.tf
    │   ├── variables.tf
    │   └── outputs.tf
    │
    └── ansible/                                # Configuration management
        ├── playbook.yml
        ├── inventory/
        └── roles/
```

## Key Features Implementation

### 🔥 NEW Auto-Posting Features

1. **OAuth 2.0 Integration**
   - Secure social media connections without password storage
   - Platform-specific authentication flows
   - Automatic token refresh and management

2. **AI Content Generation**
   - Multi-format file upload support (PDF, DOCX, PPTX, images)
   - Context-aware content generation using Mistral AI + Groq
   - Platform-specific content optimization
   - Performance prediction and hashtag generation

3. **Smart Scheduling System**
   - AI-optimized posting times
   - Platform-specific frequency controls
   - Content distribution management
   - Timezone-aware scheduling

4. **File Processing Pipeline**
   - PDF text extraction using PyPDF2
   - Word document processing with python-docx
   - PowerPoint handling with python-pptx
   - Image OCR with pytesseract
   - Context analysis and understanding

### Subscription Tiers

1. **Free Tier**
   - 2 social media platforms
   - 2 posts per day maximum
   - Basic AI content generation
   - Standard analytics

2. **Pro Tier ($29/month)**
   - 5 social media platforms
   - 10 posts per day
   - Advanced AI content generation
   - File upload and processing
   - Advanced analytics

3. **Agency Tier ($99/month)**
   - Unlimited platforms
   - Unlimited posts
   - White-label options
   - Team collaboration
   - API access

### Supported Platforms

**Social Media Platforms:**
- Facebook (OAuth + Graph API)
- Instagram (OAuth + Graph API)
- Twitter (OAuth 2.0 + API v2)
- LinkedIn (OAuth + API v2)
- YouTube (Google OAuth + Data API)
- TikTok (Business API - Limited)
- Pinterest (OAuth + API)
- Reddit (OAuth + API)

**Messaging Platforms:**
- WhatsApp Business API
- Telegram Bot API
- Email (SMTP)
- SMS (Twilio)
- Slack (OAuth + API)

**Review Platforms:**
- Google My Business
- Yelp
- Trustpilot
- TripAdvisor
- App Store Connect

**E-commerce Platforms:**
- Shopify
- WooCommerce
- Amazon Seller Central
- Etsy
- eBay

### Technology Stack

**Frontend:**
- React 18 with Vite
- TailwindCSS for styling
- React Query for state management
- Axios for API calls
- React Router for routing

**Backend:**
- Python Flask
- MongoDB with PyMongo
- Celery for background tasks
- Redis for caching and queues
- JWT for authentication

**AI Services:**
- Mistral AI (Primary)
- Groq (Fallback)
- OpenAI (Additional features)

**File Processing:**
- PyPDF2 for PDF processing
- python-docx for Word documents
- python-pptx for PowerPoint
- Pillow + pytesseract for image OCR

**Deployment:**
- Docker containerization
- Nginx reverse proxy
- MongoDB Atlas
- Redis Cloud
- Railway/Vercel for hosting

This structure provides a comprehensive foundation for building a production-ready AI social media automation platform that can compete with existing solutions like Buffer and Hootsuite while offering unique AI-powered features.





# Platform API Setup Guide - VelocityPost.ai

This guide provides step-by-step instructions for obtaining API credentials from all supported social media platforms.

## Overview of Required APIs

| Platform | API Cost | Approval Time | Difficulty | Business Required |
|----------|----------|---------------|------------|------------------|
| Facebook/Instagram | Free + Usage | 2-14 days | ⭐⭐⭐ | Yes |
| Twitter | $100/month | 1-3 days | ⭐⭐ | No |
| LinkedIn | Free | 7-21 days | ⭐⭐⭐⭐ | Yes |
| YouTube | Free + Quotas | 1-7 days | ⭐⭐ | No |
| Pinterest | Free | 1-7 days | ⭐⭐ | No |
| TikTok | Enterprise Only | 30-90 days | ⭐⭐⭐⭐⭐ | Yes |

## 1. Facebook & Instagram Business API

### Prerequisites
- Facebook Business Account
- Facebook Developer Account
- Legitimate Business Entity
- Business Website with Privacy Policy
- Business Email Address

### Step-by-Step Setup

#### 1.1 Create Developer Account
1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Click "Get Started" → Use Facebook Account
3. Verify phone number & email
4. Accept Developer Terms

#### 1.2 Create App
1. Click "Create App" → "Business" → Continue
2. Fill App Details:
   - Display Name: "VelocityPost Social Manager"
   - Contact Email: your-business@domain.com
   - Business Account: Select your business

#### 1.3 Add Products
Required Products:
1. **Facebook Login** → Set Up
2. **Instagram Basic Display** → Set Up
3. **Instagram API** → Set Up (Requires Business Verification)
4. **Marketing API** → Set Up (For advanced features)

#### 1.4 Configure Settings
```javascript
// App Settings → Basic
App ID: 1234567890123456
App Secret: abcd1234567890efgh (Keep Secret!)

// Facebook Login Settings
Valid OAuth Redirect URIs:
- http://localhost:3000/auth/callback/facebook (Development)
- https://yourapp.com/auth/callback/facebook (Production)

// Instagram Settings
Valid OAuth Redirect URIs:
- http://localhost:3000/auth/callback/instagram
- https://yourapp.com/auth/callback/instagram

Client OAuth Settings:
- Web OAuth Login: YES
- Use Strict Mode: YES
```

#### 1.5 Get Permissions
**Basic Permissions (Auto-Approved):**
- email
- public_profile

**Advanced Permissions (Require Review):**
- pages_manage_posts (Post to Facebook Pages)
- pages_read_engagement (Read engagement data)
- instagram_basic (Instagram profile access)
- instagram_content_publish (Post to Instagram)
- business_management (Business account access)

#### 1.6 Business Verification
1. Go to Business Settings → Security Center
2. Upload business documents:
   - Business license
   - Tax registration
   - Articles of incorporation
3. Wait 2-4 weeks for verification

### Warning
- Instagram Business Requirements: Must have Instagram Business/Creator account
- Need Facebook Page connected to Instagram
- Personal Instagram accounts NOT supported

## 2. Twitter API v2

### Step-by-Step Setup

#### 2.1 Apply for Developer Account
1. Go to [developer.twitter.com](https://developer.twitter.com)
2. Click "Apply for a developer account"
3. Fill detailed application:

```
Use Case: Social Media Management Tool

Description: "Building an AI-powered social media automation platform 
that helps businesses create and schedule Twitter content. The app will:
- Generate content using AI
- Schedule tweets for optimal times
- Analyze tweet performance
- Manage multiple Twitter accounts for agencies"

Will you make Twitter content available to government entities? NO
Will your app use Tweet, Retweet, Like, Follow, or DM functionality? YES
```

#### 2.2 Create Project & App
```bash
# After approval (usually 24-48 hours)
1. Create New Project
   - Name: "VelocityPost Twitter Integration"
   - Use Case: "Making a bot"
   - Description: "Social media automation platform"

2. Create App
   - App Name: "VelocityPost"
   - Description: "AI-powered social media management"
```

#### 2.3 Configure OAuth 2.0
```javascript
// App Settings → User authentication settings
OAuth 2.0 Settings:
- OAuth 2.0: ON
- Type: Web App
- Callback URI: https://yourapp.com/auth/callback/twitter
- Website URL: https://yourapp.com
- Terms of Service: https://yourapp.com/terms
- Privacy Policy: https://yourapp.com/privacy

Client ID: VGhpc0lzQUNsaWVudElE
Client Secret: VGhpc0lzQVNlY3JldEtleQ (Keep Secret!)
```

#### 2.4 Get API Keys
```javascript
// Keys and Tokens
API Key: abc123def456ghi789
API Secret: xyz987uvw654rst321
Bearer Token: AAAAAAAAAAAAAAAAAAAAAAAAA...

// For OAuth 2.0 (Recommended)
Client ID: VGhpc0lzQUNsaWVudElE
Client Secret: VGhpc0lzQVNlY3JldEtleQ
```

### Twitter API Pricing (2024)
- **Free Tier**: 1,500 tweets/month, 50,000 reads/month
- **Basic ($100/month)**: 50,000 tweets/month, 2M reads/month
- **Pro ($5,000/month)**: 300,000 tweets/month, 10M reads/month

### Warning
- Free tier is very limited (1,500 tweets/month only)
- Pricing jumps to $100/month for real usage
- Suspended accounts lose all data

## 3. LinkedIn API

### Prerequisites
- LinkedIn Company Page (Must create first!)
- Business Email
- Verified LinkedIn Profile
- Company Logo (square format)

### Step-by-Step Setup

#### 3.1 Create LinkedIn App
1. Go to [developer.linkedin.com](https://developer.linkedin.com)
2. Click "Create App" → Sign in with LinkedIn

#### 3.2 App Configuration
```javascript
App Details:
- App Name: "VelocityPost"
- LinkedIn Page: Your Company Page
- Privacy Policy URL: https://yourapp.com/privacy
- App Logo: Upload square logo (400x400px min)
- Legal Agreement: Accept LinkedIn API Terms

OAuth 2.0 Settings:
Redirect URLs:
- http://localhost:3000/auth/callback/linkedin (Dev)
- https://yourapp.com/auth/callback/linkedin (Prod)
```

#### 3.3 Request Products
**Available Products:**
1. **Sign In with LinkedIn** (Auto-approved)
2. **Share on LinkedIn** (Requires Review - 7-14 days)
3. **Marketing Developer Platform** (Enterprise only)

**Required Permissions:**
- r_liteprofile (Basic profile)
- r_emailaddress (Email address)
- w_member_social (Post updates)

#### 3.4 Get Credentials
```javascript
// Auth Tab
Client ID: 78xyz123abc
Client Secret: ABCD1234567890 (Keep Secret!)
```

### Warning
- Requires existing Company Page
- Review process takes 1-3 weeks
- Very strict content policies
- Limited to professional content only

## 4. YouTube Data API

### Step-by-Step Setup

#### 4.1 Google Cloud Console Setup
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create New Project:
   - Project Name: "VelocityPost YouTube"
   - Organization: Your business

#### 4.2 Enable APIs
```bash
APIs & Services → Library → Search:
1. "YouTube Data API v3" → Enable
2. "YouTube Analytics API" → Enable (Optional)
3. "YouTube Reporting API" → Enable (Optional)
```

#### 4.3 Create Credentials
```javascript
// APIs & Services → Credentials → Create Credentials
OAuth 2.0 Client IDs:
- Application Type: Web Application
- Name: "VelocityPost OAuth"
- Authorized JavaScript Origins:
  - http://localhost:3000 (Development)
  - https://yourapp.com (Production)
- Authorized Redirect URIs:
  - http://localhost:3000/auth/callback/youtube
  - https://yourapp.com/auth/callback/youtube

Client ID: 123456789-abcdefg.apps.googleusercontent.com
Client Secret: GOCSPX-1234567890abcdef
```

#### 4.4 OAuth Consent Screen
```javascript
// OAuth Consent Screen Configuration
User Type: External
App Information:
- App Name: "VelocityPost"
- User Support Email: support@yourapp.com
- Developer Contact: dev@yourapp.com
- App Logo: Upload 1024x1024 PNG

Scopes:
- https://www.googleapis.com/auth/youtube
- https://www.googleapis.com/auth/youtube.upload
- https://www.googleapis.com/auth/youtube.readonly

Test Users (for development):
- Add your email and test accounts
```

#### 4.5 Quotas & Limits
**Default Quotas (Free):**
- 10,000 units per day
- 100 units per 100 seconds per user

**Unit Costs:**
- Video Upload: 1,600 units
- Video List: 1 unit
- Search: 100 units
- Comment Insert: 50 units

## 5. Pinterest API

### Step-by-Step Setup

#### 5.1 Create Pinterest App
1. Go to [developers.pinterest.com](https://developers.pinterest.com)
2. Click "Create App" → Business Account Required

#### 5.2 App Configuration
```javascript
App Details:
- App Name: "VelocityPost"
- Description: "Social media management platform"
- Website: https://yourapp.com
- Redirect URI: https://yourapp.com/auth/callback/pinterest
- Platform: Web

Terms and Guidelines:
- Accept Pinterest Developer Agreement
- Confirm GDPR compliance
- Agree to content policies
```

#### 5.3 Get API Credentials
```javascript
// App Settings
App ID: 1234567890123456
App Secret: abcd1234567890efgh1234567890ijkl

// API Features
Available Endpoints:
- User Profile
- Boards Management
- Pins Management
- Analytics (Business accounts only)
```

## 6. Payment Integration Setup

### Stripe Setup

#### 6.1 Create Stripe Account
1. Go to [stripe.com](https://stripe.com)
2. Sign up for business account
3. Complete business verification

#### 6.2 Get API Keys
```bash
# Test Mode (Development)
Publishable Key: pk_test_...
Secret Key: sk_test_... (Keep Secret!)

# Live Mode (Production)
Publishable Key: pk_live_...
Secret Key: sk_live_... (Keep Secret!)
```

#### 6.3 Configure Webhooks
```javascript
// Dashboard → Webhooks → Add endpoint
Endpoint URL: https://yourapp.com/api/webhooks/stripe
Events to send:
- payment_intent.succeeded
- payment_intent.payment_failed
- customer.subscription.created
- customer.subscription.updated
- customer.subscription.deleted
- invoice.payment_succeeded
- invoice.payment_failed
```

### Razorpay Setup (India/UPI)

#### 6.1 Create Razorpay Account
1. Go to [razorpay.com](https://razorpay.com)
2. Sign up with business details
3. Complete KYC verification

#### 6.2 Get API Keys
```bash
# Test Mode
Key ID: rzp_test_...
Key Secret: ... (Keep Secret!)

# Live Mode
Key ID: rzp_live_...
Key Secret: ... (Keep Secret!)
```

#### 6.3 Configure Webhooks
```javascript
// Dashboard → Webhooks → Add Webhook
Webhook URL: https://yourapp.com/api/webhooks/razorpay
Events:
- payment.authorized
- payment.failed
- payment.captured
- subscription.authenticated
- subscription.cancelled
```

## Environment Variables Template

Create a `.env` file with these variables:

```env
# Flask Configuration
SECRET_KEY=your-super-secret-key-32-chars-min
JWT_SECRET_KEY=your-jwt-secret-key-32-chars-min
FLASK_ENV=development
DEBUG=True
PORT=5000

# Database
MONGODB_URI=mongodb://localhost:27017/velocitypost
REDIS_URL=redis://localhost:6379

# Facebook/Instagram
FACEBOOK_APP_ID=your_facebook_app_id
FACEBOOK_APP_SECRET=your_facebook_app_secret
FACEBOOK_REDIRECT_URI=http://localhost:3000/auth/callback/facebook

# Twitter
TWITTER_CLIENT_ID=your_twitter_client_id
TWITTER_CLIENT_SECRET=your_twitter_client_secret
TWITTER_REDIRECT_URI=http://localhost:3000/auth/callback/twitter

# LinkedIn
LINKEDIN_CLIENT_ID=your_linkedin_client_id
LINKEDIN_CLIENT_SECRET=your_linkedin_client_secret
LINKEDIN_REDIRECT_URI=http://localhost:3000/auth/callback/linkedin

# YouTube (Google)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:3000/auth/callback/youtube

# Pinterest
PINTEREST_CLIENT_ID=your_pinterest_client_id
PINTEREST_CLIENT_SECRET=your_pinterest_client_secret
PINTEREST_REDIRECT_URI=http://localhost:3000/auth/callback/pinterest

# AI Services
MISTRAL_API_KEY=your_mistral_api_key
GROQ_API_KEY=your_groq_api_key
OPENAI_API_KEY=your_openai_api_key

# Payment Processing
STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_publishable_key
STRIPE_SECRET_KEY=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

RAZORPAY_KEY_ID=rzp_test_your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret

# File Upload
MAX_FILE_SIZE=50MB
ALLOWED_EXTENSIONS=pdf,docx,pptx,txt,jpg,png,jpeg
UPLOAD_FOLDER=storage/uploads

# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## Security Best Practices

1. **API Key Security**
   - Never commit API keys to version control
   - Use environment variables for all sensitive data
   - Rotate API keys regularly (every 90 days)
   - Use separate keys for development and production

2. **OAuth Security**
   - Always use HTTPS in production
   - Implement state parameter for CSRF protection
   - Validate redirect URIs strictly
   - Store access tokens encrypted in database

3. **Rate Limiting**
   - Implement rate limiting on all API endpoints
   - Respect platform rate limits strictly
   - Use exponential backoff for failed requests
   - Monitor API usage regularly

4. **Data Protection**
   - Encrypt all user data at rest
   - Use TLS for all API communications
   - Implement proper session management
   - Regular security audits

## Implementation Priority

### Phase 1: MVP (Start Here)
1. **Twitter API** ✅
   - Easiest approval process
   - Good for testing automation
   - Pay $100/month for real usage

2. **YouTube API** ✅
   - Free Google integration
   - Good quotas for starting
   - Straightforward setup

3. **Pinterest API** ✅
   - Simple approval process
   - Good for content testing
   - Free tier sufficient

### Phase 2: Growth
4. **Facebook/Instagram API** ⚠️
   - Most valuable users
   - Complex setup process
   - Requires business verification
   - 2-4 week approval time

5. **LinkedIn API** ⚠️
   - High-value B2B users
   - Professional content focus
   - Requires company page
   - 1-3 week review

### Phase 3: Enterprise
6. **TikTok API** ❌
   - Skip for now
   - Extremely difficult approval
   - Focus on other platforms first
   - Revisit when you have significant traction

## Cost Breakdown (Monthly)

### Development Phase:
- Twitter API: $100/month
- Others: Free
- **Total: $100/month**

### Growth Phase (1000+ users):
- Twitter API: $100-500/month
- Facebook/Instagram: $0-200/month (usage-based)
- Google/YouTube: $0-100/month
- LinkedIn: Free
- Pinterest: Free
- **Total: $100-800/month**

### Scale Phase (10,000+ users):
- Twitter API: $5,000/month
- Facebook/Instagram: $500-2,000/month
- Google/YouTube: $200-1,000/month
- Others: Free
- **Total: $5,700-8,000/month**

## Common Issues and Solutions

### Facebook/Instagram Issues
- **Issue**: App rejected during review
- **Solution**: Ensure you have a legitimate business, proper privacy policy, and clear use case explanation

### Twitter Issues
- **Issue**: High API costs
- **Solution**: Start with free tier for testing, upgrade gradually as user base grows

### LinkedIn Issues
- **Issue**: Content restrictions
- **Solution**: Focus on professional content only, avoid promotional posts

### General OAuth Issues
- **Issue**: Token expiration
- **Solution**: Implement automatic token refresh with proper error handling

## Testing Your Integration

### 1. Development Testing
```bash
# Test OAuth flow
curl -X GET "https://api.twitter.com/2/users/me" \
     -H "Authorization: Bearer YOUR_BEARER_TOKEN"

# Test posting
curl -X POST "https://api.twitter.com/2/tweets" \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"text": "Test post from VelocityPost.ai"}'
```

### 2. Production Testing
- Start with small test audiences
- Monitor error rates and API responses
- Test all edge cases (expired tokens, rate limits, etc.)
- Implement comprehensive logging

## Compliance and Legal Requirements

### Required Legal Documents
- Privacy Policy (GDPR compliant)
- Terms of Service
- Data Processing Agreement
- Cookie Policy
- Business License
- Developer Agreements (all platforms)

### Platform-Specific Compliance
- **Facebook**: Business verification required
- **Twitter**: Bot policy compliance
- **LinkedIn**: Professional use only
- **YouTube**: Content policy adherence
- **Pinterest**: Community guidelines

## Next Steps

1. **Week 1-2**: Set up development environment and basic OAuth flows
2. **Week 3-4**: Apply for platform APIs (starting with Twitter and YouTube)
3. **Week 5-6**: Implement basic posting functionality
4. **Week 7-8**: Add business verification and advanced features

## Support Resources

- **Facebook Developers**: [developers.facebook.com/support](https://developers.facebook.com/support)
- **Twitter Developer Support**: [twittercommunity.com](https://twittercommunity.com)
- **LinkedIn Developer Support**: [linkedin.com/help/linkedin/answer/46](https://linkedin.com/help/linkedin/answer/46)
- **YouTube API Support**: [developers.google.com/youtube/v3/support](https://developers.google.com/youtube/v3/support)
- **Pinterest Developer Support**: [help.pinterest.com/en/developers](https://help.pinterest.com/en/developers)

This guide provides the foundation for integrating with all major social media platforms. Follow the priority order and budget accordingly for API costs as your platform scales.







# VelocityPost.ai - Complete User Workflow Guide

This document outlines the complete user journey and workflow for VelocityPost.ai, from landing page to full automation setup.

## User Journey Overview

```
Landing Page → Registration → Platform Connection → Content Domain Selection → 
AI Content Generation → Auto-Posting Setup → Analytics & Monitoring
```

## Detailed User Workflow

### Phase 1: Discovery & Registration

#### 1.1 Landing Page Experience (`/`)
**File**: `frontend/src/pages/public/LandingPage.jsx`

**User Actions:**
- Views hero section with value proposition
- Explores platform integrations showcase
- Reviews pricing plans (Free, Pro, Agency)
- Clicks "Start Free Trial" or "Get Started"

**Key Elements:**
- Hero: "Generate 30 days of content in 30 seconds"
- Platform logos: Facebook, Instagram, Twitter, LinkedIn, YouTube, etc.
- Pricing comparison with Buffer/Hootsuite
- Social proof testimonials

**Next Action**: Redirect to `/register`

#### 1.2 User Registration (`/register`)
**File**: `frontend/src/pages/auth/Register.jsx`

**User Input:**
```javascript
{
  "name": "John Smith",
  "email": "john@example.com", 
  "password": "SecurePass123!",
  "plan_type": "free" // Selected during registration
}
```

**Validation Rules:**
- Name: 2+ characters
- Email: Valid format
- Password: 8+ chars, uppercase, lowercase, number, special character
- Terms acceptance: Required

**Backend Process:**
1. Validate input data
2. Check email uniqueness
3. Hash password securely
4. Create user record in MongoDB
5. Generate JWT access token
6. Send welcome email

**Response:**
```json
{
  "success": true,
  "message": "Registration successful",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "user123",
    "name": "John Smith",
    "email": "john@example.com",
    "plan_type": "free"
  }
}
```

**Next Action**: Auto-redirect to `/onboarding/welcome`

### Phase 2: Onboarding Flow

#### 2.1 Welcome & Plan Confirmation (`/onboarding/welcome`)
**File**: `frontend/src/pages/onboarding/Welcome.jsx`

**User Actions:**
- Confirms selected plan
- Reviews plan limitations:
  - Free: 2 platforms, 2 posts/day
  - Pro: 5 platforms, 10 posts/day  
  - Agency: Unlimited platforms & posts

**Plan Limitations Enforcement:**
```javascript
const PLAN_LIMITS = {
  free: {
    max_platforms: 2,
    max_posts_per_day: 2,
    file_upload: false,
    advanced_ai: false
  },
  pro: {
    max_platforms: 5,
    max_posts_per_day: 10,
    file_upload: true,
    advanced_ai: true
  },
  agency: {
    max_platforms: -1, // Unlimited
    max_posts_per_day: -1, // Unlimited
    file_upload: true,
    advanced_ai: true,
    white_label: true
  }
}
```

**Next Action**: Click "Continue Setup" → `/onboarding/platform-connection`

#### 2.2 Platform Connection (`/onboarding/platform-connection`)
**File**: `frontend/src/pages/onboarding/PlatformConnection.jsx`

**Available Platforms Display:**
```javascript
const PLATFORMS = [
  {
    id: 'facebook',
    name: 'Facebook',
    icon: FacebookIcon,
    description: 'Post to pages and groups',
    oauth_url: '/api/oauth/auth-url/facebook',
    pro_required: false
  },
  {
    id: 'instagram', 
    name: 'Instagram',
    icon: InstagramIcon,
    description: 'Share photos and stories',
    oauth_url: '/api/oauth/auth-url/instagram',
    pro_required: false
  },
  {
    id: 'twitter',
    name: 'Twitter',
    icon: TwitterIcon, 
    description: 'Tweet and engage',
    oauth_url: '/api/oauth/auth-url/twitter',
    pro_required: false
  },
  {
    id: 'linkedin',
    name: 'LinkedIn',
    icon: LinkedInIcon,
    description: 'Professional networking',
    oauth_url: '/api/oauth/auth-url/linkedin', 
    pro_required: true // Requires Pro plan
  },
  {
    id: 'youtube',
    name: 'YouTube',
    icon: YouTubeIcon,
    description: 'Upload videos',
    oauth_url: '/api/oauth/auth-url/youtube',
    pro_required: true
  }
]
```

**Free Plan User Experience:**
1. Can select maximum 2 platforms
2. LinkedIn/YouTube show "Upgrade to Pro" badges
3. Facebook, Instagram, Twitter available for free users

**Platform Connection Flow:**
```javascript
// User clicks "Connect Facebook"
1. Frontend calls: GET /api/oauth/auth-url/facebook
2. Backend generates OAuth URL with state parameter
3. User redirected to Facebook OAuth page
4. User grants permissions
5. Facebook redirects to: /auth/callback/facebook?code=xxx&state=yyy
6. Backend exchanges code for access token
7. Backend stores encrypted token in database
8. Frontend shows "Connected" status with green checkmark
```

**Backend OAuth Storage:**
```javascript
// MongoDB Collection: social_accounts
{
  "_id": ObjectId("..."),
  "user_id": ObjectId("user123"),
  "platform": "facebook",
  "platform_user_id": "fb_user_456",
  "username": "john.smith",
  "access_token": "encrypted_token_data",
  "refresh_token": "encrypted_refresh_token", 
  "token_expires_at": ISODate("2025-09-26T10:00:00Z"),
  "permissions": ["pages_manage_posts", "pages_read_engagement"],
  "profile_data": {
    "name": "John Smith",
    "profile_picture": "https://...",
    "follower_count": 1250
  },
  "is_active": true,
  "connected_at": ISODate("2025-08-26T10:00:00Z")
}
```

**Next Action**: After connecting 1+ platforms → "Continue to Content Setup"

#### 2.3 Content Domain Selection (`/onboarding/domain-selection`) 
**File**: `frontend/src/pages/onboarding/DomainSelection.jsx`

**Available Content Domains:**
```javascript
const CONTENT_DOMAINS = {
  "memes": {
    id: "memes",
    name: "Memes & Humor", 
    description: "Funny content, trending memes, relatable posts",
    sample_content: "When you finally fix that bug... 😅 #coding #developer",
    audience: "General, millennials, Gen Z",
    engagement_rate: "High (8-12%)",
    pro_required: false
  },
  "tech": {
    id: "tech", 
    name: "Technology & Innovation",
    description: "Tech news, AI updates, programming tips",
    sample_content: "🚀 AI is revolutionizing web development. Here's how...",
    audience: "Developers, tech enthusiasts",
    engagement_rate: "Medium (4-8%)", 
    pro_required: false
  },
  "business": {
    id: "business",
    name: "Business & Entrepreneurship", 
    description: "Business tips, startup advice, leadership content",
    sample_content: "💼 5 proven strategies to scale your startup in 2025",
    audience: "Entrepreneurs, professionals",
    engagement_rate: "Medium (3-6%)",
    pro_required: true // Requires Pro plan
  },
  "lifestyle": {
    id: "lifestyle",
    name: "Lifestyle & Wellness",
    description: "Health tips, personal development, life advice", 
    sample_content: "✨ Morning routine that changed my productivity...",
    audience: "General audience, wellness enthusiasts",
    engagement_rate: "High (6-10%)",
    pro_required: true
  },
  "finance": {
    id: "finance",
    name: "Personal Finance",
    description: "Money tips, investment advice, financial education",
    sample_content: "💰 Simple investment strategy for beginners...",
    audience: "Young professionals, investors", 
    engagement_rate: "Medium (4-7%)",
    pro_required: true
  }
}
```

**Free Plan Limitations:**
- Can select maximum 2 domains
- Only "memes" and "tech" available for free users
- Other domains require Pro upgrade

**User Selection Process:**
1. User sees domain cards with samples
2. Clicks "Preview Content" to see generated examples
3. Selects 1-2 domains (based on plan)
4. Configures posting settings:
   - Posts per day: 1-2 (free) or 1-10 (pro)
   - Posting times: Morning/Afternoon/Evening
   - Content style: Casual/Professional/Funny

**Next Action**: Click "Save & Continue" → `/onboarding/automation-setup`

#### 2.4 Automation Setup (`/onboarding/automation-setup`)
**File**: `frontend/src/pages/onboarding/AutomationSetup.jsx`

**Automation Configuration:**
```javascript
const automationConfig = {
  enabled: false, // User choice to enable
  schedule: {
    timezone: "America/New_York", // Auto-detected
    active_hours: {
      start: "09:00",
      end: "18:00" 
    },
    posting_frequency: {
      posts_per_day: 2, // Based on plan limits
      interval_hours: 12 // Calculated automatically
    },
    optimal_times: [ // AI-suggested times
      "10:00", "15:00", "19:00"
    ]
  },
  content_distribution: {
    "memes": 60, // 60% memes
    "tech": 40   // 40% tech content
  },
  platform_priorities: {
    "facebook": 1,
    "instagram": 2
  }
}
```

**User Decisions:**
1. **Enable Automation**: Yes/No toggle
2. **Posting Schedule**: Select optimal times
3. **Content Mix**: Percentage per domain
4. **Safety Settings**: 
   - Auto-post immediately: Yes/No
   - Review before posting: Yes/No

**Next Action**: Click "Complete Setup" → `/dashboard`

### Phase 3: Daily Usage & Content Management

#### 3.1 Dashboard Overview (`/dashboard`)
**File**: `frontend/src/pages/dashboard/Dashboard.jsx`

**Dashboard Components:**
```javascript
// Key Metrics Cards
const metrics = {
  total_posts: 45,
  engagement_rate: "8.2%",
  follower_growth: "+127 this week",
  next_post: "in 2 hours",
  automation_status: "active" // active/paused/stopped
}

// Recent Activity Feed
const recentActivity = [
  {
    type: "post_published", 
    platform: "instagram",
    content: "🚀 AI is changing everything...",
    engagement: { likes: 23, comments: 5 },
    time: "2 hours ago"
  },
  {
    type: "content_generated",
    domain: "tech", 
    count: 5,
    time: "4 hours ago"
  }
]
```

**Quick Actions Available:**
- Generate new content batch
- Pause/Resume automation
- Connect additional platform
- View detailed analytics
- Adjust posting schedule

#### 3.2 Content Generation Flow (`/content-generator`)
**File**: `frontend/src/pages/autoposting/ContentGenerator.jsx`

**Manual Content Generation:**
1. **Domain Selection**: Choose from connected domains
2. **Platform Selection**: Choose target platforms
3. **Prompt Input**: Custom prompt or use suggestions
4. **File Upload** (Pro only): Upload PDF/DOCX/PPTX for context
5. **Generate**: AI creates optimized content

**Generation Request:**
```javascript
// Frontend API Call
POST /api/ai/generate-content
{
  "domain": "tech",
  "platforms": ["instagram", "twitter"],
  "custom_prompt": "Create a post about AI automation in 2025",
  "creativity_level": 80,
  "include_hashtags": true,
  "include_emojis": true,
  "uploaded_file_id": "file123" // Optional
}
```

**AI Processing Pipeline:**
1. **Context Analysis**: If file uploaded, extract key points
2. **Domain Specialization**: Apply domain-specific knowledge
3. **Platform Optimization**: Adapt content length and format
4. **Performance Prediction**: Score content 1-100
5. **Response Generation**:

```json
{
  "success": true,
  "generated_content": {
    "instagram": {
      "content": "🚀 AI Automation is reshaping 2025! From smart workflows to predictive analytics, businesses are scaling faster than ever. What's your favorite AI tool? #AI #Automation #Tech2025 #Innovation",
      "performance_prediction": {
        "score": 87,
        "expected_likes": 245,
        "expected_comments": 18
      }
    },
    "twitter": {
      "content": "AI automation in 2025: \n• Smart workflows ✅\n• Predictive analytics 📊\n• Faster scaling 🚀\n\nWhat's your go-to AI tool? #AI #Automation", 
      "performance_prediction": {
        "score": 82,
        "expected_likes": 89,
        "expected_retweets": 23
      }
    }
  }
}
```

**Content Management Actions:**
- **Edit**: Modify generated content
- **Schedule**: Set specific posting time
- **Post Now**: Immediate publishing
- **Save to Library**: Store for later use
- **Generate Variations**: Create alternative versions

#### 3.3 File Upload & Processing (`/content-generator`)
**File**: `frontend/src/components/content/FileUpload.jsx`

**Supported File Types:**
```javascript
const SUPPORTED_FILES = {
  "application/pdf": {
    extension: ".pdf",
    max_size: "10MB", 
    processor: "pdf_processor"
  },
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document": {
    extension: ".docx",
    max_size: "5MB",
    processor: "docx_processor" 
  },
  "application/vnd.openxmlformats-officedocument.presentationml.presentation": {
    extension: ".pptx", 
    max_size: "20MB",
    processor: "pptx_processor"
  },
  "image/jpeg": {
    extension: ".jpg",
    max_size: "5MB",
    processor: "image_ocr_processor"
  }
}
```

**File Processing Pipeline:**
```python
# backend/app/services/file_processor.py

class FileProcessor:
    def process_file(self, file_path, file_type):
        if file_type == "application/pdf":
            return self.extract_pdf_content(file_path)
        elif file_type.startswith("application/vnd.openxml"):
            return self.extract_docx_content(file_path)  
        elif file_type.startswith("image/"):
            return self.extract_image_text(file_path)
            
    def extract_pdf_content(self, pdf_path):
        # Uses PyPDF2 to extract text
        # Analyzes document structure
        # Identifies key topics and themes
        return {
            "text_content": "extracted text...",
            "key_topics": ["AI", "automation", "business"],
            "document_type": "business_report",
            "summary": "Document discusses AI automation trends..."
        }
```

**Content Generation with Context:**
```python
# AI prompt with file context
prompt = f"""
Based on the uploaded document about {file_context['key_topics']}, 
create engaging social media content for {platform}.

Document Summary: {file_context['summary']}
Key Points: {file_context['key_topics']}
Target Audience: {domain_config['audience']}
Platform: {platform} (max {platform_config['max_length']} chars)
Tone: {domain_config['tone']}

Generate content that:
1. Incorporates key insights from the document
2. Is optimized for {platform} engagement
3. Includes relevant hashtags
4. Maintains {tone} voice
"""
```

### Phase 4: Automation & Monitoring

#### 4.1 Auto-Posting System (`/auto-posting`)
**File**: `frontend/src/pages/autoposting/AutoPostingCenter.jsx`

**Automation Status Dashboard:**
```javascript
const automationStatus = {
  is_active: true,
  posts_today: 3,
  posts_remaining: 2, // Based on plan limits
  next_post_in: "2 hours 15 minutes",
  platforms_active: ["instagram", "facebook"],
  content_queue: 12, // Generated content ready to post
  performance_today: {
    total_engagement: 156,
    avg_engagement_rate: "7.8%"
  }
}
```

**Control Actions:**
- **Start Automation**: Begin scheduled posting
- **Pause**: Temporarily stop (keeps content in queue)
- **Stop**: Halt automation and clear queue
- **Emergency Stop**: Immediate halt with notifications

**Background Automation Process:**
```python
# backend/app/workers/auto_posting_worker.py

@celery.task
def process_scheduled_posts():
    # Runs every minute via cron
    current_time = datetime.utcnow()
    
    # Find posts scheduled for now
    scheduled_posts = get_posts_due_for_posting(current_time)
    
    for post in scheduled_posts:
        try:
            # Post to platform using stored OAuth tokens
            result = post_to_platform(
                user_id=post.user_id,
                platform=post.platform, 
                content=post.content,
                media_urls=post.media_urls
            )
            
            # Update post status and engagement tracking
            update_post_status(post.id, 'published', result)
            
        except Exception as e:
            # Handle errors, retry logic, user notifications
            handle_posting_error(post.id, e)
```

#### 4.2 Analytics & Performance (`/analytics`)
**File**: `frontend/src/pages/analytics/Analytics.jsx`

**Analytics Dashboard:**
```javascript
const analyticsData = {
  overview: {
    total_posts: 156,
    total_engagement: 3247,
    follower_growth: 412,
    engagement_rate: "6.8%"
  },
  platform_breakdown: {
    instagram: {
      posts: 78,
      avg_likes: 45,
      avg_comments: 8,
      engagement_rate: "8.2%"
    },
    facebook: {
      posts: 56, 
      avg_likes: 23,
      avg_comments: 12,
      engagement_rate: "5.4%"
    }
  },
  content_performance: {
    memes: {
      posts: 89,
      avg_engagement: 67,
      top_performing: "When you fix a bug... 😅"
    },
    tech: {
      posts: 67,
      avg_engagement: 43,
      top_performing: "AI automation trends 2025"
    }
  },
  optimal_times: {
    best_posting_times: ["10:00", "15:00", "19:00"],
    best_days: ["Monday", "Wednesday", "Friday"],
    audience_timezone: "America/New_York"
  }
}
```

**Performance Insights:**
- AI vs Manual content performance comparison
- Best performing content types
- Optimal posting times per platform
- Audience engagement patterns
- Growth trajectory predictions

### Phase 5: Billing & Plan Management

#### 5.1 Subscription Management (`/billing`)
**File**: `frontend/src/pages/billing/BillingDashboard.jsx`

**Plan Usage Tracking:**
```javascript
const usageStats = {
  current_plan: "free",
  billing_cycle: "monthly",
  usage: {
    platforms_connected: 2,
    platforms_limit: 2,
    posts_today: 1,
    posts_limit: 2,
    posts_this_month: 45,
    file_uploads_used: 0, // Not available on free
    file_uploads_limit: 0
  },
  next_billing_date: "2025-09-26",
  upgrade_recommendations: [
    "Connect LinkedIn for professional content",
    "Upload documents for context-aware content",
    "Increase daily posting limit to 10"
  ]
}
```

**Upgrade Flow:**
1. User clicks "Upgrade to Pro" 
2. Stripe/Razorpay payment modal opens
3. Payment processing with webhook confirmation
4. Plan limits updated immediately
5. User gains access to pro features

**Payment Integration:**
```javascript
// Stripe Integration (International)
const stripe = await stripePromise;
const { error } = await stripe.redirectToCheckout({
  sessionId: checkout_session_id
});

// Razorpay Integration (India/UPI)
const options = {
  key: "rzp_live_...",
  amount: 2900, // ₹29.00
  currency: "INR",
  name: "VelocityPost.ai",
  description: "Pro Plan Subscription",
  handler: function(response) {
    // Handle successful payment
    verifyPayment(response.razorpay_payment_id);
  }
};
```

## Technical Implementation Summary

### Frontend Architecture
- **Framework**: React 18 with Vite
- **Styling**: TailwindCSS with custom design system
- **State Management**: React Query + Context API
- **Routing**: React Router with protected routes
- **HTTP Client**: Axios with interceptors

### Backend Architecture  
- **Framework**: Python Flask with Blueprint structure
- **Database**: MongoDB with PyMongo ODM
- **Authentication**: JWT with refresh tokens
- **Background Tasks**: Celery with Redis broker
- **File Processing**: PyPDF2, python-docx, pytesseract

### AI Integration
- **Primary**: Mistral AI API for content generation
- **Fallback**: Groq API for reliability
- **Enhancement**: OpenAI for specific features
- **Processing**: Domain-specific prompt engineering

### Security & Compliance
- **OAuth 2.0**: Secure social media authentication
- **Encryption**: AES-256 for sensitive data storage
- **HTTPS**: TLS 1.3 for all communications
- **GDPR**: Compliant data handling and privacy

This workflow guide provides a comprehensive overview of how users interact with VelocityPost.ai from discovery to full automation, ensuring a smooth and engaging user experience while maintaining technical excellence.














