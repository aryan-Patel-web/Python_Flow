# SMB Automation Hub - Complete Folder Structure Creator
# Run this script in PowerShell to create the entire project structure

# Create main project directory
New-Item -ItemType Directory -Path "smb-automation-hub" -Force
Set-Location "smb-automation-hub"

# Frontend Structure
Write-Host "Creating Frontend Structure..." -ForegroundColor Green

# Frontend root directories
New-Item -ItemType Directory -Path "frontend" -Force
New-Item -ItemType Directory -Path "frontend/public" -Force
New-Item -ItemType Directory -Path "frontend/src" -Force

# Frontend components
New-Item -ItemType Directory -Path "frontend/src/components" -Force
New-Item -ItemType Directory -Path "frontend/src/components/common" -Force
New-Item -ItemType Directory -Path "frontend/src/components/dashboard" -Force
New-Item -ItemType Directory -Path "frontend/src/components/platforms" -Force
New-Item -ItemType Directory -Path "frontend/src/components/automation" -Force
New-Item -ItemType Directory -Path "frontend/src/components/analytics" -Force

# Frontend pages
New-Item -ItemType Directory -Path "frontend/src/pages" -Force
New-Item -ItemType Directory -Path "frontend/src/pages/auth" -Force
New-Item -ItemType Directory -Path "frontend/src/pages/dashboard" -Force
New-Item -ItemType Directory -Path "frontend/src/pages/platforms" -Force
New-Item -ItemType Directory -Path "frontend/src/pages/automation" -Force
New-Item -ItemType Directory -Path "frontend/src/pages/content" -Force
New-Item -ItemType Directory -Path "frontend/src/pages/analytics" -Force
New-Item -ItemType Directory -Path "frontend/src/pages/settings" -Force

# Frontend other directories
New-Item -ItemType Directory -Path "frontend/src/hooks" -Force
New-Item -ItemType Directory -Path "frontend/src/context" -Force
New-Item -ItemType Directory -Path "frontend/src/services" -Force
New-Item -ItemType Directory -Path "frontend/src/utils" -Force
New-Item -ItemType Directory -Path "frontend/src/styles" -Force

# Create Frontend Files
Write-Host "Creating Frontend Files..." -ForegroundColor Yellow

# Public files
New-Item -ItemType File -Path "frontend/public/index.html" -Force
New-Item -ItemType File -Path "frontend/public/logo.svg" -Force

# Common components
New-Item -ItemType File -Path "frontend/src/components/common/Header.jsx" -Force
New-Item -ItemType File -Path "frontend/src/components/common/Sidebar.jsx" -Force
New-Item -ItemType File -Path "frontend/src/components/common/LoadingSpinner.jsx" -Force
New-Item -ItemType File -Path "frontend/src/components/common/Modal.jsx" -Force

# Dashboard components
New-Item -ItemType File -Path "frontend/src/components/dashboard/MetricsCard.jsx" -Force
New-Item -ItemType File -Path "frontend/src/components/dashboard/ActivityFeed.jsx" -Force
New-Item -ItemType File -Path "frontend/src/components/dashboard/QuickActions.jsx" -Force

# Platform components
New-Item -ItemType File -Path "frontend/src/components/platforms/PlatformCard.jsx" -Force
New-Item -ItemType File -Path "frontend/src/components/platforms/ConnectButton.jsx" -Force
New-Item -ItemType File -Path "frontend/src/components/platforms/StatusBadge.jsx" -Force

# Automation components
New-Item -ItemType File -Path "frontend/src/components/automation/AutoReplySetup.jsx" -Force
New-Item -ItemType File -Path "frontend/src/components/automation/SchedulePost.jsx" -Force
New-Item -ItemType File -Path "frontend/src/components/automation/RuleBuilder.jsx" -Force

# Analytics components
New-Item -ItemType File -Path "frontend/src/components/analytics/Chart.jsx" -Force
New-Item -ItemType File -Path "frontend/src/components/analytics/MetricsTable.jsx" -Force
New-Item -ItemType File -Path "frontend/src/components/analytics/ExportData.jsx" -Force

# Auth pages
New-Item -ItemType File -Path "frontend/src/pages/auth/Login.jsx" -Force
New-Item -ItemType File -Path "frontend/src/pages/auth/Signup.jsx" -Force
New-Item -ItemType File -Path "frontend/src/pages/auth/ForgotPassword.jsx" -Force

