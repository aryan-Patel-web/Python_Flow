# VelocityPost.ai - Complete Postman API Testing Guide

## 🚀 Environment Setup

### Postman Environment Variables
Create a new environment in Postman called "VelocityPost Development" with these variables:

```
Variable Name          | Initial Value              | Current Value
base_url              | http://localhost:5000      | http://localhost:5000
access_token          |                            | (auto-set after login)
refresh_token         |                            | (auto-set after login)
user_id              |                            | (auto-set after login)
user_email           |                            | (auto-set after login)
reset_token          |                            | (for password reset testing)
```

---

## 📂 Collection Structure

### 1. System & Health Checks
### 2. Authentication & User Management  
### 3. Content Generation
### 4. OAuth & Platform Management
### 5. Auto-Posting & Scheduling
### 6. Analytics & Reporting
### 7. Billing & Subscription
### 8. Error Testing Scenarios

---

## 1. 🏥 SYSTEM & HEALTH CHECKS

### 1.1 Health Check
```http
GET {{base_url}}/api/health
```

**Test Script:**
```javascript
pm.test("Health check returns 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has status field", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('status');
});
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-26T21:30:00.000Z",
  "version": "1.0.0",
  "database": "connected",
  "redis": "not-configured",
  "registered_blueprints": ["content_generator_bp", "auth_bp"],
  "config_loaded": "development"
}
```

### 1.2 Root Endpoint  
```http
GET {{base_url}}/
```

### 1.3 API Documentation
```http
GET {{base_url}}/api/docs
```

---

## 2. 🔐 AUTHENTICATION & USER MANAGEMENT

### 2.1 Register New User
```http
POST {{base_url}}/api/auth/register
Content-Type: application/json

{
  "name": "Test User",
  "email": "test@velocitypost.ai",
  "password": "TestPassword123!"
}
```

**Test Script (Auto-set tokens):**
```javascript
pm.test("Registration successful", function () {
    pm.expect(pm.response.code).to.be.oneOf([201]);
});

pm.test("Response has access_token", function () {
    const response = pm.response.json();
    pm.expect(response).to.have.property('access_token');
    pm.environment.set("access_token", response.access_token);
    
    if (response.refresh_token) {
        pm.environment.set("refresh_token", response.refresh_token);
    }
    
    if (response.user && response.user.id) {
        pm.environment.set("user_id", response.user.id);
        pm.environment.set("user_email", response.user.email);
    }
});

pm.test("User has free plan", function () {
    const response = pm.response.json();
    pm.expect(response.user.plan_type).to.eql("free");
});
```

### 2.2 Login User
```http
POST {{base_url}}/api/auth/login
Content-Type: application/json

{
  "email": "test@velocitypost.ai", 
  "password": "TestPassword123!"
}
```

**Test Script:**
```javascript
if (pm.response.code === 200) {
    const response = pm.response.json();
    pm.environment.set("access_token", response.access_token);
    pm.environment.set("refresh_token", response.refresh_token);
    pm.environment.set("user_id", response.user.id);
    pm.environment.set("user_email", response.user.email);
}
```

### 2.3 Get User Profile
```http
GET {{base_url}}/api/auth/profile
Authorization: Bearer {{access_token}}
```

### 2.4 Update User Profile
```http
PUT {{base_url}}/api/auth/profile
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "name": "Updated Test User",
  "preferences": {
    "timezone": "UTC",
    "email_notifications": true,
    "auto_posting_enabled": true
  }
}
```

### 2.5 Change Password
```http
POST {{base_url}}/api/auth/change-password
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "current_password": "TestPassword123!",
  "new_password": "NewPassword123!"
}
```

### 2.6 Refresh Token
```http
POST {{base_url}}/api/auth/refresh
Authorization: Bearer {{refresh_token}}
```

### 2.7 Forgot Password
```http
POST {{base_url}}/api/auth/forgot-password
Content-Type: application/json

{
  "email": "test@velocitypost.ai"
}
```

**Test Script:**
```javascript
if (pm.response.code === 200) {
    const response = pm.response.json();
    if (response.reset_token) {
        pm.environment.set("reset_token", response.reset_token);
    }
}
```

