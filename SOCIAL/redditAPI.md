# Reddit OAuth Web App Setup for Multi-User Platform

## Understanding App Types

### Script vs Web App
- **Script**: For single user, uses username/password (what I showed before)
- **Web App**: For multiple users connecting through OAuth (what you need)

Your platform needs **Web App** because:
- Multiple users will connect their Reddit accounts
- Users authenticate through Reddit's OAuth flow
- Each user grants permission to your app
- Your app posts on behalf of different users

---

## Step 1: Create Reddit Web Application

### 1.1 Navigate to Reddit Apps
- Go to: **https://www.reddit.com/prefs/apps**
- Login with your Reddit account

### 1.2 Create New App
- Click **"Create App"** or **"Create Another App"**

### 1.3 Fill Web App Form
```
App Name: Indian Social Media Automation Platform
App Type: Select "web app" (NOT script)


Description: Multi-user social media automation 
platform for Indian businesses and content creators

About URL: https://yourdomain.com (or 

http://localhost:3000 for development)

Redirect URI: 
http://localhost:8000/api/oauth/reddit/callback
```

**Important Notes:**
- **App Type**: Choose **"web app"**
- **Redirect URI**: Must match exactly what your backend expects
- **About URL**: Your platform's homepage

### 1.4 Click "Create app"

---

## Step 2: Get OAuth Credentials

### 2.1 Note Your Credentials
After creating the web app, you'll see:

```
Client ID: [14 character string under app name]
Example: abcd1234efgh56

Secret: [27 character string next to "secret"]
Example: xyz789abc123def456ghi789jkl012

App Type: web app
Redirect URI: http://localhost:8000/api/oauth/reddit/callback
```

### 2.2 Update Environment Variables
```env
# Reddit OAuth Configuration
REDDIT_CLIENT_ID=abcd1234efgh56
REDDIT_CLIENT_SECRET=xyz789abc123def456ghi789jkl012
REDDIT_REDIRECT_URI=http://localhost:8000/api/oauth/reddit/callback
REDDIT_USER_AGENT=IndianAutomationPlatform/1.0
```

---

## Step 3: OAuth Flow Implementation

### 3.1 OAuth Authorization URL
Your backend creates this URL to redirect users:
```
https://www.reddit.com/api/v1/authorize?
client_id=YOUR_CLIENT_ID&
response_type=code&
state=random_string&
redirect_uri=http://localhost:8000/api/oauth/reddit/callback&
duration=permanent&
scope=identity edit flair history modconfig modflair modlog modposts modwiki mysubreddits privatemessages read report save submit subscribe vote wikiread wikiedit
```

### 3.2 User Flow
1. **User clicks "Connect Reddit"** in your web app
2. **Redirected to Reddit** authorization page
3. **User grants permissions** to your app
4. **Reddit redirects back** to your callback URL with authorization code
5. **Your backend exchanges code** for access token
6. **Store encrypted token** for that user

### 3.3 Required Scopes
For your automation features:
```
identity - Get user info
read - Read posts and comments
submit - Submit posts
edit - Edit posts/comments
vote - Upvote/downvote
save - Save posts
subscribe - Subscribe to subreddits
privatemessages - Send/receive messages
```

---

## Step 4: Backend OAuth Implementation

### 4.1 OAuth Initiation Endpoint
```python
@app.get("/api/oauth/reddit/authorize")
async def reddit_oauth_authorize():
    """Initiate Reddit OAuth flow"""
    state = generate_random_string(32)  # CSRF protection
    
    params = {
        "client_id": settings.reddit_client_id,
        "response_type": "code", 
        "state": state,
        "redirect_uri": settings.reddit_redirect_uri,
        "duration": "permanent",
        "scope": "identity read submit edit vote save subscribe"
    }
    
    # Store state in session/database for verification
    # In production, associate state with current user
    
    auth_url = "https://www.reddit.com/api/v1/authorize?" + urlencode(params)
    
    return {"redirect_url": auth_url, "state": state}
```

