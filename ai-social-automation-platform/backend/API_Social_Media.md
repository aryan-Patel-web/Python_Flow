# Complete Social Media API Credentials Setup Guide for VelocityPost.ai

## 📋 Overview
This guide covers how to obtain API credentials for all social media platforms needed for your VelocityPost.ai application. **Processing times vary from instant to 1-15 days depending on the platform.**

---

## 🔵 1. Facebook/Instagram API Setup

### 📍 Where to Get:
**Website:** https://developers.facebook.com/apps/

### 📝 Step-by-Step Process:

#### Step 1: Create Facebook App
1. Go to https://developers.facebook.com/apps/
2. Click **"Create App"**
3. Select **"Business"** as app type
4. Fill in:
   - **App Name:** VelocityPost AI
   - **Contact Email:** your-email@domain.com
   - **Business Account:** (Optional)

#### Step 2: Configure App
1. Go to **App Settings > Basic**
2. Note down:
   - **App ID** → `FACEBOOK_APP_ID`
   - **App Secret** → `FACEBOOK_APP_SECRET`

#### Step 3: Add Products
1. Click **"+ Add Product"**
2. Add **"Facebook Login"**
3. Add **"Instagram Basic Display"**

#### Step 4: Configure OAuth Settings
1. Go to **Facebook Login > Settings**
2. Add redirect URI: `http://localhost:5000/api/oauth/callback/facebook`
3. For production: `https://yourdomain.com/api/oauth/callback/facebook`

### ⚠️ Important Notes:
- **Instagram uses the same credentials as Facebook**
- **Review Process:** 1-7 days for advanced permissions
- **Business Verification:** May be required for certain features

### 📋 Final Environment Variables:
```env
FACEBOOK_APP_ID=1234567890123456
FACEBOOK_APP_SECRET=abcd1234efgh5678ijkl9012mnop3456
FACEBOOK_CLIENT_ID=1234567890123456
FACEBOOK_CLIENT_SECRET=abcd1234efgh5678ijkl9012mnop3456
INSTAGRAM_CLIENT_ID=1234567890123456
INSTAGRAM_CLIENT_SECRET=abcd1234efgh5678ijkl9012mnop3456
```

---

## 🐦 2. Twitter/X API Setup

### 📍 Where to Get:
**Website:** https://developer.twitter.com/en/portal/dashboard

### 📝 Step-by-Step Process:

#### Step 1: Apply for Developer Account
1. Go to https://developer.twitter.com/en/portal/dashboard
2. Click **"Sign up for free account"**
3. Fill out application form:
   - **Use case:** Social media management tool
   - **Detailed description:** AI-powered social media automation platform

#### Step 2: Create Project & App
1. Create a **Project** (required for API v2)
2. Create an **App** within the project
3. Choose **"Production"** environment

#### Step 3: Get Credentials
1. Go to **"Keys and tokens"** tab
2. Generate and save:
   - **API Key** → `TWITTER_API_KEY`
   - **API Secret** → `TWITTER_API_SECRET`
   - **Bearer Token** → `TWITTER_BEARER_TOKEN`
   - **Access Token** → For user authentication
   - **Access Token Secret** → For user authentication

#### Step 4: Configure OAuth 2.0
1. Go to **App settings > Authentication settings**
2. Enable **"OAuth 2.0"**
3. Add callback URL: `http://localhost:5000/api/oauth/callback/twitter`
4. Set **"Request email from users"** if needed

### ⚠️ Important Notes:
- **Approval Time:** Instant for basic, 1-7 days for elevated access
- **Rate Limits:** Very strict, monitor usage
- **V2 API recommended** for new applications

### 📋 Final Environment Variables:
```env
TWITTER_CLIENT_ID=your_oauth2_client_id
TWITTER_CLIENT_SECRET=your_oauth2_client_secret
TWITTER_API_KEY=abcdefghijk123456789
TWITTER_API_SECRET=xyz789abc123def456ghi789jkl012mno345pqr678
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
```