### 2.8 Reset Password
```http
POST {{base_url}}/api/auth/reset-password
Content-Type: application/json

{
  "token": "{{reset_token}}",
  "new_password": "ResetPassword123!"
}
```

### 2.9 Verify Token
```http
POST {{base_url}}/api/auth/verify-token
Authorization: Bearer {{access_token}}
```

### 2.10 Logout User
```http
POST {{base_url}}/api/auth/logout
Authorization: Bearer {{access_token}}
```

### 2.11 Delete Account
```http
DELETE {{base_url}}/api/auth/delete-account
Authorization: Bearer {{access_token}}
```

---

## 3. 🎨 CONTENT GENERATION

### 3.1 Get Content Domains
```http
GET {{base_url}}/api/content-generator/domains
```

**Expected Response:**
```json
{
  "success": true,
  "domains": [
    {
      "id": "tech",
      "name": "Technology & Innovation",
      "topics": ["AI & Machine Learning", "Web Development"],
      "tone": "informative, cutting-edge, professional",
      "pro_required": false
    },
    {
      "id": "memes",
      "name": "Memes & Humor", 
      "topics": ["Programming Memes", "Work From Home"],
      "tone": "funny, relatable, casual, witty",
      "pro_required": false
    }
  ],
  "total": 5
}
```

### 3.2 Get Supported Platforms
```http
GET {{base_url}}/api/content-generator/platforms
```

### 3.3 Generate AI Content
```http
POST {{base_url}}/api/content-generator/generate
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "domain": "tech",
  "platform": "instagram",
  "custom_prompt": "Create a post about AI automation trends in 2025",
  "creativity_level": 80,
  "include_hashtags": true,
  "include_emojis": true
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Content generated successfully",
  "generated_content": {
    "content": "🚀 AI Automation is transforming 2025! From smart workflows to predictive analytics, businesses are scaling faster than ever. What's your favorite AI tool? #AI #Automation #Tech2025 #Innovation #FutureOfWork",
    "domain": "tech",
    "platform": "instagram",
    "performance_prediction": {
      "score": 87.5,
      "grade": "A",
      "predicted_engagement": {
        "likes": 261,
        "comments": 17,
        "shares": 13
      }
    },
    "metadata": {
      "word_count": 24,
      "character_count": 165,
      "hashtag_count": 5,
      "emoji_count": 1,
      "generated_at": "2025-08-26T21:30:00.000Z",
      "creativity_level": 80,
      "ai_model_used": "template_enhanced"
    }
  },
  "user_plan": "free",
  "remaining_credits": "unlimited"
}
```

### 3.4 Generate Content Variants (Pro Feature)
```http
POST {{base_url}}/api/content-generator/generate-variants
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "domain": "business",
  "platform": "linkedin",
  "count": 3,
  "custom_prompt": "Leadership tips for remote teams",
  "creativity_level": 75
}
```

### 3.5 Get Content Templates
```http
GET {{base_url}}/api/content-generator/templates
```

### 3.6 Get Generation History
```http
GET {{base_url}}/api/content-generator/history?limit=20&domain=tech&platform=instagram
Authorization: Bearer {{access_token}}
```

### 3.7 Get Usage Statistics
```http
GET {{base_url}}/api/content-generator/usage-stats
Authorization: Bearer {{access_token}}
```

### 3.8 Test Content Generator
```http
GET {{base_url}}/api/content-generator/test
```

---

## 4. 🔗 OAUTH & PLATFORM MANAGEMENT

### 4.1 Get Supported OAuth Platforms
```http
GET {{base_url}}/api/oauth/platforms
```

### 4.2 Generate OAuth Authorization URL
```http
POST {{base_url}}/api/oauth/auth-url/instagram
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "redirect_uri": "http://localhost:3000/auth/callback/instagram"
}
```

**Expected Response:**
```json
{
  "success": true,
  "auth_url": "https://api.instagram.com/oauth/authorize?client_id=123&redirect_uri=...",
  "state": "secure_random_state_string",
  "platform": "instagram"
}
```

### 4.3 OAuth Callback Handler
```http
POST {{base_url}}/api/oauth/callback/instagram
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "code": "oauth_authorization_code_here",
  "state": "secure_random_state_string"
}
```