### 4.2 OAuth Callback Endpoint
```python
@app.get("/api/oauth/reddit/callback")
async def reddit_oauth_callback(
    code: str,
    state: str,
    current_user: Dict = Depends(get_current_user)
):
    """Handle Reddit OAuth callback"""
    
    # Verify state parameter (CSRF protection)
    # In production, check if state matches stored value
    
    # Exchange authorization code for access token
    token_data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.reddit_redirect_uri
    }
    
    auth = (settings.reddit_client_id, settings.reddit_client_secret)
    headers = {"User-Agent": settings.reddit_user_agent}
    
    response = requests.post(
        "https://www.reddit.com/api/v1/access_token",
        data=token_data,
        auth=auth,
        headers=headers
    )
    
    if response.status_code == 200:
        tokens = response.json()
        
        # Get user info from Reddit
        reddit_user = get_reddit_user_info(tokens["access_token"])
        
        # Store encrypted tokens in database
        await store_user_reddit_tokens(
            current_user["id"],
            tokens["access_token"],
            tokens["refresh_token"],
            reddit_user
        )
        
        return {
            "success": True,
            "message": "Reddit account connected successfully",
            "reddit_username": reddit_user["name"]
        }
    else:
        return {"success": False, "error": "OAuth token exchange failed"}
```

### 4.3 Store User Tokens
```python
async def store_user_reddit_tokens(user_id: str, access_token: str, refresh_token: str, reddit_user: dict):
    """Store encrypted Reddit tokens for user"""
    
    # Encrypt tokens before storing
    encrypted_access = encrypt_token(access_token)
    encrypted_refresh = encrypt_token(refresh_token)
    
    reddit_connection = {
        "user_id": user_id,
        "platform": "reddit",
        "reddit_username": reddit_user["name"],
        "reddit_user_id": reddit_user["id"],
        "access_token": encrypted_access,
        "refresh_token": encrypted_refresh,
        "created_at": datetime.now(),
        "last_used": datetime.now(),
        "is_active": True,
        "permissions": ["read", "submit", "edit", "vote"]
    }
    
    # Upsert to database
    await database.reddit_credentials.replace_one(
        {"user_id": user_id},
        reddit_connection,
        upsert=True
    )
```

---

## Step 5: Multi-User Content Posting

### 5.1 Domain-Based Content Generation
```python
@app.post("/api/reddit/auto-post")
async def auto_post_reddit_content(
    domain_request: dict,
    current_user: Dict = Depends(get_current_user)
):
    """Auto-post content based on user's domain/business type"""
    
    # Get user's Reddit credentials
    reddit_creds = await get_user_reddit_credentials(current_user["id"])
    if not reddit_creds:
        return {"success": False, "error": "Reddit not connected"}
    
    # Generate domain-specific content
    content = await generate_domain_content(
        domain=domain_request["domain"],  # "education", "restaurant", "tech"
        business_type=domain_request["business_type"],
        target_audience=domain_request["audience"],
        language=domain_request.get("language", "en")
    )
    
    # Post to appropriate subreddits
    subreddits = get_domain_subreddits(domain_request["domain"])
    
    results = []
    for subreddit in subreddits:
        result = await post_to_reddit_with_user_token(
            reddit_creds["access_token"],
            subreddit,
            content["title"],
            content["body"]
        )
        results.append(result)
    
    return {"success": True, "posts": results}
```

### 5.2 Auto-Reply to Questions
```python
@app.post("/api/reddit/auto-reply")
async def auto_reply_questions(
    reply_config: dict,
    current_user: Dict = Depends(get_current_user)
):
    """Monitor and auto-reply to Reddit questions in user's domain"""
    
    # Get user's domain expertise
    user_profile = await get_user_profile(current_user["id"])
    expertise_domains = user_profile["expertise_domains"]  # ["education", "tech"]
    
    # Monitor relevant subreddits
    questions = await monitor_reddit_questions(
        domains=expertise_domains,
        language=reply_config.get("language", "en")
    )
    
    # Generate and post replies
    replies_posted = []
    for question in questions[:5]:  # Limit to 5 per run
        
        # Generate domain-specific answer
        answer = await generate_domain_answer(
            question=question["title"] + " " + question["content"],
            domain=expertise_domains[0],
            user_expertise=user_profile["expertise_level"],
            language=reply_config.get("language", "en")
        )
        
        # Post reply using user's token
        reddit_creds = await get_user_reddit_credentials(current_user["id"])
        reply_result = await reply_to_reddit_post(
            reddit_creds["access_token"],
            question["post_id"],
            answer
        )
        
        if reply_result["success"]:
            replies_posted.append({
                "question_id": question["post_id"],
                "subreddit": question["subreddit"],
                "answer_preview": answer[:100]
            })
    
    return {
        "success": True,
        "replies_posted": len(replies_posted),
        "details": replies_posted
    }
```

