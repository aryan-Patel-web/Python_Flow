# VelocityPost.ai - Complete Postman API Testing Guide

## Environment Setup

Create a new environment in Postman called "VelocityPost Development":

```
Variable Name          | Initial Value              | Current Value
base_url              | http://localhost:5000      | http://localhost:5000
access_token          |                            | (auto-set after login)
user_id               |                            | (auto-set after login)
user_email            |                            | (auto-set after login)
reset_token           |                            | (for password reset testing)
platform_id           |                            | (for OAuth testing)
post_id               |                            | (for post management)
automation_id         |                            | (for automation testing)
```

---

# API ENDPOINTS COMPLETE GUIDE

## 1. SYSTEM & HEALTH CHECKS

### 1.1 Health Check
**Method:** GET  
**URL:** `{{base_url}}/api/health`  
**Headers:** None  
**Authorization:** None  
**Body:** None  

**Test Script:**
```javascript
pm.test("Health check returns 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has status field", function () {
    const jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('status');
    pm.expect(jsonData.status).to.eql('healthy');
});
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-27T02:30:00.000Z",
  "version": "1.0.0",
  "database": "connected",
  "registered_blueprints": ["auth_bp", "oauth_bp", "automation_bp", "content_generator_bp"]
}
```

### 1.2 API Documentation
**Method:** GET  
**URL:** `{{base_url}}/api/docs`  
**Headers:** None  
**Authorization:** None  
**Body:** None  

**Expected Response:**
HTML page with API documentation or JSON with available endpoints.

---

## 2. AUTHENTICATION ROUTES (`/api/auth/`)

### 2.1 Register New User
**Method:** POST  
**URL:** `{{base_url}}/api/auth/register`  
**Headers:** 
```
Content-Type: application/json
```
**Authorization:** None  

**Body (JSON):**
```json
{
  "name": "Aryan Patel",
  "email": "aryan@example.com",
  "password": "StrongPassword123!"
}
```

**Test Script:**
```javascript
pm.test("Registration successful", function () {
    pm.expect(pm.response.code).to.be.oneOf([201]);
});

pm.test("Response has access_token", function () {
    const response = pm.response.json();
    pm.expect(response).to.have.property('success');
    pm.expect(response.success).to.eql(true);
    pm.expect(response.data).to.have.property('access_token');
    pm.environment.set("access_token", response.data.access_token);
    
    if (response.data.user && response.data.user.id) {
        pm.environment.set("user_id", response.data.user.id);
        pm.environment.set("user_email", response.data.user.email);
    }
});
```

**Expected Response:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "timestamp": "2025-08-27T02:30:00.000Z",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "Bearer",
    "expires_in": 86400,
    "user": {
      "id": "66cc1234567890abcdef1234",
      "name": "Aryan Patel",
      "email": "aryan@example.com",
      "plan_type": "free",
      "is_active": true,
      "email_verified": false,
      "connected_platforms": [],
      "posts_this_month": 0,
      "total_posts": 0,
      "created_at": "2025-08-27T02:30:00.000Z",
      "preferences": {
        "timezone": "UTC",
        "email_notifications": true,
        "auto_posting_enabled": false
      }
    }
  }
}
```

### 2.2 Login User
**Method:** POST  
**URL:** `{{base_url}}/api/auth/login`  
**Headers:** 
```
Content-Type: application/json
```
**Authorization:** None  

**Body (JSON):**
```json
{
  "email": "aryan@example.com",
  "password": "StrongPassword123!"
}
```

**Test Script:**
```javascript
pm.test("Login successful", function () {
    pm.expect(pm.response.code).to.be.oneOf([200]);
});

if (pm.response.code === 200) {
    const response = pm.response.json();
    pm.environment.set("access_token", response.data.access_token);
    pm.environment.set("user_id", response.data.user.id);
    pm.environment.set("user_email", response.data.user.email);
    
    pm.test("Access token received", function () {
        pm.expect(response.data.access_token).to.be.a('string');
        pm.expect(response.data.access_token.length).to.be.above(50);
    });
}
```

### 2.3 Get User Profile
**Method:** GET  
**URL:** `{{base_url}}/api/auth/profile`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

### 2.4 Update User Profile
**Method:** PUT  
**URL:** `{{base_url}}/api/auth/profile`  
**Headers:** 
```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  

**Body (JSON):**
```json
{
  "name": "Updated Aryan Patel",
  "preferences": {
    "timezone": "Asia/Kolkata",
    "email_notifications": true,
    "auto_posting_enabled": true
  }
}
```