### 4.4 Get Connected Accounts
```http
GET {{base_url}}/api/oauth/connected-accounts
Authorization: Bearer {{access_token}}
```

### 4.5 Test Platform Connection
```http
POST {{base_url}}/api/oauth/test-connection/instagram
Authorization: Bearer {{access_token}}
```

### 4.6 Disconnect Platform
```http
DELETE {{base_url}}/api/oauth/disconnect/instagram
Authorization: Bearer {{access_token}}
```

### 4.7 Get Platform Status
```http
GET {{base_url}}/api/platforms/status
Authorization: Bearer {{access_token}}
```

---

## 5. 🤖 AUTO-POSTING & SCHEDULING

### 5.1 Get Auto-Posting Status
```http
GET {{base_url}}/api/auto-posting/status
Authorization: Bearer {{access_token}}
```

### 5.2 Start Auto-Posting
```http
POST {{base_url}}/api/auto-posting/start
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "platforms": ["instagram", "facebook"],
  "content_domains": ["tech", "business"],
  "posting_frequency": {
    "posts_per_day": 2,
    "interval_hours": 12
  }
}
```

### 5.3 Pause Auto-Posting
```http
POST {{base_url}}/api/auto-posting/pause
Authorization: Bearer {{access_token}}
```

### 5.4 Stop Auto-Posting
```http
POST {{base_url}}/api/auto-posting/stop
Authorization: Bearer {{access_token}}
```

### 5.5 Get Schedule Settings
```http
GET {{base_url}}/api/scheduler/settings
Authorization: Bearer {{access_token}}
```

**Expected Response:**
```json
{
  "success": true,
  "settings": {
    "auto_posting_enabled": false,
    "posting_frequency": {
      "posts_per_day": 2,
      "interval_hours": 12
    },
    "active_hours": {
      "start_time": "09:00",
      "end_time": "18:00",
      "timezone": "UTC"
    },
    "platform_settings": {
      "instagram": {
        "enabled": true,
        "posts_per_day": 2,
        "optimal_times": ["10:00", "15:00", "19:00"]
      }
    }
  }
}
```

### 5.6 Update Schedule Settings
```http
PUT {{base_url}}/api/scheduler/settings
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "auto_posting_enabled": true,
  "posting_frequency": {
    "posts_per_day": 3,
    "interval_hours": 8
  },
  "active_hours": {
    "start_time": "09:00",
    "end_time": "18:00",
    "timezone": "UTC"
  },
  "platform_settings": {
    "instagram": {
      "enabled": true,
      "posts_per_day": 2,
      "optimal_times": ["10:00", "15:00"]
    }
  }
}
```

### 5.7 Generate Optimal Times
```http
POST {{base_url}}/api/scheduler/generate-optimal-times
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "platforms": ["instagram", "facebook"],
  "timezone": "UTC",
  "posts_per_day": 3
}
```

### 5.8 Get Posting Queue
```http
GET {{base_url}}/api/scheduler/queue?days=7
Authorization: Bearer {{access_token}}
```

### 5.9 Preview Schedule
```http
POST {{base_url}}/api/scheduler/preview-schedule
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "days": 7,
  "platforms": ["instagram", "facebook"]
}
```

---

## 6. 📊 ANALYTICS & REPORTING

### 6.1 Get Analytics Dashboard
```http
GET {{base_url}}/api/analytics/dashboard?days=30
Authorization: Bearer {{access_token}}
```

**Expected Response:**
```json
{
  "success": true,
  "analytics": {
    "total_posts": 145,
    "total_engagement": 2847,
    "growth_rate": 12.5,
    "best_performing_platform": "instagram",
    "engagement_by_platform": {
      "instagram": 1247,
      "facebook": 856,
      "twitter": 744
    },
    "posts_by_day": [
      {
        "date": "2025-08-26",
        "posts": 5,
        "engagement": 234
      }
    ]
  }
}
```

### 6.2 Get Performance Metrics
```http
GET {{base_url}}/api/analytics/performance?platform=instagram&days=30
Authorization: Bearer {{access_token}}
```

### 6.3 Get Growth Statistics
```http
GET {{base_url}}/api/analytics/growth?period=monthly
Authorization: Bearer {{access_token}}
```

