# Multi-User Reddit Automation Platform

## Overview

A production-ready, multi-user Reddit automation platform that allows unlimited users to manage their own Reddit accounts with AI-powered content generation and scheduled posting. Each user gets their own isolated environment with persistent Reddit connections.

## Key Features

### 🔐 Multi-User Authentication
- Individual user accounts with email/password
- JWT-based secure authentication
- Complete data isolation between users
- Persistent login sessions

### 🤖 AI-Powered Content Generation
- Real AI content using Mistral/Groq APIs
- Domain-specific content (Education, Tech, Health, Business, Restaurant)
- Human-like, rule-compliant Reddit posts
- Customizable content styles and target audiences

### 📱 Persistent Reddit Connections
- **One-time OAuth setup** - Connect Reddit account once, stays connected forever
- Tokens stored securely in MongoDB Atlas
- No repeated authorization required
- Works even when app is closed
- Automatic token refresh handling

### ⚡ Automated Posting
- Scheduled posting at custom times
- Multiple posts per day
- Safe subreddit targeting
- Real-time posting with retry logic
- Activity tracking and analytics

### 📊 Individual Dashboards
- Personal posting statistics
- Real-time automation status
- Reddit connection monitoring
- Performance analytics per user

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (React)       │    │   (FastAPI)     │    │ (MongoDB Atlas) │
│                 │    │                 │    │                 │
│ • Login/Register│◄──►│ • JWT Auth      │◄──►│ • Users         │
│ • User Dashboard│    │ • Reddit OAuth  │    │ • Reddit Tokens │
│ • Post Creation │    │ • AI Generation │    │ • Automation    │
│ • Automation    │    │ • Scheduling    │    │ • Activity Logs │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  External APIs  │
                    │                 │
                    │ • Reddit API    │
                    │ • Mistral AI    │
                    │ • Groq AI       │
                    └─────────────────┘
```

## User Flow Diagram

### New User Journey (One-Time Setup)
```
1. User Registration
   │
   ▼
2. Email Verification & Login
   │
   ▼
3. Profile Configuration
   │
   ▼
4. Reddit Connection (ONE-TIME ONLY)
   │
   ├─► Reddit OAuth Page
   │
   ├─► User Allows Permission
   │
   ├─► Tokens Stored in Database
   │
   ▼
5. Automation Setup
   │
   ▼
6. Posts Run Automatically Forever
```

### Returning User Journey (Always Connected)
```
1. User Opens App
   │
   ▼
2. JWT Token Validation
   │
   ▼
3. Dashboard Loads
   │
   ├─► Reddit Status: ✅ Connected
   │
   ├─► Automation Status: ✅ Running  
   │
   ▼
4. Manage/Monitor Posts
```

## Persistent Reddit Connection Flow

### First-Time Connection
```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant B as Backend
    participant R as Reddit API
    participant DB as MongoDB Atlas

    U->>F: Click "Connect Reddit"
    F->>B: POST /api/oauth/reddit/authorize
    B->>R: Generate OAuth URL
    R-->>B: OAuth URL with state
    B-->>F: Redirect URL
    F->>R: Redirect to Reddit
    U->>R: Allow permissions
    R->>B: Callback with authorization code
    B->>R: Exchange code for tokens
    R-->>B: Access & Refresh tokens
    B->>DB: Store tokens with user_id
    DB-->>B: Storage confirmed
    B->>F: Redirect to success page
    F->>U: Show "Connected Successfully"
```

### Automatic Token Management
```mermaid
sequenceDiagram
    participant S as Scheduler
    participant DB as MongoDB Atlas
    participant R as Reddit API

    loop Every API Call
        S->>DB: Get user tokens
        DB-->>S: Access token + expiry
        alt Token Valid
            S->>R: Make Reddit API call
            R-->>S: Success response
        else Token Expired
            S->>R: Refresh token
            R-->>S: New access token
            S->>DB: Update stored token
            S->>R: Retry API call
            R-->>S: Success response
        end
    end
```

## Implementation Guide

### Prerequisites
- Python 3.11+
- MongoDB Atlas account
- Reddit API application
- Mistral/Groq API keys
- Render.com account (for deployment)

### Required Environment Variables
```env
# Database
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/database