### 2.5 Change Password
**Method:** POST  
**URL:** `{{base_url}}/api/auth/change-password`  
**Headers:** 
```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  

**Body (JSON):**
```json
{
  "current_password": "StrongPassword123!",
  "new_password": "NewStrongPassword123!"
}
```

### 2.6 Forgot Password
**Method:** POST  
**URL:** `{{base_url}}/api/auth/forgot-password`  
**Headers:** 
```
Content-Type: application/json
```
**Authorization:** None  

**Body (JSON):**
```json
{
  "email": "aryan@example.com"
}
```

**Test Script:**
```javascript
if (pm.response.code === 200) {
    const response = pm.response.json();
    if (response.data && response.data.reset_token) {
        pm.environment.set("reset_token", response.data.reset_token);
    }
}
```

### 2.7 Reset Password
**Method:** POST  
**URL:** `{{base_url}}/api/auth/reset-password`  
**Headers:** 
```
Content-Type: application/json
```
**Authorization:** None  

**Body (JSON):**
```json
{
  "token": "{{reset_token}}",
  "new_password": "ResetPassword123!"
}
```

### 2.8 Verify Token
**Method:** POST  
**URL:** `{{base_url}}/api/auth/verify-token`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

### 2.9 Logout User
**Method:** POST  
**URL:** `{{base_url}}/api/auth/logout`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

### 2.10 Delete Account
**Method:** DELETE  
**URL:** `{{base_url}}/api/auth/delete-account`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

---

## 3. OAUTH PLATFORM MANAGEMENT (`/api/oauth/`)

### 3.1 Get Supported Platforms
**Method:** GET  
**URL:** `{{base_url}}/api/oauth/platforms`  
**Headers:** None  
**Authorization:** None  
**Body:** None  

**Expected Response:**
```json
{
  "success": true,
  "message": "Platforms retrieved successfully",
  "timestamp": "2025-08-27T02:30:00.000Z",
  "data": {
    "platforms": [
      {
        "id": "facebook",
        "name": "Facebook",
        "description": "Connect your Facebook account to automatically post content",
        "icon": "facebook",
        "color": "#1877F2",
        "available": false,
        "scope": "pages_manage_posts,pages_read_engagement",
        "supported_content": ["text", "images", "links", "videos"],
        "callback_url": "http://localhost:5000/api/oauth/callback/facebook"
      },
      {
        "id": "instagram",
        "name": "Instagram",
        "description": "Connect your Instagram account to automatically post content",
        "icon": "instagram",
        "color": "#E4405F",
        "available": false,
        "scope": "user_profile,user_media",
        "supported_content": ["text", "images", "links"],
        "callback_url": "http://localhost:5000/api/oauth/callback/instagram"
      },
      {
        "id": "twitter",
        "name": "Twitter/X",
        "description": "Connect your Twitter account to automatically post content",
        "icon": "twitter",
        "color": "#1DA1F2",
        "available": false,
        "scope": "tweet.read,tweet.write,users.read",
        "supported_content": ["text", "images", "links"],
        "callback_url": "http://localhost:5000/api/oauth/callback/twitter"
      },
      {
        "id": "linkedin",
        "name": "LinkedIn",
        "description": "Connect your LinkedIn account to automatically post content",
        "icon": "linkedin",
        "color": "#0A66C2",
        "available": false,
        "scope": "r_liteprofile,w_member_social",
        "supported_content": ["text", "images", "links", "articles"],
        "callback_url": "http://localhost:5000/api/oauth/callback/linkedin"
      },
      {
        "id": "youtube",
        "name": "YouTube",
        "description": "Connect your YouTube account to automatically upload videos",
        "icon": "youtube",
        "color": "#FF0000",
        "available": false,
        "scope": "https://www.googleapis.com/auth/youtube.upload",
        "supported_content": ["videos"],
        "callback_url": "http://localhost:5000/api/oauth/callback/youtube"
      },
      {
        "id": "pinterest",
        "name": "Pinterest",
        "description": "Connect your Pinterest account to automatically post pins",
        "icon": "pinterest",
        "color": "#BD081C",
        "available": false,
        "scope": "read_public,write_public",
        "supported_content": ["images", "links"],
        "callback_url": "http://localhost:5000/api/oauth/callback/pinterest"
      },
      {
        "id": "tiktok",
        "name": "TikTok",
        "description": "Connect your TikTok account to automatically post videos",
        "icon": "tiktok",
        "color": "#000000",
        "available": false,
        "scope": "user.info.basic,video.publish",
        "supported_content": ["videos"],
        "callback_url": "http://localhost:5000/api/oauth/callback/tiktok"
      }
    ],
    "total_count": 7,
    "available_count": 0
  }
}
```

### 3.2 Generate OAuth Authorization URL
**Method:** POST  
**URL:** `{{base_url}}/api/oauth/auth-url/facebook`  
**Headers:** 
```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  