---

## 💼 3. LinkedIn API Setup

### 📍 Where to Get:
**Website:** https://developer.linkedin.com/apps

### 📝 Step-by-Step Process:

#### Step 1: Create LinkedIn App
1. Go to https://developer.linkedin.com/apps
2. Click **"Create App"**
3. Fill in:
   - **App name:** VelocityPost AI
   - **LinkedIn Company Page:** (Create if needed)
   - **Privacy Policy URL:** Required
   - **App Logo:** Upload 300x300px image

#### Step 2: Configure Authentication
1. Go to **"Auth"** tab
2. Note down:
   - **Client ID** → `LINKEDIN_CLIENT_ID`
   - **Client Secret** → `LINKEDIN_CLIENT_SECRET`

#### Step 3: Add Redirect URLs
1. In **"Auth"** tab under **"OAuth 2.0 settings"**
2. Add: `http://localhost:5000/api/oauth/callback/linkedin`
3. For production: `https://yourdomain.com/api/oauth/callback/linkedin`

#### Step 4: Request Products
1. Go to **"Products"** tab
2. Request access to:
   - **Sign In with LinkedIn**
   - **Share on LinkedIn** (requires verification)

### ⚠️ Important Notes:
- **Company Page Required:** Must have a LinkedIn company page
- **Verification Process:** 5-10 business days for marketing features
- **Limited permissions** without business verification

### 📋 Final Environment Variables:
```env
LINKEDIN_CLIENT_ID=86abcdefgh123456
LINKEDIN_CLIENT_SECRET=AbCdEfGh123456
```

---

## 📺 4. YouTube/Google API Setup

### 📍 Where to Get:
**Website:** https://console.cloud.google.com/

### 📝 Step-by-Step Process:

#### Step 1: Create Google Cloud Project
1. Go to https://console.cloud.google.com/
2. Click **"Select a project"** → **"New Project"**
3. Name: **"VelocityPost AI"**
4. Enable billing (required for most APIs)

#### Step 2: Enable APIs
1. Go to **"APIs & Services"** → **"Library"**
2. Enable these APIs:
   - **YouTube Data API v3**
   - **Google+ API** (for profile info)
   - **People API** (for contacts)

#### Step 3: Create OAuth Credentials
1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
3. Configure OAuth consent screen first:
   - **User Type:** External
   - **App name:** VelocityPost AI
   - **User support email:** your-email@domain.com
   - **Developer contact information:** your-email@domain.com

#### Step 4: Create OAuth Client
1. **Application type:** Web application
2. **Name:** VelocityPost AI Web Client
3. **Authorized redirect URIs:**
   - `http://localhost:5000/api/oauth/callback/google`
   - `http://localhost:5000/api/oauth/callback/youtube`

#### Step 5: Get Credentials
1. Download the JSON file or copy:
   - **Client ID** → `GOOGLE_CLIENT_ID` & `YOUTUBE_CLIENT_ID`
   - **Client Secret** → `GOOGLE_CLIENT_SECRET` & `YOUTUBE_CLIENT_SECRET`

### ⚠️ Important Notes:
- **Verification Required:** For production with >100 users
- **Quota Limits:** 10,000 units/day default
- **Billing Required:** For most API usage

### 📋 Final Environment Variables:
```env
GOOGLE_CLIENT_ID=123456789012-abcdefghijklmnop.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz
YOUTUBE_CLIENT_ID=123456789012-abcdefghijklmnop.apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=GOCSPX-abcdefghijklmnopqrstuvwxyz
```

---

## 📌 5. Pinterest API Setup

### 📍 Where to Get:
**Website:** https://developers.pinterest.com/apps/

### 📝 Step-by-Step Process:

#### Step 1: Create Pinterest App
1. Go to https://developers.pinterest.com/apps/
2. Click **"Connect app"**
3. Fill in:
   - **App name:** VelocityPost AI
   - **App description:** AI-powered social media management
   - **App website:** https://velocitypost.ai