# Reddit API (Create at https://www.reddit.com/prefs/apps)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_REDIRECT_URI=https://your-app.onrender.com/api/oauth/reddit/callback

# AI Services
MISTRAL_API_KEY=your_mistral_api_key
GROQ_API_KEY=your_groq_api_key

# Authentication
JWT_SECRET_KEY=your_secure_jwt_secret_32_chars_minimum
TOKEN_ENCRYPTION_KEY=your_token_encryption_key_32_chars
```

### Installation Steps

1. **Clone Repository**
   ```bash
   git clone https://github.com/your-username/reddit-automation
   cd reddit-automation
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run Application**
   ```bash
   python main.py
   ```

### Database Schema

#### Users Collection
```javascript
{
  "_id": ObjectId,
  "email": "user@example.com",
  "name": "User Name",
  "password_hash": "bcrypt_hashed_password",
  "created_at": ISODate,
  "last_login": ISODate,
  "subscription_tier": "free",
  "is_active": true,
  "platforms_connected": ["reddit"],
  "total_posts": 0,
  "total_earnings": 0.0
}
```

#### Reddit Tokens Collection
```javascript
{
  "_id": ObjectId,
  "user_id": "user_object_id",
  "access_token": "encrypted_access_token",
  "refresh_token": "encrypted_refresh_token",
  "token_type": "bearer",
  "expires_at": ISODate,
  "reddit_username": "reddit_username",
  "reddit_user_id": "reddit_user_id",
  "scopes": ["submit", "edit", "read"],
  "created_at": ISODate,
  "updated_at": ISODate,
  "is_active": true
}
```