**Body (JSON):**
```json
{
  "redirect_uri": "http://localhost:3000/oauth/callback"
}
```

**Test Script:**
```javascript
pm.test("Auth URL generated", function () {
    const response = pm.response.json();
    if (response.success) {
        pm.environment.set("platform_id", "facebook");
        if (response.data && response.data.state) {
            pm.environment.set("oauth_state", response.data.state);
        }
    }
});
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Authorization URL generated successfully",
  "timestamp": "2025-08-27T02:30:00.000Z",
  "data": {
    "auth_url": "https://www.facebook.com/v18.0/dialog/oauth?client_id=your_app_id&redirect_uri=http%3A%2F%2Flocalhost%3A5000%2Fapi%2Foauth%2Fcallback%2Ffacebook&scope=pages_manage_posts%2Cpages_read_engagement&response_type=code&state=abc123def456ghi789",
    "state": "abc123def456ghi789",
    "platform": "facebook",
    "expires_in": 600,
    "redirect_uri": "http://localhost:5000/api/oauth/callback/facebook"
  }
}
```

### 3.3 OAuth Callback Handler
**Method:** GET  
**URL:** `{{base_url}}/api/oauth/callback/facebook?code=AUTH_CODE&state=abc123def456ghi789`  
**Headers:** None  
**Authorization:** None  
**Body:** None  

### 3.4 Get Connected Accounts
**Method:** GET  
**URL:** `{{base_url}}/api/oauth/connected-accounts`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

**Expected Response:**
```json
{
  "success": true,
  "message": "Connected accounts retrieved successfully",
  "timestamp": "2025-08-27T02:30:00.000Z",
  "data": {
    "accounts": [
      {
        "id": "66cc1234567890abcdef1234",
        "platform": "facebook",
        "platform_user_id": "facebook_user_123",
        "username": "john.doe",
        "display_name": "John Doe",
        "profile_picture": "https://graph.facebook.com/facebook_user_123/picture",
        "is_active": true,
        "connected_at": "2025-08-27T02:30:00.000Z",
        "last_used": "2025-08-27T02:30:00.000Z",
        "permissions": ["pages_manage_posts", "pages_read_engagement"],
        "expires_at": "2025-11-27T02:30:00.000Z"
      }
    ],
    "total_count": 1,
    "active_count": 1,
    "platforms_summary": {
      "facebook": 1,
      "instagram": 0,
      "twitter": 0,
      "linkedin": 0,
      "youtube": 0,
      "pinterest": 0,
      "tiktok": 0
    }
  }
}
```

### 3.5 Get Platform Account Details
**Method:** GET  
**URL:** `{{base_url}}/api/oauth/account/facebook`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

### 3.6 Test Platform Connection
**Method:** POST  
**URL:** `{{base_url}}/api/oauth/test-connection/facebook`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

### 3.7 Refresh Platform Token
**Method:** POST  
**URL:** `{{base_url}}/api/oauth/refresh-token/facebook`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

### 3.8 Disconnect Platform
**Method:** DELETE  
**URL:** `{{base_url}}/api/oauth/disconnect/facebook`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

**Expected Response:**
```json
{
  "success": true,
  "message": "Facebook account disconnected successfully",
  "timestamp": "2025-08-27T02:30:00.000Z"
}
```

---

## 4. AUTO-POSTING AUTOMATION (`/api/automation/`)

### 4.1 Get Automation Status
**Method:** GET  
**URL:** `{{base_url}}/api/automation/status`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

**Expected Response:**
```json
{
  "success": true,
  "message": "Automation status retrieved successfully",
  "timestamp": "2025-08-27T02:30:00.000Z",
  "data": {
    "automation_status": {
      "is_active": false,
      "selected_domains": [],
      "connected_platforms_count": 0,
      "posting_frequency": {
        "posts_per_day": 2,
        "interval_hours": 12
      },
      "posting_schedule": {
        "times": ["09:00", "13:00", "17:00"],
        "days": ["monday", "tuesday", "wednesday", "thursday", "friday"],
        "timezone": "UTC"
      },
      "content_settings": {
        "tone": "professional",
        "target_audience": "general",
        "include_hashtags": true,
        "auto_optimize": true,
        "content_length": "medium",
        "language": "en"
      },
      "active_hours": {
        "start_time": "09:00",
        "end_time": "18:00",
        "timezone": "UTC"
      },
      "statistics": {
        "posts_today": 0,
        "posts_this_week": 0,
        "posts_this_month": 0,
        "total_automated_posts": 0,
        "next_post_time": null,
        "max_posts_per_day": 2,
        "success_rate": 0,
        "failed_posts": 0
      },
      "last_updated": "2025-08-27T02:30:00.000Z",
      "created_at": "2025-08-27T02:30:00.000Z"
    }
  }
}
```