---

## Step 6: Frontend User Flow

### 6.1 Connect Reddit Button
```javascript
// In your React/Streamlit frontend
async function connectReddit() {
    try {
        // Get OAuth authorization URL
        const response = await fetch('/api/oauth/reddit/authorize');
        const data = await response.json();
        
        // Redirect user to Reddit OAuth
        window.location.href = data.redirect_url;
        
    } catch (error) {
        console.error('Reddit connection failed:', error);
    }
}
```

### 6.2 Streamlit Implementation
```python
def reddit_connection_page():
    st.title("Connect Your Reddit Account")
    
    if st.button("Connect Reddit Account", type="primary"):
        # Get OAuth URL from backend
        response = make_api_request("/api/oauth/reddit/authorize")
        
        if response.get("success"):
            st.markdown(f"""
            **Step 1:** Click the link below to authorize with Reddit
            
            [Authorize Reddit Account]({response['redirect_url']})
            
            **Step 2:** After authorization, you'll be redirected back automatically
            """)
        else:
            st.error("Failed to initiate Reddit connection")
```

---

## Step 7: Domain-Specific Automation

### 7.1 Business Domain Configuration
```python
DOMAIN_CONFIGS = {
    "education": {
        "subreddits": ["india", "JEE", "NEET", "IndianStudents", "StudyTips"],
        "content_types": ["study_tips", "exam_guidance", "career_advice"],
        "keywords": ["JEE", "NEET", "study", "exam", "education", "college"]
    },
    "restaurant": {
        "subreddits": ["india", "bangalore", "mumbai", "delhi", "food"],
        "content_types": ["food_posts", "recipe_sharing", "restaurant_updates"],
        "keywords": ["food", "restaurant", "recipe", "cuisine", "delivery"]
    },
    "tech": {
        "subreddits": ["india", "bangalore", "developersIndia", "programming"],
        "content_types": ["tech_news", "tutorials", "job_posts"],
        "keywords": ["programming", "developer", "tech", "software", "coding"]
    },
    "health": {
        "subreddits": ["india", "fitness", "health", "mentalhealth"],
        "content_types": ["health_tips", "fitness_advice", "wellness"],
        "keywords": ["health", "fitness", "wellness", "exercise", "nutrition"]
    }
}
```

### 7.2 User Domain Setup
```python
@app.post("/api/user/setup-domain")
async def setup_user_domain(
    domain_config: dict,
    current_user: Dict = Depends(get_current_user)
):
    """Configure user's business domain for automation"""
    
    user_domain_config = {
        "user_id": current_user["id"],
        "primary_domain": domain_config["domain"],
        "business_type": domain_config["business_type"],
        "target_audience": domain_config["audience"],
        "content_language": domain_config["language"],
        "posting_frequency": domain_config["frequency"],
        "auto_reply_enabled": domain_config["auto_reply"],
        "subreddits": domain_config.get("custom_subreddits", [])
    }
    
    # Store configuration
    await database.user_domain_configs.replace_one(
        {"user_id": current_user["id"]},
        user_domain_config,
        upsert=True
    )
    
    return {"success": True, "message": "Domain configuration saved"}
```

---

## Step 8: Testing Multi-User Setup

### 8.1 Test User Registration
1. Register User A (Coaching Center Owner)
2. Register User B (Restaurant Owner)
3. Both connect their Reddit accounts
4. Configure different domains

### 8.2 Test Domain-Based Posting
1. User A posts education content to r/JEE
2. User B posts food content to r/bangalore
3. Verify posts appear under respective Reddit accounts

### 8.3 Test Auto-Reply
1. Monitor questions in education subreddits
2. User A's account auto-replies with study tips
3. Monitor food-related questions
4. User B's account auto-replies with restaurant recommendations

---

## Security Considerations

### 8.1 Token Security
- **Encrypt all tokens** before storing
- **Use HTTPS** in production
- **Rotate tokens** periodically
- **Implement token refresh** logic

### 8.2 Rate Limiting
- **Per-user rate limits** (not global)
- **Respect Reddit's API limits**
- **Implement exponential backoff**
- **Monitor for abuse**

### 8.3 Content Safety
- **Content moderation** before posting
- **Spam detection** algorithms
- **User content approval** workflows
- **Compliance with Reddit rules**

This OAuth web app setup allows multiple users to connect their Reddit accounts through your platform while maintaining security and enabling domain-specific automation.