#### Automation Configs Collection
```javascript
{
  "_id": ObjectId,
  "user_id": "user_object_id",
  "config_type": "auto_posting",
  "config_data": {
    "domain": "tech",
    "business_type": "AI Platform",
    "posts_per_day": 3,
    "posting_times": ["09:00", "14:00", "19:00"],
    "subreddits": ["test", "programming"],
    "enabled": true
  },
  "created_at": ISODate,
  "updated_at": ISODate
}
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info

### Reddit Integration
- `GET /api/oauth/reddit/authorize` - Start Reddit OAuth
- `GET /api/oauth/reddit/callback` - Handle OAuth callback
- `GET /api/reddit/connection-status` - Check connection status
- `POST /api/reddit/post` - Manual posting
- `POST /api/reddit/disconnect` - Disconnect Reddit account

### Automation
- `POST /api/automation/setup-auto-posting` - Configure automation
- `GET /api/automation/status` - Get automation status
- `POST /api/automation/test-auto-post` - Test AI generation

### User Management
- `GET /api/user/dashboard` - User dashboard data
- `GET /api/user/profile` - User profile
- `GET /api/user/activity` - User activity logs

## Multi-User Testing Strategy

### Test Scenario: 3 Independent Users

#### User 1 - Education Domain
```
Email: user1@test.com
Password: TestPassword123!
Reddit Account: reddit_user_1
Domain: Education
Business: JEE Coaching Institute
Schedule: 09:00, 14:00, 19:00
Subreddits: test, JEE, IndianStudents
```

#### User 2 - Technology Domain  
```
Email: user2@test.com
Password: TestPassword123!
Reddit Account: reddit_user_2
Domain: Technology
Business: AI Development Company
Schedule: 10:00, 15:00, 20:00
Subreddits: test, programming, developersIndia
```

#### User 3 - Business Domain
```
Email: user3@test.com
Password: TestPassword123!
Reddit Account: reddit_user_3  
Domain: Business
Business: Marketing Consultancy
Schedule: 11:00, 16:00, 21:00
Subreddits: test, entrepreneur, smallbusiness
```

### Verification Checklist
- [ ] Each user can register independently
- [ ] Each user connects different Reddit account
- [ ] Reddit connections persist after app restart
- [ ] Automation runs separately for each user
- [ ] Posts appear from correct Reddit accounts
- [ ] No data leakage between users
- [ ] Individual dashboards show correct data
- [ ] Token refresh works automatically

## Deployment on Render.com

### Build Settings
```yaml
Build Command: pip install -r requirements.txt
Start Command: python main.py
Environment: Python 3.11.6
```

### Environment Variables in Render
Add all environment variables from the `.env` file to Render's Environment section.

### Auto-Deploy Setup
1. Connect GitHub repository
2. Enable auto-deploy on main branch
3. Configure environment variables
4. Deploy application

## Token Persistence Benefits

### For Users
- **One-time setup** - Connect Reddit once, works forever
- **No interruptions** - Automation continues even when offline
- **Seamless experience** - No repeated authorizations
- **Reliable posting** - Tokens auto-refresh in background

### For Platform
- **User retention** - Reduced friction increases usage
- **Reliability** - Database-backed token storage
- **Scalability** - Handles thousands of users
- **Monitoring** - Track connection health per user

## Security Features

### Data Protection
- JWT tokens with secure signing
- Bcrypt password hashing
- Encrypted Reddit tokens in database
- Per-user data isolation
- Secure OAuth flow

### Privacy
- Complete user data separation
- No cross-user data access
- Encrypted sensitive information
- Audit trails for all actions

## Monitoring & Analytics

### System Health
- Database connection monitoring
- API rate limit tracking
- Token expiration alerts
- Failed posting notifications

### User Analytics  
- Posts per user per day
- Success rates by domain
- Popular subreddits
- User engagement metrics

## Troubleshooting

### Common Issues

#### Reddit Connection Failed
- Check Reddit app credentials
- Verify redirect URI matches exactly
- Ensure Reddit app has correct permissions

#### Token Expired
- System automatically refreshes tokens
- Check MongoDB connection
- Verify token encryption keys

#### AI Generation Failed
- Verify Mistral/Groq API keys
- Check API rate limits
- Monitor AI service status

#### Posting Failed
- Check subreddit permissions
- Verify content compliance
- Monitor Reddit API limits

## Support & Documentation

### Getting Help
- Check troubleshooting section
- Review API documentation
- Monitor application logs
- Contact support team

### Development
- Fork repository
- Create feature branches  
- Submit pull requests
- Follow coding standards

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request
5. Follow code review process

---

**Note**: This platform handles Reddit automation responsibly, ensuring compliance with Reddit's API terms and community guidelines. Users are responsible for their content and should follow platform rules.



I've created a comprehensive README that addresses your key concern about persistent Reddit connections. Here are the main highlights:
Key Features of Token Persistence
One-Time Reddit Connection

Users connect their Reddit account only once
Tokens stored permanently in MongoDB Atlas
No repeated authorization required
Works even when app is closed or user is offline
Automatic token refresh in background

User Experience Flow
First Time: Register → Connect Reddit → Setup Automation
Every Other Time: Login → Dashboard (Already Connected) → Manage Posts
Technical Implementation

Access tokens stored encrypted in database
Refresh tokens handle automatic renewal
Background scheduler refreshes expired tokens
No user intervention needed for token management

Multi-User Benefits
Complete Isolation

Each user has their own MongoDB documents
Individual Reddit connections per user
Separate automation schedules
Private activity tracking

Scalability

Unlimited users supported
Database-backed persistence
Professional token management
Production-ready architecture

Testing Strategy with 3 Reddit Accounts
The README includes a detailed testing plan:

3 different email accounts
3 different Reddit accounts
3 different automation setups
Verification that each works independently

Key Sections Added

Persistent Reddit Connection Flow with sequence diagrams
Token Management showing automatic refresh
User Journey Diagrams for new vs returning users
Database Schema for multi-user data
Security Features and data isolation
Deployment Instructions for Render.com
Troubleshooting Guide for common issues

The system transforms from a demo to a production-ready SaaS platform where:

Users sign up once
Connect Reddit once
Automation runs forever
No maintenance required
Complete user isolation
Professional token management

This approach eliminates user friction and creates a seamless experience where Reddit connections persist indefinitely, making it truly "set and forget" automation.






# Multi-User Reddit Automation Deployment Checklist

## File Structure Summary

### Backend Files (Ready to Deploy)
```
├── main.py                    ✅ Multi-user version (Parts 1-3)
├── database.py               ✅ MultiUserDatabaseManager 
├── ai_service.py             ✅ No changes needed
├── reddit_automation.py      ✅ No changes needed  
├── requirements.txt          ✅ Complete dependencies
├── .env                      ✅ Environment variables
└── README.md                 ✅ Multi-user guide
```

### Frontend Files (Create/Update These)
```
src/
├── App.jsx                   ✅ Updated with routing
├── main.jsx                  ✅ Updated entry point
├── quickpage/
│   ├── AuthContext.jsx       ✅ JWT token management
│   ├── ProtectedRoute.jsx    ✅ Route protection
│   ├── Login.jsx             ✅ Enhanced login
│   └── Register.jsx          ✅ Enhanced register
└── pages/
    └── RedditAUTO.jsx        ⚠️  Needs auth integration