### 4.2 Start Automation
**Method:** POST  
**URL:** `{{base_url}}/api/automation/start`  
**Headers:** 
```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  

**Body (JSON):**
```json
{
  "platforms": ["facebook", "instagram"],
  "content_domains": ["technology", "business", "memes"],
  "posting_frequency": {
    "posts_per_day": 3,
    "interval_hours": 8
  },
  "posting_schedule": {
    "times": ["09:00", "13:00", "17:00"],
    "days": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday"],
    "timezone": "Asia/Kolkata"
  },
  "content_settings": {
    "tone": "casual",
    "target_audience": "young_professionals",
    "include_hashtags": true,
    "auto_optimize": true,
    "content_length": "medium",
    "language": "en"
  },
  "active_hours": {
    "start_time": "08:00",
    "end_time": "20:00",
    "timezone": "Asia/Kolkata"
  }
}
```

**Test Script:**
```javascript
pm.test("Automation started successfully", function () {
    pm.expect(pm.response.code).to.be.oneOf([200]);
    const response = pm.response.json();
    pm.expect(response.success).to.eql(true);
    
    if (response.data && response.data.automation_id) {
        pm.environment.set("automation_id", response.data.automation_id);
    }
});
```

### 4.3 Stop Automation
**Method:** POST  
**URL:** `{{base_url}}/api/automation/stop`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

### 4.4 Update Automation Settings
**Method:** PUT  
**URL:** `{{base_url}}/api/automation/settings`  
**Headers:** 
```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  

**Body (JSON):**
```json
{
  "posting_frequency": {
    "posts_per_day": 4,
    "interval_hours": 6
  },
  "content_settings": {
    "tone": "professional",
    "target_audience": "business_professionals",
    "include_hashtags": true,
    "auto_optimize": false
  }
}
```

### 4.5 Get Automation History
**Method:** GET  
**URL:** `{{base_url}}/api/automation/history?limit=10&offset=0`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

### 4.6 Get Available Content Domains
**Method:** GET  
**URL:** `{{base_url}}/api/automation/content-domains`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

**Expected Response:**
```json
{
  "success": true,
  "message": "Content domains retrieved successfully",
  "timestamp": "2025-08-27T02:30:00.000Z",
  "data": {
    "domains": [
      {
        "id": "technology",
        "name": "Technology",
        "description": "Latest tech news, gadgets, and innovations",
        "keywords": ["tech", "innovation", "gadgets", "AI", "software"],
        "is_active": true
      },
      {
        "id": "business",
        "name": "Business",
        "description": "Business news, entrepreneurship, and market trends",
        "keywords": ["business", "entrepreneur", "startup", "finance", "marketing"],
        "is_active": true
      },
      {
        "id": "memes",
        "name": "Memes",
        "description": "Funny memes and viral content",
        "keywords": ["memes", "funny", "viral", "humor", "trending"],
        "is_active": true
      },
      {
        "id": "lifestyle",
        "name": "Lifestyle",
        "description": "Lifestyle tips, health, and wellness content",
        "keywords": ["lifestyle", "health", "wellness", "fitness", "food"],
        "is_active": true
      }
    ],
    "total_count": 4,
    "active_count": 4
  }
}
```

### 4.7 Pause Automation
**Method:** POST  
**URL:** `{{base_url}}/api/automation/pause`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

### 4.8 Resume Automation
**Method:** POST  
**URL:** `{{base_url}}/api/automation/resume`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

### 4.9 Test Automation
**Method:** POST  
**URL:** `{{base_url}}/api/automation/test-post`  
**Headers:** 
```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  

**Body (JSON):**
```json
{
  "platforms": ["facebook"],
  "content_domain": "technology",
  "test_mode": true
}
```

---

## 5. AI CONTENT GENERATION (`/api/content/`)

### 5.1 Generate Content
**Method:** POST  
**URL:** `{{base_url}}/api/content/generate`  
**Headers:** 
```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  