### 6.4 Export Analytics Data
```http
POST {{base_url}}/api/analytics/export
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "format": "csv",
  "date_range": {
    "start": "2025-08-01",
    "end": "2025-08-26"
  },
  "platforms": ["instagram", "facebook"]
}
```

---

## 7. 💳 BILLING & SUBSCRIPTION

### 7.1 Get Subscription Plans
```http
GET {{base_url}}/api/billing/plans
```

**Expected Response:**
```json
{
  "success": true,
  "plans": [
    {
      "id": "free",
      "name": "Free Plan",
      "price": 0,
      "currency": "USD",
      "features": {
        "platforms": 2,
        "posts_per_day": 2,
        "ai_generations_per_month": 50
      }
    },
    {
      "id": "pro",
      "name": "Pro Plan",
      "price": 29,
      "currency": "USD",
      "features": {
        "platforms": 5,
        "posts_per_day": 10,
        "ai_generations_per_month": 500
      }
    }
  ]
}
```

### 7.2 Get Current Subscription
```http
GET {{base_url}}/api/billing/subscription
Authorization: Bearer {{access_token}}
```

### 7.3 Subscribe to Plan (Stripe)
```http
POST {{base_url}}/api/billing/subscribe
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "plan": "pro",
  "billing_cycle": "monthly",
  "payment_method": {
    "type": "stripe",
    "token": "pm_test_card_visa"
  }
}
```

### 7.4 Subscribe to Plan (Razorpay - Indian Users)
```http
POST {{base_url}}/api/billing/subscribe
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "plan": "pro", 
  "billing_cycle": "monthly",
  "payment_method": {
    "type": "razorpay",
    "payment_id": "pay_test123456789"
  }
}
```

### 7.5 Get Usage Statistics
```http
GET {{base_url}}/api/billing/usage?days=30
Authorization: Bearer {{access_token}}
```

### 7.6 Update Payment Method
```http
PUT {{base_url}}/api/billing/payment-method
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "payment_method": {
    "type": "stripe",
    "token": "pm_new_card_token"
  }
}
```

### 7.7 Cancel Subscription
```http
POST {{base_url}}/api/billing/cancel
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "reason": "No longer needed",
  "immediate": false
}
```

### 7.8 Get Invoices
```http
GET {{base_url}}/api/billing/invoices?limit=10
Authorization: Bearer {{access_token}}
```

---

## 8. 🚨 ERROR TESTING SCENARIOS

### 8.1 Test Without Token (401 Error)
```http
GET {{base_url}}/api/auth/profile
```

**Expected Response:**
```json
{
  "success": false,
  "message": "Authentication required",
  "error": "Missing or invalid authorization header"
}
```

### 8.2 Test with Invalid Token (401 Error)
```http
GET {{base_url}}/api/auth/profile
Authorization: Bearer invalid_token_here
```

### 8.3 Test Free User Accessing Pro Features (403 Error)
```http
POST {{base_url}}/api/content-generator/generate-variants
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "domain": "tech",
  "platform": "instagram", 
  "count": 5
}
```

**Expected Response:**
```json
{
  "success": false,
  "message": "Variants generation requires Pro plan",
  "feature_note": "Variants generation requires Pro plan"
}
```

### 8.4 Test Invalid Registration Data (400 Error)
```http
POST {{base_url}}/api/auth/register
Content-Type: application/json

{
  "email": "invalid-email",
  "password": "123"
}
```

### 8.5 Test Duplicate Registration (409 Error)
```http
POST {{base_url}}/api/auth/register
Content-Type: application/json

{
  "name": "Duplicate User",
  "email": "test@velocitypost.ai",
  "password": "TestPassword123!"
}
```

### 8.6 Test Invalid Login (401 Error)
```http
POST {{base_url}}/api/auth/login
Content-Type: application/json

{
  "email": "test@velocitypost.ai",
  "password": "WrongPassword123!"
}
```

### 8.7 Test Weak Password (400 Error)
```http
POST {{base_url}}/api/auth/register
Content-Type: application/json

{
  "name": "Test User",
  "email": "weak@test.com",
  "password": "weak"
}
```

---

## 9. 🔄 COMPLETE USER JOURNEY TEST COLLECTION