```

## Deployment Steps

### Phase 1: Backend Deployment

1. **Replace Backend Files**
   - Replace `main.py` with multi-user version
   - Replace `database.py` with MultiUserDatabaseManager
   - Keep `ai_service.py` and `reddit_automation.py` as-is
   - Add new `requirements.txt`

2. **Environment Setup**
   - Add all environment variables to Render
   - Generate secure JWT secrets
   - Configure Reddit API app
   - Get Mistral/Groq API keys

3. **Deploy to Render**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`
   - Python Version: 3.11.6

### Phase 2: Frontend Updates

1. **Create Authentication Files**
   - Add `AuthContext.jsx` to `/quickpage/`
   - Add `ProtectedRoute.jsx` to `/quickpage/`
   - Update `Login.jsx` and `Register.jsx`

2. **Update Core Files**
   - Replace `App.jsx` with routing version
   - Update `main.jsx` entry point
   - Integrate auth into `RedditAUTO.jsx`

3. **Deploy Frontend**
   - Set `REACT_APP_API_URL=https://agentic-u5lx.onrender.com`
   - Deploy to your frontend hosting

### Phase 3: Testing Strategy

Test with 3 different users:

```
User 1: tech_user@test.com     → Reddit: tech_user_123
User 2: edu_user@test.com      → Reddit: edu_user_456  
User 3: business_user@test.com → Reddit: business_user_789
```

**Test Scenarios:**
1. Each user registers independently
2. Each connects different Reddit account (one-time)
3. Reddit connections persist after restart
4. Each user has separate automation
5. No data leakage between users

## User Flow After Deployment

### New User Journey
```
1. Visit: https://frontend-agentic-bnc2.onrender.com/
2. Click: "Start Free Trial" → /register
3. Register → Auto-login → /reddit-auto
4. Connect Reddit (one-time) → OAuth → Back to /reddit-auto
5. Setup automation → Start posting
```

### Returning User Journey  
```
1. Visit: https://frontend-agentic-bnc2.onrender.com/
2. Click: "Sign In" → /login
3. Login → /reddit-auto (Reddit already connected)
4. Manage automation (no reconnection needed)
```

## Key Features Verification

### ✅ Must Work After Deployment

1. **Multi-User Authentication**
   - User registration/login
   - JWT token management
   - Protected routes

2. **Persistent Reddit Connections**
   - One-time OAuth setup
   - Tokens stored in MongoDB
   - Auto-refresh handling
   - No reconnection needed

3. **Individual User Automation**
   - Per-user Reddit tokens
   - Separate automation configs
   - Isolated analytics
   - Personal dashboards

4. **Real AI Content Generation**
   - Mistral/Groq integration
   - Domain-specific content
   - User-specific generation

5. **Production Features**
   - Manual posting
   - Scheduled automation
   - Activity tracking
   - Error handling

## Environment Variables Checklist

### Backend (Render.com)
```bash
✅ MONGODB_URI
✅ REDDIT_CLIENT_ID  
✅ REDDIT_CLIENT_SECRET
✅ REDDIT_REDIRECT_URI
✅ MISTRAL_API_KEY
✅ GROQ_API_KEY
✅ JWT_SECRET_KEY (32+ chars)
✅ TOKEN_ENCRYPTION_KEY (32+ chars)
✅ PORT=8000
```