# Dashboard pages
New-Item -ItemType File -Path "frontend/src/pages/dashboard/Dashboard.jsx" -Force
New-Item -ItemType File -Path "frontend/src/pages/dashboard/Overview.jsx" -Force
New-Item -ItemType File -Path "frontend/src/pages/dashboard/QuickStart.jsx" -Force

# Platform pages
New-Item -ItemType File -Path "frontend/src/pages/platforms/Connections.jsx" -Force
New-Item -ItemType File -Path "frontend/src/pages/platforms/SocialMedia.jsx" -Force
New-Item -ItemType File -Path "frontend/src/pages/platforms/Reviews.jsx" -Force
New-Item -ItemType File -Path "frontend/src/pages/platforms/Messaging.jsx" -Force

# Automation pages
New-Item -ItemType File -Path "frontend/src/pages/automation/AutoReplies.jsx" -Force
New-Item -ItemType File -Path "frontend/src/pages/automation/ContentScheduler.jsx" -Force
New-Item -ItemType File -Path "frontend/src/pages/automation/ReviewManager.jsx" -Force
New-Item -ItemType File -Path "frontend/src/pages/automation/Workflows.jsx" -Force

# Content pages
New-Item -ItemType File -Path "frontend/src/pages/content/ContentLibrary.jsx" -Force
New-Item -ItemType File -Path "frontend/src/pages/content/CreatePost.jsx" -Force
New-Item -ItemType File -Path "frontend/src/pages/content/Templates.jsx" -Force

# Analytics pages
New-Item -ItemType File -Path "frontend/src/pages/analytics/Analytics.jsx" -Force
New-Item -ItemType File -Path "frontend/src/pages/analytics/Reports.jsx" -Force
New-Item -ItemType File -Path "frontend/src/pages/analytics/Insights.jsx" -Force

# Settings pages
New-Item -ItemType File -Path "frontend/src/pages/settings/Profile.jsx" -Force
New-Item -ItemType File -Path "frontend/src/pages/settings/BusinessInfo.jsx" -Force
New-Item -ItemType File -Path "frontend/src/pages/settings/Billing.jsx" -Force
New-Item -ItemType File -Path "frontend/src/pages/settings/Integrations.jsx" -Force

# Hooks
New-Item -ItemType File -Path "frontend/src/hooks/useAuth.js" -Force
New-Item -ItemType File -Path "frontend/src/hooks/useAPI.js" -Force
New-Item -ItemType File -Path "frontend/src/hooks/usePlatforms.js" -Force
New-Item -ItemType File -Path "frontend/src/hooks/useAnalytics.js" -Force

# Context
New-Item -ItemType File -Path "frontend/src/context/AuthContext.jsx" -Force
New-Item -ItemType File -Path "frontend/src/context/ThemeContext.jsx" -Force
New-Item -ItemType File -Path "frontend/src/context/BusinessContext.jsx" -Force

# Services
New-Item -ItemType File -Path "frontend/src/services/api.js" -Force
New-Item -ItemType File -Path "frontend/src/services/authService.js" -Force
New-Item -ItemType File -Path "frontend/src/services/platformService.js" -Force
New-Item -ItemType File -Path "frontend/src/services/contentService.js" -Force
New-Item -ItemType File -Path "frontend/src/services/analyticsService.js" -Force

# Utils
New-Item -ItemType File -Path "frontend/src/utils/formatters.js" -Force
New-Item -ItemType File -Path "frontend/src/utils/validators.js" -Force
New-Item -ItemType File -Path "frontend/src/utils/constants.js" -Force
New-Item -ItemType File -Path "frontend/src/utils/helpers.js" -Force

# Styles
New-Item -ItemType File -Path "frontend/src/styles/globals.css" -Force
New-Item -ItemType File -Path "frontend/src/styles/components.css" -Force
New-Item -ItemType File -Path "frontend/src/styles/tailwind.config.js" -Force

# Main frontend files
New-Item -ItemType File -Path "frontend/src/App.jsx" -Force
New-Item -ItemType File -Path "frontend/src/main.jsx" -Force
New-Item -ItemType File -Path "frontend/package.json" -Force
New-Item -ItemType File -Path "frontend/vite.config.js" -Force

# Backend Structure
Write-Host "Creating Backend Structure..." -ForegroundColor Green