#### Step 2: Configure OAuth
1. Go to your app dashboard
2. Note down:
   - **App ID** → `PINTEREST_CLIENT_ID`
   - **App secret** → `PINTEREST_CLIENT_SECRET`

#### Step 3: Set Redirect URI
1. In app settings, add:
   - `http://localhost:5000/api/oauth/callback/pinterest`

### ⚠️ Important Notes:
- **Business Account Recommended:** For better API access
- **Rate Limits:** 200 calls per hour per user
- **Review Process:** Usually instant approval

### 📋 Final Environment Variables:
```env
PINTEREST_CLIENT_ID=1234567890123456789
PINTEREST_CLIENT_SECRET=abcdefghijklmnopqrstuvwxyz123456789012
```

---

## 🎵 6. TikTok API Setup

### 📍 Where to Get:
**Website:** https://developers.tiktok.com/

### 📝 Step-by-Step Process:

#### Step 1: Apply for TikTok Developer
1. Go to https://developers.tiktok.com/
2. Click **"Get Started"**
3. Complete the application:
   - **Company information**
   - **Use case description**
   - **Expected monthly API calls**

#### Step 2: Create App
1. After approval, go to **"Manage apps"**
2. Click **"Connect an app"**
3. Fill in app details:
   - **App name:** VelocityPost AI
   - **App description:** Social media management platform

#### Step 3: Get Credentials
1. Go to app details
2. Note down:
   - **Client Key** → `TIKTOK_CLIENT_KEY`
   - **Client Secret** → `TIKTOK_CLIENT_SECRET`

#### Step 4: Configure Login Kit
1. Add redirect URI: `http://localhost:5000/api/oauth/callback/tiktok`
2. Configure scopes needed

### ⚠️ Important Notes:
- **Longest Approval Time:** 7-15 business days
- **Strict Review:** Detailed business case required
- **Limited API Access:** Many features restricted

### 📋 Final Environment Variables:
```env
TIKTOK_CLIENT_KEY=aw123456789abcdefgh
TIKTOK_CLIENT_SECRET=xyz789abc123def456ghi789
```

---

## 🤖 7. AI Services Setup

### OpenAI API
**Website:** https://platform.openai.com/api-keys
1. Create account and add billing
2. Generate API key
```env
OPENAI_API_KEY=sk-proj-abcdefghijklmnopqrstuvwxyz123456789
```

### Mistral AI
**Website:** https://console.mistral.ai/
1. Create account
2. Generate API key
```env
MISTRAL_API_KEY=abc123def456ghi789jkl012
```

### Groq API
**Website:** https://console.groq.com/keys
1. Create account
2. Generate API key
```env
GROQ_API_KEY=gsk_abcdefghijklmnopqrstuvwxyz123456789
```

---

## 💳 8. Payment Processors

### Stripe
**Website:** https://dashboard.stripe.com/apikeys
```env
STRIPE_PUBLISHABLE_KEY=pk_test_abcdefghijklmnopqrstuvwxyz
STRIPE_SECRET_KEY=sk_test_abcdefghijklmnopqrstuvwxyz
```

### Razorpay (India)
**Website:** https://dashboard.razorpay.com/app/keys
```env
RAZORPAY_KEY_ID=rzp_test_abcdefghijk
RAZORPAY_KEY_SECRET=xyz123abc456def789ghi012
```

---

## ⏰ Timeline & Approval Process

| Platform | Instant | 1-3 Days | 1-7 Days | 7-15 Days | Special Requirements |
|----------|---------|----------|----------|-----------|-------------------|
| OpenAI | ✅ | | | | Billing required |
| Stripe | ✅ | | | | Business verification for live |
| Google/YouTube | ✅ | | ✅ | | Verification for >100 users |
| Facebook/Instagram | ✅ | | ✅ | | Business verification for advanced features |
| Twitter | ✅ | ✅ | | | Elevated access review |
| LinkedIn | ✅ | | ✅ | | Company page required |
| Pinterest | ✅ | | | | Usually instant |
| TikTok | | | | ✅ | Longest approval process |