### Test Collection: Complete User Workflow

**Collection Pre-request Script:**
```javascript
// Set base URL if not set
if (!pm.environment.get("base_url")) {
    pm.environment.set("base_url", "http://localhost:5000");
}

console.log("Running request to:", pm.request.url);
```

**Collection Test Script:**
```javascript
pm.test("Response time is less than 2000ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(2000);
});

pm.test("Response is JSON", function () {
    pm.response.to.be.json;
});
```

### User Journey Test Sequence:

1. **Health Check** → Verify server is running
2. **Register User** → Create new account  
3. **Login** → Get access token
4. **Get Profile** → Verify authentication
5. **Get Content Domains** → View available options
6. **Generate Content** → Create AI content  
7. **Get Platforms** → View OAuth platforms
8. **Get Schedule Settings** → View automation settings
9. **Update Schedule** → Configure posting times
10. **Get Subscription** → View current plan
11. **Get Analytics** → View performance data
12. **Logout** → End session

---

## 10. 📈 AUTOMATED TEST SCRIPTS

### Universal Test Scripts for Protected Routes:
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has success field", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('success');
});

pm.test("No error in response", function () {
    const jsonData = pm.response.json();
    if (jsonData.success === false) {
        console.log("Error:", jsonData.error);
        console.log("Message:", jsonData.message);
    }
    pm.expect(jsonData.success).to.eql(true);
});
```

### Test Script for Auth Routes:
```javascript
pm.test("Auth response structure", function () {
    const response = pm.response.json();
    
    if (pm.response.code === 200 || pm.response.code === 201) {
        if (response.access_token) {
            pm.environment.set("access_token", response.access_token);
        }
        if (response.refresh_token) {
            pm.environment.set("refresh_token", response.refresh_token);
        }
        if (response.user) {
            pm.environment.set("user_id", response.user.id);
            pm.environment.set("user_email", response.user.email);
        }
    }
});
```

---

## 11. 🔧 PERFORMANCE & LOAD TESTING

### Performance Benchmarks:
- **Health Check:** < 50ms
- **Authentication:** < 200ms  
- **Content Generation:** < 2000ms
- **Database Queries:** < 100ms
- **OAuth Operations:** < 500ms

### Load Test Configuration:
- **Concurrent Users:** 10
- **Duration:** 60 seconds
- **Key Endpoints:** `/api/auth/login`, `/api/content-generator/generate`

---

## 12. 🚀 QUICK START COMMANDS

### Setup Commands:
```bash
# 1. Start the backend server
cd backend/app
python app.py

# 2. Test basic connectivity
curl http://localhost:5000/api/health

# 3. Import collection into Postman
# 4. Set environment variables
# 5. Run the complete test collection
```

### Collection Runner Settings:
- **Environment:** VelocityPost Development
- **Iterations:** 1
- **Delay:** 100ms between requests
- **Data File:** Optional CSV for bulk testing

---

## 13. 📋 TEST CHECKLIST

### Pre-Testing Checklist:
- [ ] Backend server running on port 5000
- [ ] MongoDB connected (check health endpoint)
- [ ] Postman environment configured
- [ ] All environment variables set

### Authentication Testing:
- [ ] User registration works
- [ ] User login returns valid tokens
- [ ] Token refresh functionality
- [ ] Password reset flow
- [ ] Profile CRUD operations
- [ ] Account deletion

### Content Generation Testing:
- [ ] Domain listing
- [ ] Platform listing  
- [ ] Content generation with all parameters
- [ ] Variant generation (Pro feature)
- [ ] Usage statistics
- [ ] Generation history

### OAuth & Platform Testing:
- [ ] Platform listing
- [ ] Auth URL generation
- [ ] Connection testing
- [ ] Account management

### Auto-Posting Testing:
- [ ] Status checking
- [ ] Start/pause/stop operations
- [ ] Schedule configuration
- [ ] Queue management

### Error Handling Testing:
- [ ] Invalid tokens
- [ ] Missing parameters
- [ ] Plan limitations
- [ ] Rate limiting
- [ ] Database failures

This comprehensive guide covers all API endpoints with proper test scripts, expected responses, and error scenarios. Each request includes authentication handling and automated token management for seamless testing.