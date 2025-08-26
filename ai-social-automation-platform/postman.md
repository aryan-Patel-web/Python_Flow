# VelocityPost.ai - Complete Postman API Testing Collection

## Environment Setup
**Base URL:** `http://localhost:5000`

### Postman Environment Variables
- `base_url`: `http://localhost:5000`
- `access_token`: `{{access_token}}` (auto-set after login)
- `user_id`: `{{user_id}}` (auto-set after login)

---

## 1. Health & System Checks

### Health Check
```
GET {{base_url}}/api/health
```
**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-25T10:30:00.000Z",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected",
  "registered_blueprints": ["auth_bp", "oauth_bp", "platforms_bp"],
  "config_loaded": "development"
}
```

### Root Endpoint  
```
GET {{base_url}}/
```
**Expected Response:**
```json
{
  "message": "VelocityPost.ai API Server",
  "version": "1.0.0",
  "status": "operational",
  "environment": "development",
  "docs": "/api/docs",
  "health": "/api/health"
}
```

---

## 2. Authentication & User Management

### Register New User
```
POST {{base_url}}/api/auth/register
Content-Type: application/json

{
  "name": "Test User",
  "email": "test@velocitypost.ai",
  "password": "TestPassword123!"
}
```

**Test Script (Auto-set token):**
```javascript
if (pm.response.code === 201) {
    const response = pm.response.json();
    pm.environment.set("access_token", response.access_token);
    pm.environment.set("user_id", response.user.id);
}
```

**Expected Response:**
```json
{
  "message": "User registered successfully",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": "66c9f1a2b8d4c123456789ab",
    "email": "test@velocitypost.ai",
    "name": "Test User",
    "plan_type": "free",
    "is_active": true,
    "connected_platforms": [],
    "posts_this_month": 0
  }
}
```

### Login User
```
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
    pm.environment.set("user_id", response.user.id);
}
```

### Get User Profile
```
GET {{base_url}}/api/auth/profile
Authorization: Bearer {{access_token}}
```

### Update User Profile
```
PUT {{base_url}}/api/auth/profile
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "name": "Updated Test User"
}
```

### Change Password
```
POST {{base_url}}/api/auth/change-password
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "current_password": "TestPassword123!",
  "new_password": "NewPassword123!"
}
```

### Refresh Token
```
POST {{base_url}}/api/auth/refresh
Authorization: Bearer {{refresh_token}}
```

---

## 3. Content Generation

### Get Content Domains
```
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
      "topics": ["AI and Machine Learning", "Web Development", "Mobile Apps"],
      "tone": "informative, cutting-edge, professional"
    },
    {
      "id": "memes",
      "name": "Memes & Humor",
      "topics": ["Programming Memes", "Work From Home", "Developer Life"],
      "tone": "funny, relatable, casual, witty"
    }
  ],
  "total": 8
}
```

### Generate AI Content
```
POST {{base_url}}/api/content-generator/generate
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "domain": "tech",
  "platform": "instagram",
  "custom_prompt": "Create a post about AI automation in 2025",
  "creativity_level": 80,
  "include_hashtags": true,
  "include_emojis": true,
  "follow_trends": true
}
```

**Expected Response:**
```json
{
  "success": true,
  "generated_content": {
    "content": "🚀 AI Automation is revolutionizing 2025! From smart workflows to predictive analytics, businesses are scaling like never before. What's your favorite AI tool? #AI #Automation #Tech2025 #Innovation #FutureOfWork",
    "domain": "tech",
    "platform": "instagram",
    "performance_prediction": {
      "score": 87,
      "grade": "A",
      "predicted_engagement": {
        "likes": 245,
        "comments": 18,
        "shares": 12
      }
    },
    "metadata": {
      "word_count": 23,
      "character_count": 156,
      "hashtag_count": 5,
      "emoji_count": 1,
      "generated_at": "2025-08-25T10:30:00.000Z",
      "ai_model_used": "mistral",
      "creativity_level": 80
    }
  },
  "user_plan": "free",
  "remaining_credits": "unlimited"
}
```

### Generate Content Variants (Pro+ only)
```
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

### Get Usage Statistics
```
GET {{base_url}}/api/content-generator/usage-stats
Authorization: Bearer {{access_token}}
```

---

## 4. Scheduling & Automation

### Get Schedule Settings
```
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
  },
  "subscription_plan": "free",
  "features_available": {
    "smart_scheduling": false,
    "unlimited_platforms": false
  }
}
```

### Update Schedule Settings
```
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
    },
    "facebook": {
      "enabled": true,
      "posts_per_day": 1,
      "optimal_times": ["12:00"]
    }
  },
  "content_distribution": {
    "tech": 60,
    "business": 30,
    "lifestyle": 10
  }
}
```

### Get Posting Queue
```
GET {{base_url}}/api/scheduler/queue
Authorization: Bearer {{access_token}}
```

### Start Automation
```
POST {{base_url}}/api/scheduler/automation/start
Authorization: Bearer {{access_token}}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Automated posting started successfully",
  "status": "active",
  "next_post_scheduled": "2025-08-25T12:00:00.000Z",
  "platforms_active": ["instagram", "facebook"]
}
```

### Stop Automation
```
POST {{base_url}}/api/scheduler/automation/stop
Authorization: Bearer {{access_token}}
```

### Get Automation Status
```
GET {{base_url}}/api/scheduler/automation/status
Authorization: Bearer {{access_token}}
```

### Preview Schedule
```
POST {{base_url}}/api/scheduler/preview-schedule
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "days": 7
}
```