**Body (JSON):**
```json
{
  "prompt": "Create a social media post about the latest AI trends",
  "platform": "facebook",
  "tone": "professional",
  "content_type": "text",
  "target_audience": "tech_professionals",
  "include_hashtags": true,
  "include_emojis": false,
  "max_length": 280
}
```

**Test Script:**
```javascript
pm.test("Content generated successfully", function () {
    pm.expect(pm.response.code).to.be.oneOf([200]);
    const response = pm.response.json();
    pm.expect(response.success).to.eql(true);
    pm.expect(response.data).to.have.property('content');
    
    if (response.data.id) {
        pm.environment.set("generated_content_id", response.data.id);
    }
});
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Content generated successfully",
  "timestamp": "2025-08-27T02:30:00.000Z",
  "data": {
    "id": "66cc1234567890abcdef1234",
    "content": "The AI revolution is transforming how we work and live. From automated customer service to predictive analytics, artificial intelligence is becoming integral to business success. Companies embracing AI are seeing 30% improvement in efficiency. What AI tools are you using in your workflow?",
    "platform": "facebook",
    "content_type": "text",
    "tone": "professional",
    "hashtags": ["#AI", "#Technology", "#Business", "#Innovation", "#Automation"],
    "word_count": 47,
    "character_count": 280,
    "estimated_engagement": {
      "likes": "25-50",
      "comments": "5-10",
      "shares": "3-8"
    },
    "generated_at": "2025-08-27T02:30:00.000Z",
    "model_used": "mistral-7b",
    "credits_used": 1
  }
}
```

### 5.2 Generate Image Caption
**Method:** POST  
**URL:** `{{base_url}}/api/content/generate-caption`  
**Headers:** 
```
Content-Type: multipart/form-data
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  

**Body (Form Data):**
```
image: [Upload image file]
platform: instagram
tone: casual
include_hashtags: true
```

### 5.3 Generate Hashtags
**Method:** POST  
**URL:** `{{base_url}}/api/content/generate-hashtags`  
**Headers:** 
```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  

**Body (JSON):**
```json
{
  "content": "Just launched my new tech startup! Excited to share this journey with everyone.",
  "platform": "linkedin",
  "count": 10,
  "trending": true
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Hashtags generated successfully",
  "timestamp": "2025-08-27T02:30:00.000Z",
  "data": {
    "hashtags": [
      "#startup",
      "#entrepreneur",
      "#tech",
      "#innovation",
      "#business",
      "#journey",
      "#launch",
      "#technology",
      "#success",
      "#growth"
    ],
    "trending_hashtags": [
      "#startuplife",
      "#techstartup",
      "#entrepreneurship"
    ],
    "total_count": 10,
    "platform": "linkedin"
  }
}
```

### 5.4 Optimize Content for Platform
**Method:** POST  
**URL:** `{{base_url}}/api/content/optimize`  
**Headers:** 
```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  

**Body (JSON):**
```json
{
  "content": "This is a long form content that needs to be optimized for different social media platforms",
  "source_platform": "facebook",
  "target_platforms": ["twitter", "instagram", "linkedin"],
  "maintain_tone": true
}
```

### 5.5 Content History
**Method:** GET  
**URL:** `{{base_url}}/api/content/history?limit=20&offset=0&platform=all`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

### 5.6 Save Generated Content
**Method:** POST  
**URL:** `{{base_url}}/api/content/save`  
**Headers:** 
```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  

**Body (JSON):**
```json
{
  "content_id": "{{generated_content_id}}",
  "title": "AI Trends Post",
  "tags": ["ai", "technology", "business"],
  "scheduled_for": "2025-08-28T10:00:00.000Z",
  "platforms": ["facebook", "linkedin"]
}
```

### 5.7 Get Content Templates
**Method:** GET  
**URL:** `{{base_url}}/api/content/templates?category=business&platform=linkedin`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

### 5.8 Analyze Content Performance
**Method:** POST  
**URL:** `{{base_url}}/api/content/analyze`  
**Headers:** 
```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  

**Body (JSON):**
```json
{
  "content": "AI is revolutionizing business operations! 🚀 #AI #Technology #Business",
  "platform": "facebook",
  "metrics": {
    "engagement_rate": 0.05,
    "reach": 1000,
    "clicks": 25
  }
}
```

### 5.9 Bulk Content Generation
**Method:** POST  
**URL:** `{{base_url}}/api/content/bulk-generate`  
**Headers:** 
```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  