# Backend root directories
New-Item -ItemType Directory -Path "backend" -Force
New-Item -ItemType Directory -Path "backend/app" -Force

# Backend models
New-Item -ItemType Directory -Path "backend/app/models" -Force

# Backend routes
New-Item -ItemType Directory -Path "backend/app/routes" -Force

# Backend services
New-Item -ItemType Directory -Path "backend/app/services" -Force
New-Item -ItemType Directory -Path "backend/app/services/social_media" -Force
New-Item -ItemType Directory -Path "backend/app/services/reviews" -Force
New-Item -ItemType Directory -Path "backend/app/services/ecommerce" -Force
New-Item -ItemType Directory -Path "backend/app/services/messaging" -Force
New-Item -ItemType Directory -Path "backend/app/services/content_platforms" -Force
New-Item -ItemType Directory -Path "backend/app/services/qna_platforms" -Force

# Backend AI
New-Item -ItemType Directory -Path "backend/app/ai" -Force

# Backend workers
New-Item -ItemType Directory -Path "backend/app/workers" -Force

# Backend utils
New-Item -ItemType Directory -Path "backend/app/utils" -Force

# Backend tests and migrations
New-Item -ItemType Directory -Path "backend/migrations" -Force
New-Item -ItemType Directory -Path "backend/tests" -Force

# Create Backend Files
Write-Host "Creating Backend Files..." -ForegroundColor Yellow

# Main backend files
New-Item -ItemType File -Path "backend/app/__init__.py" -Force
New-Item -ItemType File -Path "backend/app/config.py" -Force
New-Item -ItemType File -Path "backend/app/extensions.py" -Force
New-Item -ItemType File -Path "backend/app/main.py" -Force

# Models
New-Item -ItemType File -Path "backend/app/models/__init__.py" -Force
New-Item -ItemType File -Path "backend/app/models/user.py" -Force
New-Item -ItemType File -Path "backend/app/models/business.py" -Force
New-Item -ItemType File -Path "backend/app/models/platform_connection.py" -Force
New-Item -ItemType File -Path "backend/app/models/content.py" -Force
New-Item -ItemType File -Path "backend/app/models/automation_rule.py" -Force
New-Item -ItemType File -Path "backend/app/models/analytics.py" -Force
New-Item -ItemType File -Path "backend/app/models/billing.py" -Force

# Routes
New-Item -ItemType File -Path "backend/app/routes/__init__.py" -Force
New-Item -ItemType File -Path "backend/app/routes/auth.py" -Force
New-Item -ItemType File -Path "backend/app/routes/platforms.py" -Force
New-Item -ItemType File -Path "backend/app/routes/content.py" -Force
New-Item -ItemType File -Path "backend/app/routes/automation.py" -Force
New-Item -ItemType File -Path "backend/app/routes/reviews.py" -Force
New-Item -ItemType File -Path "backend/app/routes/messaging.py" -Force
New-Item -ItemType File -Path "backend/app/routes/analytics.py" -Force
New-Item -ItemType File -Path "backend/app/routes/billing.py" -Force

# Social Media Services
New-Item -ItemType File -Path "backend/app/services/__init__.py" -Force
New-Item -ItemType File -Path "backend/app/services/social_media/facebook_service.py" -Force
New-Item -ItemType File -Path "backend/app/services/social_media/instagram_service.py" -Force
New-Item -ItemType File -Path "backend/app/services/social_media/youtube_service.py" -Force
New-Item -ItemType File -Path "backend/app/services/social_media/twitter_service.py" -Force
New-Item -ItemType File -Path "backend/app/services/social_media/linkedin_service.py" -Force
New-Item -ItemType File -Path "backend/app/services/social_media/pinterest_service.py" -Force
New-Item -ItemType File -Path "backend/app/services/social_media/tiktok_service.py" -Force

# Review Services
New-Item -ItemType File -Path "backend/app/services/reviews/google_business.py" -Force
New-Item -ItemType File -Path "backend/app/services/reviews/yelp_service.py" -Force
New-Item -ItemType File -Path "backend/app/services/reviews/trustpilot_service.py" -Force
New-Item -ItemType File -Path "backend/app/services/reviews/tripadvisor_service.py" -Force
New-Item -ItemType File -Path "backend/app/services/reviews/app_store_service.py" -Force