---

## 🚨 Important Warnings

### Security
- **Never commit API keys to version control**
- **Use environment variables always**
- **Rotate keys regularly**
- **Use test keys during development**

### Rate Limits
- **Twitter:** Most restrictive (300 requests/15min)
- **YouTube:** 10,000 quota units/day
- **Facebook:** 200 calls/hour/user
- **Pinterest:** 1000 requests/hour

### Compliance
- **GDPR compliance required for EU users**
- **Privacy policies must be published**
- **Terms of service required**
- **Data handling policies needed**

---

## 🛠️ Testing Your Setup

### 1. Create a test environment file:
```bash
cp .env.example .env.test
```

### 2. Test each OAuth flow individually:
```bash
curl -X GET "http://localhost:5000/api/oauth/facebook"
curl -X GET "http://localhost:5000/api/oauth/twitter" 
curl -X GET "http://localhost:5000/api/oauth/linkedin"
```

### 3. Use Postman collection:
- Import the provided collection
- Set environment variables
- Test each endpoint sequentially

---

## 💡 Pro Tips

### Development Strategy
1. **Start with easiest APIs first** (OpenAI, Stripe)
2. **Use test/sandbox modes everywhere**
3. **Implement one platform at a time**
4. **Test OAuth flows thoroughly**

### Production Readiness
1. **Switch to production keys**
2. **Update redirect URLs to your domain**
3. **Implement proper error handling**
4. **Add rate limiting middleware**
5. **Set up monitoring and alerts**

### Backup Plan
- **Have alternative AI providers configured**
- **Implement graceful degradation**
- **Cache responses where possible**
- **Use webhooks for real-time updates**

---

## 📞 Support Resources

- **Facebook Developer Community:** https://developers.facebook.com/community/
- **Twitter Developer Community:** https://twittercommunity.com/
- **Google Developer Support:** https://developers.google.com/support
- **LinkedIn Developer Support:** Via LinkedIn messaging
- **Pinterest Developer Support:** developers-support@pinterest.com
- **TikTok Developer Support:** Via developer portal

---

**⚡ Quick Start Priority:**
1. OpenAI API (immediate)
2. Stripe (immediate) 
3. Google OAuth (1-2 days)
4. Facebook/Instagram (2-3 days)
5. Twitter (3-5 days)
6. LinkedIn (5-7 days)
7. Pinterest (1-2 days)
8. TikTok (7-15 days) - Start this application first!

**Total estimated time: 1-15 days depending on platform approvals.**

🎯 Immediate Action Items for You:
Day 1 (Today):

Start TikTok application immediately - longest approval time
Get OpenAI API key - instant, needed for core functionality
Set up Stripe account - instant for test mode
Apply for Twitter Developer account - can take 1-7 days

Day 2:

Create Google Cloud project and OAuth credentials
Set up Facebook Developer account and create app
Create LinkedIn Developer app

Day 3-7:

Complete remaining platform setups
Test all OAuth flows in Postman
Implement error handling for failed authentications

⚠️ Critical Notes:

For Postman testing to work, you need REAL credentials - the placeholder values won't work
Start with test/sandbox modes for all platforms
Some platforms require business verification which adds 5-10 days
TikTok has the longest approval process (7-15 days) - apply first!
Keep all credentials secure and never commit them to git

🔥 Pro Tips:

Use test webhook URLs like https://webhook.site during development
Set up proper error handling for when APIs are down
Implement retry logic with exponential backoff
Consider using API key rotation for security
Monitor rate limits closely, especially Twitter's strict limits

Would you like me to create specific Postman test scripts for each platform or help you with any particular OAuth flow implementation?