**Body (JSON):**
```json
{
  "topics": ["AI trends", "Remote work", "Digital marketing"],
  "platforms": ["facebook", "linkedin", "twitter"],
  "count_per_topic": 2,
  "tone": "professional",
  "schedule_posts": false
}
```

---

## 6. POST MANAGEMENT (`/api/posts/`)

### 6.1 Create Manual Post
**Method:** POST  
**URL:** `{{base_url}}/api/posts/create`  
**Headers:** 
```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  

**Body (JSON):**
```json
{
  "content": "Excited to share my latest project! Building an AI-powered social media automation platform. #AI #SocialMedia #Automation",
  "platforms": ["facebook", "linkedin"],
  "schedule_for": "2025-08-28T10:30:00.000Z",
  "media": [],
  "hashtags": ["#AI", "#SocialMedia", "#Automation"],
  "post_type": "text"
}
```

**Test Script:**
```javascript
pm.test("Post created successfully", function () {
    pm.expect(pm.response.code).to.be.oneOf([201]);
    const response = pm.response.json();
    pm.expect(response.success).to.eql(true);
    
    if (response.data && response.data.post_id) {
        pm.environment.set("post_id", response.data.post_id);
    }
});
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Post created successfully",
  "timestamp": "2025-08-27T02:30:00.000Z",
  "data": {
    "post_id": "66cc1234567890abcdef1234",
    "content": "Excited to share my latest project! Building an AI-powered social media automation platform. #AI #SocialMedia #Automation",
    "platforms": ["facebook", "linkedin"],
    "status": "scheduled",
    "scheduled_for": "2025-08-28T10:30:00.000Z",
    "created_at": "2025-08-27T02:30:00.000Z",
    "platform_posts": [
      {
        "platform": "facebook",
        "status": "scheduled",
        "scheduled_for": "2025-08-28T10:30:00.000Z"
      },
      {
        "platform": "linkedin",
        "status": "scheduled",
        "scheduled_for": "2025-08-28T10:30:00.000Z"
      }
    ]
  }
}
```

### 6.2 Get All Posts
**Method:** GET  
**URL:** `{{base_url}}/api/posts?limit=20&offset=0&status=all&platform=all`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

**Expected Response:**
```json
{
  "success": true,
  "message": "Posts retrieved successfully",
  "timestamp": "2025-08-27T02:30:00.000Z",
  "data": {
    "posts": [
      {
        "id": "66cc1234567890abcdef1234",
        "content": "Excited to share my latest project!",
        "platforms": ["facebook", "linkedin"],
        "status": "published",
        "scheduled_for": "2025-08-28T10:30:00.000Z",
        "published_at": "2025-08-28T10:30:00.000Z",
        "created_at": "2025-08-27T02:30:00.000Z",
        "engagement": {
          "total_likes": 25,
          "total_comments": 5,
          "total_shares": 3,
          "total_reach": 500
        },
        "platform_results": [
          {
            "platform": "facebook",
            "status": "published",
            "platform_post_id": "fb_123456789",
            "likes": 15,
            "comments": 3,
            "shares": 2,
            "reach": 300
          },
          {
            "platform": "linkedin",
            "status": "published",
            "platform_post_id": "li_123456789",
            "likes": 10,
            "comments": 2,
            "shares": 1,
            "reach": 200
          }
        ]
      }
    ],
    "pagination": {
      "total_posts": 1,
      "current_page": 1,
      "total_pages": 1,
      "limit": 20,
      "offset": 0
    },
    "summary": {
      "total_posts": 1,
      "published": 1,
      "scheduled": 0,
      "draft": 0,
      "failed": 0
    }
  }
}
```

### 6.3 Get Post by ID
**Method:** GET  
**URL:** `{{base_url}}/api/posts/{{post_id}}`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

### 6.4 Update Post
**Method:** PUT  
**URL:** `{{base_url}}/api/posts/{{post_id}}`  
**Headers:** 
```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  

**Body (JSON):**
```json
{
  "content": "Updated: Excited to share my latest AI project! 🚀",
  "scheduled_for": "2025-08-29T11:00:00.000Z"
}
```

### 6.5 Delete Post
**Method:** DELETE  
**URL:** `{{base_url}}/api/posts/{{post_id}}`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