# E-commerce Services
New-Item -ItemType File -Path "backend/app/services/ecommerce/shopify_service.py" -Force
New-Item -ItemType File -Path "backend/app/services/ecommerce/woocommerce_service.py" -Force
New-Item -ItemType File -Path "backend/app/services/ecommerce/amazon_service.py" -Force
New-Item -ItemType File -Path "backend/app/services/ecommerce/etsy_service.py" -Force
New-Item -ItemType File -Path "backend/app/services/ecommerce/ebay_service.py" -Force

# Messaging Services
New-Item -ItemType File -Path "backend/app/services/messaging/whatsapp_business.py" -Force
New-Item -ItemType File -Path "backend/app/services/messaging/telegram_service.py" -Force
New-Item -ItemType File -Path "backend/app/services/messaging/email_service.py" -Force
New-Item -ItemType File -Path "backend/app/services/messaging/sms_service.py" -Force

# Content Platform Services
New-Item -ItemType File -Path "backend/app/services/content_platforms/wordpress_service.py" -Force
New-Item -ItemType File -Path "backend/app/services/content_platforms/medium_service.py" -Force
New-Item -ItemType File -Path "backend/app/services/content_platforms/substack_service.py" -Force
New-Item -ItemType File -Path "backend/app/services/content_platforms/ghost_service.py" -Force

# Q&A Platform Services
New-Item -ItemType File -Path "backend/app/services/qna_platforms/quora_service.py" -Force
New-Item -ItemType File -Path "backend/app/services/qna_platforms/reddit_service.py" -Force
New-Item -ItemType File -Path "backend/app/services/qna_platforms/stackoverflow_service.py" -Force

# AI Services
New-Item -ItemType File -Path "backend/app/ai/__init__.py" -Force
New-Item -ItemType File -Path "backend/app/ai/content_generator.py" -Force
New-Item -ItemType File -Path "backend/app/ai/reply_generator.py" -Force
New-Item -ItemType File -Path "backend/app/ai/sentiment_analyzer.py" -Force
New-Item -ItemType File -Path "backend/app/ai/image_generator.py" -Force
New-Item -ItemType File -Path "backend/app/ai/prompt_templates.py" -Force

# Workers
New-Item -ItemType File -Path "backend/app/workers/__init__.py" -Force
New-Item -ItemType File -Path "backend/app/workers/scheduler.py" -Force
New-Item -ItemType File -Path "backend/app/workers/auto_responder.py" -Force
New-Item -ItemType File -Path "backend/app/workers/content_publisher.py" -Force
New-Item -ItemType File -Path "backend/app/workers/review_monitor.py" -Force
New-Item -ItemType File -Path "backend/app/workers/analytics_collector.py" -Force

# Utils
New-Item -ItemType File -Path "backend/app/utils/__init__.py" -Force
New-Item -ItemType File -Path "backend/app/utils/auth_helpers.py" -Force
New-Item -ItemType File -Path "backend/app/utils/validators.py" -Force
New-Item -ItemType File -Path "backend/app/utils/formatters.py" -Force
New-Item -ItemType File -Path "backend/app/utils/rate_limiter.py" -Force
New-Item -ItemType File -Path "backend/app/utils/error_handlers.py" -Force

# Tests
New-Item -ItemType File -Path "backend/tests/test_auth.py" -Force
New-Item -ItemType File -Path "backend/tests/test_platforms.py" -Force
New-Item -ItemType File -Path "backend/tests/test_automation.py" -Force
New-Item -ItemType File -Path "backend/tests/test_workers.py" -Force

# Backend config files
New-Item -ItemType File -Path "backend/requirements.txt" -Force
New-Item -ItemType File -Path "backend/Dockerfile" -Force
New-Item -ItemType File -Path "backend/celery_app.py" -Force

# Shared Structure
Write-Host "Creating Shared Structure..." -ForegroundColor Green

New-Item -ItemType Directory -Path "shared" -Force
New-Item -ItemType Directory -Path "shared/schemas" -Force
New-Item -ItemType Directory -Path "shared/constants" -Force
New-Item -ItemType Directory -Path "shared/utils" -Force