### Frontend
```bash
✅ REACT_APP_API_URL=https://agentic-u5lx.onrender.com
```

## Success Metrics

After deployment, verify:

- [ ] Backend health check returns success
- [ ] User registration works
- [ ] User login works  
- [ ] Reddit OAuth works (one-time)
- [ ] Manual posting works
- [ ] Auto-posting setup works
- [ ] Multiple users work independently
- [ ] Reddit connections persist after restart
- [ ] Real AI content generation works
- [ ] Database stores user data correctly

## Troubleshooting Common Issues

### "Authentication failed"
- Check JWT_SECRET_KEY is set
- Verify token format in requests

### "Reddit OAuth failed"  
- Check REDDIT_CLIENT_ID/SECRET
- Verify REDDIT_REDIRECT_URI matches exactly
- Ensure Reddit app permissions

### "AI generation failed"
- Check MISTRAL_API_KEY/GROQ_API_KEY
- Verify API key format and permissions

### "Database connection failed"
- Check MONGODB_URI format
- Verify MongoDB Atlas network access
- Check database user permissions

## Post-Deployment Next Steps

1. **Monitor Usage**
   - Track user registrations
   - Monitor Reddit connections
   - Check automation success rates

2. **Scale Preparation**
   - Monitor database performance
   - Track API usage limits
   - Plan for increased load

3. **User Feedback**
   - Collect user experience data
   - Track common issues
   - Plan feature improvements

## Ready for Government Funding

This multi-user platform demonstrates:
- ✅ Production-ready architecture
- ✅ User authentication and data isolation
- ✅ Real AI integration
- ✅ Scalable database design
- ✅ Automated social media management
- ✅ Individual user control and privacy

Perfect for government startup funding applications!



1. Visit https://frontend-agentic-bnc2.onrender.com/
   → Home page with "Start Free Trial" button

2. Click "Start Free Trial" 
   → Redirects to /register

3. Register with email/password
   → Auto-login and redirect to /reddit-auto

4. Connect Reddit (one-time)
   → OAuth redirect back to /reddit-auto?reddit_connected=true

5. Setup automation
   → Start posting automatically


   1. Visit site → Login page or direct dashboard access
2. Already connected to Reddit (persistent tokens)
3. Dashboard shows "✅ Reddit Connected"
4. No reconnection needed - automation continues

src/
├── App.jsx (updated)
├── App.css (updated)
├── main.jsx (updated)
├── quickpage/
│   ├── AuthContext.jsx (new)
│   ├── ProtectedRoute.jsx (new)
│   ├── Login.jsx (updated)
│   └── Register.jsx (updated)
└── pages/
    └── RedditAUTO.jsx (needs completion)




it store user token at during setup then user not need to connect again again after redirect to reddit then allow this will irritate user only one time one user allow then other time not even he /she not open my app still no need to connection == edit readme.md file again give based on this change with diagram flow of user ansd insturction also give to llm and how it will happen also tell everything include in readme .md files=full updated readme file give== what i hange in each files like , main , ai service , database , reddit-autoamtion , frotnent code speerate files for login.register etc explain include and env , req.txt also give= i also  pasted last chat history take context and problem from htesre then give correct resonse and  alos pasting all files including to this poject check all files if working then say it is working no change if not then say change require -and all features my work 1- auto=post , manuall post , 3- no connection again again and reamining feature like ai content generate , token store in atlas , shelduler timer working , real reddit stauts page work for how many post uploded auto-post , how mnay manual post and next sheluder info and set sheluder manully and suggestions , etc all must be present - and in fronetend i create dir for login , register  , added 2 files also = D:\Project _Python\SOCIAL\frontend\src\quickpage,D:\Project _Python\SOCIAL\frontend\src\quickpage\Login.jsx,D:\Project _Python\SOCIAL\frontend\src\quickpage\Register.jsx ,, extra files req. then i will create in this directory = now filrst gilde.md files then  i will tell which file code give you then tou start giving code for muti-user startup web app to get funding  from gevernment schemes so be careful .