### 6.6 Duplicate Post
**Method:** POST  
**URL:** `{{base_url}}/api/posts/{{post_id}}/duplicate`  
**Headers:** 
```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  

**Body (JSON):**
```json
{
  "platforms": ["twitter", "instagram"],
  "schedule_for": "2025-08-30T14:00:00.000Z"
}
```

### 6.7 Publish Post Now
**Method:** POST  
**URL:** `{{base_url}}/api/posts/{{post_id}}/publish`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

### 6.8 Get Post Analytics
**Method:** GET  
**URL:** `{{base_url}}/api/posts/{{post_id}}/analytics`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

### 6.9 Upload Media for Post
**Method:** POST  
**URL:** `{{base_url}}/api/posts/upload-media`  
**Headers:** 
```
Content-Type: multipart/form-data
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  

**Body (Form Data):**
```
file: [Upload image/video file]
post_id: {{post_id}}
media_type: image
```

---

## 7. ANALYTICS & INSIGHTS (`/api/analytics/`)

### 7.1 Get Dashboard Overview
**Method:** GET  
**URL:** `{{base_url}}/api/analytics/dashboard`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

**Expected Response:**
```json
{
  "success": true,
  "message": "Analytics dashboard retrieved successfully",
  "timestamp": "2025-08-27T02:30:00.000Z",
  "data": {
    "overview": {
      "total_posts": 45,
      "posts_this_month": 12,
      "connected_platforms": 3,
      "total_engagement": 1250,
      "avg_engagement_rate": 0.035
    },
    "recent_performance": {
      "last_7_days": {
        "posts": 5,
        "engagement": 180,
        "reach": 2500
      },
      "last_30_days": {
        "posts": 20,
        "engagement": 750,
        "reach": 10000
      }
    },
    "platform_breakdown": {
      "facebook": {
        "posts": 20,
        "engagement": 600,
        "reach": 5000
      },
      "linkedin": {
        "posts": 15,
        "engagement": 400,
        "reach": 3000
      },
      "twitter": {
        "posts": 10,
        "engagement": 250,
        "reach": 2000
      }
    },
    "top_performing_posts": [
      {
        "id": "66cc1234567890abcdef1234",
        "content": "AI is transforming business...",
        "platform": "linkedin",
        "engagement": 85,
        "reach": 1200,
        "published_at": "2025-08-25T10:00:00.000Z"
      }
    ]
  }
}
```

### 7.2 Get Platform Analytics
**Method:** GET  
**URL:** `{{base_url}}/api/analytics/platform/facebook?period=30d`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

### 7.3 Get Content Performance
**Method:** GET  
**URL:** `{{base_url}}/api/analytics/content-performance?limit=10&sort=engagement`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

### 7.4 Get Engagement Metrics
**Method:** GET  
**URL:** `{{base_url}}/api/analytics/engagement?start_date=2025-08-01&end_date=2025-08-31`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

### 7.5 Export Analytics Data
**Method:** GET  
**URL:** `{{base_url}}/api/analytics/export?format=csv&period=30d`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

---

## 8. USER PLAN & BILLING (`/api/billing/`)

### 8.1 Get Current Plan
**Method:** GET  
**URL:** `{{base_url}}/api/billing/plan`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

**Expected Response:**
```json
{
  "success": true,
  "message": "Plan information retrieved successfully",
  "timestamp": "2025-08-27T02:30:00.000Z",
  "data": {
    "current_plan": {
      "id": "free",
      "name": "Free Plan",
      "price": 0,
      "billing_cycle": "monthly",
      "features": {
        "posts_per_month": 10,
        "connected_platforms": 2,
        "ai_content_generation": 50,
        "automation": false,
        "analytics": "basic",
        "support": "community"
      },
      "usage": {
        "posts_this_month": 5,
        "connected_platforms": 1,
        "ai_generations_used": 15,
        "automation_active": false
      },
      "limits": {
        "posts_remaining": 5,
        "platforms_remaining": 1,
        "ai_generations_remaining": 35
      }
    },
    "available_plans": [
      {
        "id": "pro",
        "name": "Pro Plan",
        "price": 29,
        "billing_cycle": "monthly",
        "features": {
          "posts_per_month": 100,
          "connected_platforms": 5,
          "ai_content_generation": 500,
          "automation": true,
          "analytics": "advanced",
          "support": "priority"
        }
      },
      {
        "id": "agency",
        "name": "Agency Plan",
        "price": 99,
        "billing_cycle": "monthly",
        "features": {
          "posts_per_month": "unlimited",
          "connected_platforms": "unlimited",
          "ai_content_generation": "unlimited",
          "automation": true,
          "analytics": "premium",
          "support": "dedicated"
        }
      }
    ]
  }
}
```