# Shared files
New-Item -ItemType File -Path "shared/schemas/user_schema.py" -Force
New-Item -ItemType File -Path "shared/schemas/platform_schema.py" -Force
New-Item -ItemType File -Path "shared/schemas/content_schema.py" -Force
New-Item -ItemType File -Path "shared/constants/platforms.py" -Force
New-Item -ItemType File -Path "shared/constants/content_types.py" -Force
New-Item -ItemType File -Path "shared/constants/error_codes.py" -Force
New-Item -ItemType File -Path "shared/utils/encryption.py" -Force
New-Item -ItemType File -Path "shared/utils/validators.py" -Force
New-Item -ItemType File -Path "shared/utils/formatters.py" -Force

# Automation Structure
Write-Host "Creating Automation Structure..." -ForegroundColor Green

New-Item -ItemType Directory -Path "automation" -Force
New-Item -ItemType Directory -Path "automation/playwright_scripts" -Force
New-Item -ItemType Directory -Path "automation/selenium_scripts" -Force

# Automation files
New-Item -ItemType File -Path "automation/playwright_scripts/tiktok_poster.py" -Force
New-Item -ItemType File -Path "automation/playwright_scripts/pinterest_automation.py" -Force
New-Item -ItemType File -Path "automation/playwright_scripts/instagram_story_poster.py" -Force
New-Item -ItemType File -Path "automation/selenium_scripts/linkedin_automation.py" -Force
New-Item -ItemType File -Path "automation/selenium_scripts/facebook_groups.py" -Force

# Documentation Structure
Write-Host "Creating Documentation Structure..." -ForegroundColor Green

New-Item -ItemType Directory -Path "docs" -Force
New-Item -ItemType Directory -Path "docs/api" -Force
New-Item -ItemType Directory -Path "docs/setup" -Force
New-Item -ItemType Directory -Path "docs/architecture" -Force
New-Item -ItemType Directory -Path "docs/user_guides" -Force

# Documentation files
New-Item -ItemType File -Path "docs/api/authentication.md" -Force
New-Item -ItemType File -Path "docs/api/platforms.md" -Force
New-Item -ItemType File -Path "docs/api/automation.md" -Force
New-Item -ItemType File -Path "docs/setup/installation.md" -Force
New-Item -ItemType File -Path "docs/setup/platform_setup.md" -Force
New-Item -ItemType File -Path "docs/setup/deployment.md" -Force
New-Item -ItemType File -Path "docs/architecture/overview.md" -Force
New-Item -ItemType File -Path "docs/architecture/database_design.md" -Force
New-Item -ItemType File -Path "docs/architecture/api_design.md" -Force
New-Item -ItemType File -Path "docs/user_guides/getting_started.md" -Force
New-Item -ItemType File -Path "docs/user_guides/automation_setup.md" -Force
New-Item -ItemType File -Path "docs/user_guides/troubleshooting.md" -Force

# Scripts Structure
Write-Host "Creating Scripts Structure..." -ForegroundColor Green

New-Item -ItemType Directory -Path "scripts" -Force

# Script files
New-Item -ItemType File -Path "scripts/deploy.sh" -Force
New-Item -ItemType File -Path "scripts/backup_db.py" -Force
New-Item -ItemType File -Path "scripts/migrate_data.py" -Force
New-Item -ItemType File -Path "scripts/seed_data.py" -Force

# Config Structure
Write-Host "Creating Config Structure..." -ForegroundColor Green

New-Item -ItemType Directory -Path "config" -Force

# Config files
New-Item -ItemType File -Path "config/docker-compose.yml" -Force
New-Item -ItemType File -Path "config/docker-compose.prod.yml" -Force
New-Item -ItemType File -Path "config/nginx.conf" -Force
New-Item -ItemType File -Path "config/redis.conf" -Force

# Root Files
Write-Host "Creating Root Files..." -ForegroundColor Green

New-Item -ItemType File -Path ".env.example" -Force
New-Item -ItemType File -Path ".gitignore" -Force
New-Item -ItemType File -Path "README.md" -Force
New-Item -ItemType File -Path "LICENSE" -Force

Write-Host "✅ Complete SMB Automation Hub project structure created successfully!" -ForegroundColor Green
Write-Host "📁 Total folders and files created in: $(Get-Location)" -ForegroundColor Cyan
Write-Host "🚀 You can now start developing your multi-platform automation platform!" -ForegroundColor Yellow

# Optional: Open the project in VS Code
$openInVSCode = Read-Host "Do you want to open this project in VS Code? (y/n)"
if ($openInVSCode -eq "y" -or $openInVSCode -eq "Y") {
    code .
}