---

## 5. OAuth & Platform Management

### Get Supported Platforms
```
GET {{base_url}}/api/oauth/platforms
```

### Generate OAuth Authorization URL
```
POST {{base_url}}/api/oauth/auth-url/instagram
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "redirect_uri": "http://localhost:3000/oauth/callback"
}
```

**Expected Response:**
```json
{
  "auth_url": "https://api.instagram.com/oauth/authorize?client_id=123&redirect_uri=...",
  "state": "secure_random_state_string",
  "platform": "instagram"
}
```

### Get Connected Accounts
```
GET {{base_url}}/api/oauth/connected-accounts
Authorization: Bearer {{access_token}}
```

### Test Platform Connection
```
POST {{base_url}}/api/oauth/test-connection/instagram
Authorization: Bearer {{access_token}}
```

### Disconnect Platform
```
DELETE {{base_url}}/api/oauth/disconnect/instagram
Authorization: Bearer {{access_token}}
```

### Get Platform Status
```
GET {{base_url}}/api/platforms/status
Authorization: Bearer {{access_token}}
```

---

## 6. Analytics & Reporting

### Get Analytics Dashboard
```
GET {{base_url}}/api/analytics/dashboard
Authorization: Bearer {{access_token}}
```

**Expected Response:**
```json
{
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
        "date": "2025-08-25",
        "posts": 5,
        "engagement": 234
      }
    ]
  }
}
```

---

## 7. Billing & Subscription Management

### Get Subscription Plans
```
GET {{base_url}}/api/billing/plans
```

### Get Current Subscription
```
GET {{base_url}}/api/billing/subscription
Authorization: Bearer {{access_token}}
```

**Expected Response:**
```json
{
  "success": true,
  "subscription": {
    "current_plan": "free",
    "plan_details": {
      "price": 0,
      "max_platforms": 2,
      "max_posts_per_day": 2,
      "features": ["2 social media platforms", "3 posts per day"]
    },
    "usage": {
      "posts_today": 1,
      "posts_limit": 2,
      "connected_platforms": 0,
      "platforms_limit": 2
    },
    "subscription_status": "active"
  }
}
```

### Subscribe to Plan
```
POST {{base_url}}/api/billing/subscribe
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "plan": "pro",
  "billing_cycle": "monthly",
  "payment_method": {
    "type": "card",
    "token": "pm_test_card_visa"
  }
}
```

### Get Usage Statistics
```
GET {{base_url}}/api/billing/usage?days=30
Authorization: Bearer {{access_token}}
```

### Cancel Subscription
```
POST {{base_url}}/api/billing/cancel
Authorization: Bearer {{access_token}}
Content-Type: application/json

{
  "reason": "No longer needed",
  "immediate": false
}
```

---

## 8. Error Testing Scenarios

### Test Without Token (401 Error)
```
GET {{base_url}}/api/auth/profile
```

**Expected Response:**
```json
{
  "error": "Token required",
  "message": "Please provide an authorization token"
}
```

### Test with Invalid Token (422 Error)
```
GET {{base_url}}/api/auth/profile
Authorization: Bearer invalid_token_here
```

### Test Free User Accessing Pro Features (403 Error)
```
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
  "error": "Multiple variants require Pro plan"
}
```

### Test Invalid Data (400 Error)
```
POST {{base_url}}/api/auth/register
Content-Type: application/json

{
  "email": "invalid-email",
  "password": "123"
}
```

---

## 9. Complete User Journey Test Collection

### Test Collection: Complete User Workflow

1. **Health Check** → Verify server is running
2. **Register User** → Create new account
3. **Login** → Get access token
4. **Get Profile** → Verify authentication
5. **Get Content Domains** → View available options
6. **Generate Content** → Create AI content
7. **Get Schedule Settings** → View automation settings
8. **Update Schedule** → Configure posting times
9. **Get Subscription** → View current plan
10. **Get Analytics** → View performance data

### Automated Test Scripts

**Pre-request Script for Collection:**
```javascript
// Set base URL if not set
if (!pm.environment.get("base_url")) {
    pm.environment.set("base_url", "http://localhost:5000");
}
```

**Test Script for Registration/Login:**
```javascript
pm.test("Status code is 200 or 201", function () {
    pm.expect(pm.response.code).to.be.oneOf([200, 201]);
});

pm.test("Response has access_token", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('access_token');
    pm.environment.set("access_token", jsonData.access_token);
    
    if (jsonData.user && jsonData.user.id) {
        pm.environment.set("user_id", jsonData.user.id);
    }
});
```

**Test Script for Protected Routes:**
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response is JSON", function () {
    pm.response.to.be.json;
});

pm.test("No error in response", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.not.have.property('error');
});
```

---

## 10. Performance & Load Testing

### Load Test Configuration
- **Concurrent Users:** 10
- **Duration:** 60 seconds
- **Key Endpoints:** `/api/auth/login`, `/api/content-generator/generate`

### Performance Benchmarks
- **Health Check:** < 50ms
- **Authentication:** < 200ms
- **Content Generation:** < 2000ms
- **Database Queries:** < 100ms

---

## Quick Start Commands

```bash
# 1. Start the server
python app.py

# 2. Test basic connectivity
curl http://localhost:5000/api/health

# 3. Import this collection into Postman
# 4. Set environment variables
# 5. Run the complete test collection
```

This collection covers all major API endpoints with proper authentication, error handling, and real-world usage scenarios. Each request includes expected responses and test scripts for automated validation.