### 8.2 Upgrade Plan
**Method:** POST  
**URL:** `{{base_url}}/api/billing/upgrade`  
**Headers:** 
```
Content-Type: application/json
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  

**Body (JSON):**
```json
{
  "plan_id": "pro",
  "billing_cycle": "monthly",
  "payment_method": "stripe"
}
```

### 8.3 Get Billing History
**Method:** GET  
**URL:** `{{base_url}}/api/billing/history?limit=10`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

### 8.4 Cancel Subscription
**Method:** POST  
**URL:** `{{base_url}}/api/billing/cancel`  
**Headers:** 
```
Authorization: Bearer {{access_token}}
```
**Authorization:** Bearer Token  
**Body:** None  

---

## ERROR TESTING SCENARIOS

### Test Without Token (401 Error)
**Method:** GET  
**URL:** `{{base_url}}/api/auth/profile`  
**Headers:** None  
**Authorization:** None  
**Body:** None  

**Expected Response:**
```json
{
  "success": false,
  "message": "Authentication required",
  "error": "Missing or invalid authorization header"
}
```

### Test with Invalid Token (401 Error)
**Method:** GET  
**URL:** `{{base_url}}/api/auth/profile`  
**Headers:** 
```
Authorization: Bearer invalid_token_here
```
**Authorization:** Bearer Token  
**Body:** None  

**Expected Response:**
```json
{
  "success": false,
  "message": "Authentication failed",
  "error": "Invalid or expired token"
}
```

### Test Invalid Registration Data (400 Error)
**Method:** POST  
**URL:** `{{base_url}}/api/auth/register`  
**Headers:** 
```
Content-Type: application/json
```
**Authorization:** None  

**Body (JSON):**
```json
{
  "email": "invalid-email",
  "password": "123"
}
```

**Expected Response:**
```json
{
  "success": false,
  "message": "Validation failed",
  "error": {
    "name": "Name is required",
    "email": "Invalid email format",
    "password": "Password must be at least 8 characters long"
  }
}
```

---

## COLLECTION SETUP

### Environment Variables Setup
```javascript
// Add to Collection Pre-request Script
if (!pm.environment.get("base_url")) {
    pm.environment.set("base_url", "http://localhost:5000");
}

// Log request details
console.log("Request:", pm.request.method, pm.request.url);
console.log("Headers:", JSON.stringify(pm.request.headers));
```

### Global Test Scripts
```javascript
// Add to Collection Tests
pm.test("Response time is reasonable", function () {
    pm.expect(pm.response.responseTime).to.be.below(5000);
});

pm.test("Response has correct content type", function () {
    pm.expect(pm.response.headers.get("Content-Type")).to.include("application/json");
});

// Handle token expiration
if (pm.response.code === 401 && pm.response.json().error.includes("expired")) {
    console.log("Token expired, please re-login");
}
```

---

## TESTING SEQUENCE RECOMMENDATIONS

### Phase 1: System Health & Auth (Required First)
1. Health Check
2. Register New User
3. Login User
4. Verify Token
5. Get User Profile

### Phase 2: Platform Management
6. Get Supported Platforms
7. Generate OAuth URL
8. Get Connected Accounts

### Phase 3: Content Generation
9. Generate Content
10. Generate Hashtags
11. Content History
12. Save Content

### Phase 4: Post Management
13. Create Manual Post
14. Get All Posts
15. Get Post Analytics
16. Update Post

### Phase 5: Automation
17. Get Automation Status
18. Get Content Domains
19. Start Automation
20. Get Automation History

### Phase 6: Analytics & Billing
21. Dashboard Analytics
22. Get Current Plan
23. Platform Analytics

### Phase 7: Error Testing
24. Test without authentication
25. Test with invalid data
26. Test rate limiting

---

## TROUBLESHOOTING GUIDE

### Common Issues & Solutions

1. **"Using generated encryption key" Warning**
   - This is cosmetic and doesn't affect functionality
   - Your server is working correctly despite the warning

2. **Authentication Failures**
   - Ensure JWT token is properly set in environment
   - Check token hasn't expired (24 hours)
   - Verify Authorization header format: `Bearer {{access_token}}`

3. **Database Connection Issues**
   - Verify MongoDB is running
   - Check health endpoint shows "database": "connected"

4. **Platform Connection Failures**
   - Ensure OAuth credentials are configured
   - Check callback URLs match your setup
   - Verify platform-specific requirements

5. **Content Generation Errors**
   - Check AI service API keys are configured
   - Verify sufficient credits/quota
   - Test with simpler prompts first

This comprehensive guide covers all your VelocityPost.ai API endpoints with proper Postman configuration, test scripts, and expected responses.
  "