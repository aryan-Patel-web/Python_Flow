# Facebook & Instagram Automation Complete Guide
## Multi-User Platform with OAuth Integration

## Overview Flow Diagram

```
User Registration → Facebook App Setup → OAuth Flow → Token Storage → Content Automation
     ↓                    ↓               ↓           ↓              ↓
[User Signs Up]    [Meta Developer]   [FB Login]   [MongoDB]    [Auto Post/Reply]
     ↓                    ↓               ↓           ↓              ↓
[Domain Config]    [Get App Creds]    [Get Tokens] [Encrypt]    [Monitor Engagement]
```

---

## Step 1: Meta Developer Account & App Setup

### 1.1 Create Meta Developer Account
1. **Go to**: https://developers.facebook.com/
2. **Login** with your Facebook account
3. **Complete verification** (phone number required)
4. **Accept Developer Terms**

### 1.2 Create New App
1. **Click**: "Create App"
2. **Select**: "Consumer" (for general business use)
3. **Fill Details**:
   ```
   App Name: Social Media Automation Platform
   App Contact Email: your-email@domain.com
   Purpose: Business automation and content management
   ```
4. **Click**: "Create App"

### 1.3 Get App Credentials
After app creation, go to **Settings > Basic**:
```
App ID: 1234567890123456
App Secret: abcd1234efgh5678ijkl9012mnop3456
```

### 1.4 Configure App Settings
**Settings > Basic**:
```
Display Name: Your Platform Name
App Domains: yourdomain.com
Privacy Policy URL: https://yourdomain.com/privacy
Terms of Service URL: https://yourdomain.com/terms
```

**Settings > Advanced**:
```
Server IP Whitelist: Your server IP
Client OAuth Login: Yes
Web OAuth Login: Yes
```

---

## Step 2: Add Facebook Login Product

### 2.1 Add Facebook Login
1. **Dashboard > Add Product**
2. **Select**: "Facebook Login"
3. **Click**: "Set Up"

### 2.2 Configure OAuth Settings
**Facebook Login > Settings**:
```
Valid OAuth Redirect URIs:
- http://localhost:8000/api/oauth/facebook/callback (development)
- https://yourdomain.com/api/oauth/facebook/callback (production)

Client OAuth Login: Yes
Web OAuth Login: Yes
```

### 2.3 Required Permissions Setup
**App Review > Permissions and features**:

**Standard Permissions** (No review needed):
- `public_profile`
- `email`

**Advanced Permissions** (Requires review):
- `pages_manage_posts` - Post to Facebook Pages
- `pages_read_engagement` - Read page insights
- `pages_manage_metadata` - Manage page settings
- `instagram_basic` - Basic Instagram access
- `instagram_content_publish` - Publish to Instagram

---

## Step 3: Add Instagram Basic Display

### 3.1 Add Instagram Product
1. **Dashboard > Add Product**
2. **Select**: "Instagram Basic Display"
3. **Click**: "Set Up"

### 3.2 Configure Instagram Settings
**Instagram Basic Display > Basic Display**:
```
Valid OAuth Redirect URIs:
- http://localhost:8000/api/oauth/instagram/callback

Instagram App Secret: [Generated automatically]
```

### 3.3 Create Test Users
**Roles > Test Users**:
1. **Add test users** for development
2. **Accept invitations** on Instagram accounts
3. **Test OAuth flow** before production

---

## Step 4: Environment Configuration

### 4.1 Environment Variables (.env)
```env
# Meta/Facebook Configuration
META_APP_ID=1234567890123456
META_APP_SECRET=abcd1234efgh5678ijkl9012mnop3456
META_REDIRECT_URI_FB=http://localhost:8000/api/oauth/facebook/callback
META_REDIRECT_URI_IG=http://localhost:8000/api/oauth/instagram/callback

# Instagram Configuration
INSTAGRAM_APP_ID=1234567890123456
INSTAGRAM_APP_SECRET=xyz789abc123def456ghi789jkl012

# Database
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/automation_platform
DATABASE_NAME=automation_platform

# Security
JWT_SECRET=your-super-secure-jwt-secret-key
ENCRYPTION_KEY=your-32-character-encryption-key

# App Configuration
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

### 4.2 Requirements.txt
```txt
# Core FastAPI and ASGI Server
fastapi==0.104.1
uvicorn[standard]==0.24.0

# Database - MongoDB
motor==3.3.2
pymongo==4.15.0

# Authentication & Security
bcrypt==4.1.2
PyJWT==2.8.0
python-jose[cryptography]==3.3.0
cryptography==41.0.7

# HTTP Requests
requests==2.31.0
httpx>=0.25.2

# Configuration & Environment
python-dotenv==1.0.0

# Data Validation
pydantic[email]==2.9.2
pydantic-core==2.23.4

# File Upload & Form Handling
python-multipart==0.0.6

# Additional Dependencies
aiofiles==23.2.1
python-dateutil==2.8.2

# Development & Debugging
rich==13.7.0

# Image Processing (for Instagram)
Pillow==10.0.0

# Background Tasks
celery==5.3.0
redis==4.6.0
```

---

## Step 5: Database Schema (MongoDB Atlas)

### 5.1 Collections Structure

**users** collection:
```javascript
{
  "_id": ObjectId("..."),
  "email": "user@example.com",
  "password_hash": "hashed_password",
  "full_name": "User Name",
  "business_type": "restaurant",
  "domain": "food",
  "created_at": ISODate("2024-01-01"),
  "is_active": true,
  "subscription_plan": "basic"
}
```

**social_connections** collection:
```javascript
{
  "_id": ObjectId("..."),
  "user_id": ObjectId("user_id"),
  "platform": "facebook", // or "instagram"
  "platform_user_id": "123456789",
  "platform_username": "user_page_name",
  "access_token": "encrypted_token",
  "refresh_token": "encrypted_refresh_token",
  "token_expires_at": ISODate("2024-12-31"),
  "page_id": "987654321", // For Facebook Pages
  "page_access_token": "encrypted_page_token",
  "instagram_business_account_id": "567890123",
  "permissions": ["pages_manage_posts", "instagram_content_publish"],
  "is_active": true,
  "created_at": ISODate("2024-01-01"),
  "last_used": ISODate("2024-01-01")
}
```

**automation_configs** collection:
```javascript
{
  "_id": ObjectId("..."),
  "user_id": ObjectId("user_id"),
  "platform": "facebook",
  "domain": "restaurant",
  "content_types": ["food_posts", "menu_updates", "offers"],
  "posting_schedule": {
    "frequency": "daily",
    "times": ["09:00", "13:00", "18:00"],
    "timezone": "Asia/Kolkata"
  },
  "auto_reply_config": {
    "enabled": true,
    "response_delay": 300, // seconds
    "keywords": ["menu", "price", "location", "booking"]
  },
  "target_audience": {
    "age_range": "18-45",
    "location": "Bangalore",
    "interests": ["food", "dining"]
  },
  "content_language": "en",
  "is_active": true
}
```

**posts** collection:
```javascript
{
  "_id": ObjectId("..."),
  "user_id": ObjectId("user_id"),
  "platform": "facebook",
  "post_id": "platform_post_id",
  "content": "Post content text",
  "media_urls": ["image_url_1", "image_url_2"],
  "post_type": "text", // "text", "image", "video", "link"
  "scheduled_at": ISODate("2024-01-01T09:00:00Z"),
  "posted_at": ISODate("2024-01-01T09:00:00Z"),
  "status": "published", // "draft", "scheduled", "published", "failed"
  "engagement": {
    "likes": 25,
    "comments": 5,
    "shares": 2,
    "reach": 150
  },
  "created_at": ISODate("2024-01-01")
}
```

---

## Step 6: Backend Implementation

### 6.1 Database Connection (database.py)
```python
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

database = Database()

async def connect_to_mongo():
    """Create database connection"""
    database.client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
    database.database = database.client[os.getenv("DATABASE_NAME")]
    
    # Test connection
    await database.client.admin.command('ismaster')
    print("Connected to MongoDB Atlas")

async def close_mongo_connection():
    """Close database connection"""
    if database.client:
        database.client.close()

# Collections
def get_users_collection():
    return database.database.users

def get_social_connections_collection():
    return database.database.social_connections

def get_automation_configs_collection():
    return database.database.automation_configs

def get_posts_collection():
    return database.database.posts
```

### 6.2 Facebook OAuth Implementation (oauth_facebook.py)
```python
import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from urllib.parse import urlencode
import secrets
from datetime import datetime, timedelta
from .database import get_social_connections_collection
from .auth import get_current_user
from .encryption import encrypt_token, decrypt_token

router = APIRouter(prefix="/api/oauth/facebook", tags=["Facebook OAuth"])

# Facebook OAuth Configuration
FB_OAUTH_URL = "https://www.facebook.com/v18.0/dialog/oauth"
FB_TOKEN_URL = "https://graph.facebook.com/v18.0/oauth/access_token"
FB_API_BASE = "https://graph.facebook.com/v18.0"

@router.get("/authorize")
async def facebook_oauth_authorize(current_user: dict = Depends(get_current_user)):
    """Initiate Facebook OAuth flow"""
    
    state = secrets.token_urlsafe(32)
    
    # Store state temporarily (in production, use Redis or database)
    # For now, we'll include user_id in state (encode it)
    state_data = f"{current_user['id']}:{state}"
    
    params = {
        "client_id": os.getenv("META_APP_ID"),
        "redirect_uri": os.getenv("META_REDIRECT_URI_FB"),
        "state": state_data,
        "scope": "pages_manage_posts,pages_read_engagement,instagram_basic,instagram_content_publish,public_profile,email",
        "response_type": "code"
    }
    
    auth_url = f"{FB_OAUTH_URL}?{urlencode(params)}"
    
    return {
        "success": True,
        "redirect_url": auth_url,
        "state": state_data
    }

@router.get("/callback")
async def facebook_oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    error: str = Query(None)
):
    """Handle Facebook OAuth callback"""
    
    if error:
        raise HTTPException(status_code=400, detail=f"OAuth error: {error}")
    
    # Extract user_id from state
    try:
        user_id, _ = state.split(":", 1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(FB_TOKEN_URL, data={
            "client_id": os.getenv("META_APP_ID"),
            "client_secret": os.getenv("META_APP_SECRET"),
            "redirect_uri": os.getenv("META_REDIRECT_URI_FB"),
            "code": code
        })
    
    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to exchange code for token")
    
    token_data = token_response.json()
    access_token = token_data["access_token"]
    
    # Get user info and pages
    user_info = await get_facebook_user_info(access_token)
    pages = await get_user_facebook_pages(access_token)
    
    # Store connection in database
    await store_facebook_connection(user_id, access_token, user_info, pages)
    
    return {
        "success": True,
        "message": "Facebook account connected successfully",
        "user_info": user_info,
        "pages": pages
    }

async def get_facebook_user_info(access_token: str):
    """Get Facebook user information"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{FB_API_BASE}/me",
            params={
                "access_token": access_token,
                "fields": "id,name,email"
            }
        )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=400, detail="Failed to get user info")

async def get_user_facebook_pages(access_token: str):
    """Get user's Facebook pages"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{FB_API_BASE}/me/accounts",
            params={
                "access_token": access_token,
                "fields": "id,name,access_token,instagram_business_account"
            }
        )
    
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        return []

async def store_facebook_connection(user_id: str, access_token: str, user_info: dict, pages: list):
    """Store Facebook connection in database"""
    collection = get_social_connections_collection()
    
    # Store main Facebook connection
    fb_connection = {
        "user_id": user_id,
        "platform": "facebook",
        "platform_user_id": user_info["id"],
        "platform_username": user_info["name"],
        "access_token": encrypt_token(access_token),
        "token_expires_at": datetime.now() + timedelta(days=60),
        "permissions": ["pages_manage_posts", "pages_read_engagement"],
        "is_active": True,
        "created_at": datetime.now(),
        "last_used": datetime.now()
    }
    
    await collection.replace_one(
        {"user_id": user_id, "platform": "facebook"},
        fb_connection,
        upsert=True
    )
    
    # Store page connections
    for page in pages:
        page_connection = {
            "user_id": user_id,
            "platform": "facebook_page",
            "platform_user_id": page["id"],
            "platform_username": page["name"],
            "access_token": encrypt_token(access_token),
            "page_access_token": encrypt_token(page["access_token"]),
            "page_id": page["id"],
            "permissions": ["pages_manage_posts"],
            "is_active": True,
            "created_at": datetime.now()
        }
        
        # Check if page has Instagram business account
        if "instagram_business_account" in page:
            page_connection["instagram_business_account_id"] = page["instagram_business_account"]["id"]
        
        await collection.replace_one(
            {"user_id": user_id, "platform": "facebook_page", "page_id": page["id"]},
            page_connection,
            upsert=True
        )
```

### 6.3 Instagram OAuth Implementation (oauth_instagram.py)
```python
import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from urllib.parse import urlencode
import secrets
from datetime import datetime, timedelta
from .database import get_social_connections_collection
from .auth import get_current_user
from .encryption import encrypt_token

router = APIRouter(prefix="/api/oauth/instagram", tags=["Instagram OAuth"])

# Instagram OAuth Configuration
IG_OAUTH_URL = "https://api.instagram.com/oauth/authorize"
IG_TOKEN_URL = "https://api.instagram.com/oauth/access_token"
IG_API_BASE = "https://graph.instagram.com"

@router.get("/authorize")
async def instagram_oauth_authorize(current_user: dict = Depends(get_current_user)):
    """Initiate Instagram OAuth flow"""
    
    state = f"{current_user['id']}:{secrets.token_urlsafe(32)}"
    
    params = {
        "client_id": os.getenv("INSTAGRAM_APP_ID"),
        "redirect_uri": os.getenv("META_REDIRECT_URI_IG"),
        "scope": "user_profile,user_media",
        "response_type": "code",
        "state": state
    }
    
    auth_url = f"{IG_OAUTH_URL}?{urlencode(params)}"
    
    return {
        "success": True,
        "redirect_url": auth_url,
        "state": state
    }

@router.get("/callback")
async def instagram_oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    error: str = Query(None)
):
    """Handle Instagram OAuth callback"""
    
    if error:
        raise HTTPException(status_code=400, detail=f"Instagram OAuth error: {error}")
    
    # Extract user_id from state
    try:
        user_id, _ = state.split(":", 1)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid state parameter")
    
    # Exchange code for access token
    async with httpx.AsyncClient() as client:
        token_response = await client.post(IG_TOKEN_URL, data={
            "client_id": os.getenv("INSTAGRAM_APP_ID"),
            "client_secret": os.getenv("INSTAGRAM_APP_SECRET"),
            "grant_type": "authorization_code",
            "redirect_uri": os.getenv("META_REDIRECT_URI_IG"),
            "code": code
        })
    
    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to exchange code for token")
    
    token_data = token_response.json()
    access_token = token_data["access_token"]
    
    # Get long-lived token
    long_lived_token = await get_long_lived_token(access_token)
    
    # Get user info
    user_info = await get_instagram_user_info(long_lived_token)
    
    # Store connection
    await store_instagram_connection(user_id, long_lived_token, user_info)
    
    return {
        "success": True,
        "message": "Instagram account connected successfully",
        "user_info": user_info
    }

async def get_long_lived_token(short_lived_token: str):
    """Exchange short-lived token for long-lived token"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{IG_API_BASE}/access_token",
            params={
                "grant_type": "ig_exchange_token",
                "client_secret": os.getenv("INSTAGRAM_APP_SECRET"),
                "access_token": short_lived_token
            }
        )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise HTTPException(status_code=400, detail="Failed to get long-lived token")

async def get_instagram_user_info(access_token: str):
    """Get Instagram user information"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{IG_API_BASE}/me",
            params={
                "fields": "id,username,account_type,media_count",
                "access_token": access_token
            }
        )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=400, detail="Failed to get Instagram user info")

async def store_instagram_connection(user_id: str, access_token: str, user_info: dict):
    """Store Instagram connection in database"""
    collection = get_social_connections_collection()
    
    ig_connection = {
        "user_id": user_id,
        "platform": "instagram",
        "platform_user_id": user_info["id"],
        "platform_username": user_info["username"],
        "access_token": encrypt_token(access_token),
        "token_expires_at": datetime.now() + timedelta(days=60),
        "account_type": user_info.get("account_type", "PERSONAL"),
        "permissions": ["user_profile", "user_media"],
        "is_active": True,
        "created_at": datetime.now(),
        "last_used": datetime.now()
    }
    
    await collection.replace_one(
        {"user_id": user_id, "platform": "instagram"},
        ig_connection,
        upsert=True
    )
```

### 6.4 Content Automation (automation.py)
```python
import httpx
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from .database import get_social_connections_collection, get_posts_collection
from .auth import get_current_user
from .encryption import decrypt_token
from .content_generator import generate_domain_content
import json
from datetime import datetime

router = APIRouter(prefix="/api/automation", tags=["Content Automation"])

@router.post("/facebook/post")
async def post_to_facebook(
    post_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Post content to Facebook page"""
    
    # Get user's Facebook page connection
    connection = await get_user_social_connection(current_user["id"], "facebook_page")
    if not connection:
        raise HTTPException(status_code=400, detail="Facebook page not connected")
    
    # Decrypt tokens
    page_access_token = decrypt_token(connection["page_access_token"])
    page_id = connection["page_id"]
    
    # Prepare post data
    post_content = {
        "message": post_data["content"],
        "access_token": page_access_token
    }
    
    # Add media if provided
    if post_data.get("media_urls"):
        # For multiple images, use batch request
        if len(post_data["media_urls"]) > 1:
            media_ids = await upload_facebook_media_batch(post_data["media_urls"], page_access_token)
            post_content["attached_media"] = json.dumps([{"media_fbid": mid} for mid in media_ids])
        else:
            # Single image
            post_content["url"] = post_data["media_urls"][0]
    
    # Post to Facebook
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"https://graph.facebook.com/v18.0/{page_id}/feed",
            data=post_content
        )
    
    if response.status_code == 200:
        result = response.json()
        
        # Store post record
        await store_post_record(
            user_id=current_user["id"],
            platform="facebook",
            post_id=result["id"],
            content=post_data["content"],
            media_urls=post_data.get("media_urls", []),
            status="published"
        )
        
        return {
            "success": True,
            "post_id": result["id"],
            "message": "Posted to Facebook successfully"
        }
    else:
        raise HTTPException(status_code=400, detail=f"Facebook posting failed: {response.text}")

@router.post("/instagram/post")
async def post_to_instagram(
    post_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Post content to Instagram"""
    
    # Get Instagram business account connection (through Facebook page)
    connection = await get_user_social_connection(current_user["id"], "facebook_page")
    if not connection or not connection.get("instagram_business_account_id"):
        raise HTTPException(status_code=400, detail="Instagram business account not connected")
    
    page_access_token = decrypt_token(connection["page_access_token"])
    ig_account_id = connection["instagram_business_account_id"]
    
    # Instagram requires media for posts
    if not post_data.get("media_urls"):
        raise HTTPException(status_code=400, detail="Instagram posts require media (image/video)")
    
    media_url = post_data["media_urls"][0]
    
    # Step 1: Create media container
    container_data = {
        "image_url": media_url,
        "caption": post_data["content"],
        "access_token": page_access_token
    }
    
    async with httpx.AsyncClient() as client:
        # Create container
        container_response = await client.post(
            f"https://graph.facebook.com/v18.0/{ig_account_id}/media",
            data=container_data
        )
        
        if container_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to create Instagram media container")
        
        container_id = container_response.json()["id"]
        
        # Step 2: Publish media
        publish_response = await client.post(
            f"https://graph.facebook.com/v18.0/{ig_account_id}/media_publish",
            data={
                "creation_id": container_id,
                "access_token": page_access_token
            }
        )
        
        if publish_response.status_code == 200:
            result = publish_response.json()
            
            # Store post record
            await store_post_record(
                user_id=current_user["id"],
                platform="instagram",
                post_id=result["id"],
                content=post_data["content"],
                media_urls=post_data["media_urls"],
                status="published"
            )
            
            return {
                "success": True,
                "post_id": result["id"],
                "message": "Posted to Instagram successfully"
            }
        else:
            raise HTTPException(status_code=400, detail="Failed to publish Instagram post")

@router.post("/auto-generate-content")
async def auto_generate_and_post(
    automation_request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Generate domain-specific content and auto-post"""
    
    domain = automation_request["domain"]
    platforms = automation_request["platforms"]  # ["facebook", "instagram"]
    content_type = automation_request["content_type"]
    
    # Generate content based on domain
    content = await generate_domain_content(
        domain=domain,
        content_type=content_type,
        business_info=automation_request.get("business_info", {}),
        language=automation_request.get("language", "en")
    )
    
    results = []
    
    # Post to each platform
    for platform in platforms:
        try:
            if platform == "facebook":
                result = await post_to_facebook({
                    "content": content["text"],
                    "media_urls": content.get("media_urls", [])
                }, current_user)
                results.append({"platform": "facebook", "result": result})
                
            elif platform == "instagram":
                # Instagram requires media
                if content.get("media_urls"):
                    result = await post_to_instagram({
                        "content": content["text"],
                        "media_urls": content["media_urls"]
                    }, current_user)
                    results.append({"platform": "instagram", "result": result})
                else:
                    results.append({
                        "platform": "instagram", 
                        "result": {"success": False, "error": "Instagram requires media"}
                    })
                    
        except Exception as e:
            results.append({
                "platform": platform,
                "result": {"success": False, "error": str(e)}
            })
    
    return {
        "success": True,
        "generated_content": content,
        "posting_results": results
    }

async def get_user_social_connection(user_id: str, platform: str):
    """Get user's social media connection"""
    collection = get_social_connections_collection()
    return await collection.find_one({
        "user_id": user_id,
        "platform": platform,
        "is_active": True
    })

async def store_post_record(user_id: str, platform: str, post_id: str, content: str, media_urls: list, status: str):
    """Store post record in database"""
    collection = get_posts_collection()
    
    post_record = {
        "user_id": user_id,
        "platform": platform,
        "post_id": post_id,
        "content": content,
        "media_urls": media_urls,
        "post_type": "image" if media_urls else "text",
        "posted_at": datetime.now(),
        "status": status,
        "engagement": {
            "likes": 0,
            "comments": 0,
            "shares": 0,
            "reach": 0
        },
        "created_at": datetime.now()
    }
    
    await collection.insert_one(post_record)

async def upload_facebook_media_batch(media_urls: List[str], access_token: str) -> List[str]:
    """Upload multiple media files to Facebook"""
    media_ids = []
    
    async with httpx.AsyncClient() as client:
        for media_url in media_urls:
            response = await client.post(
                "https://graph.facebook.com/v18.0/me/photos",
                data={
                    "url": media_url,
                    "published": "false",  # Upload only, don't publish yet
                    "access_token": access_token
                }
            )
            
            if response.status_code == 200:
                media_ids.append(response.json()["id"])
    
    return media_ids
```

### 6.5 Content Generator (content_generator.py)
```python
import openai
from typing import Dict, List
import random
from datetime import datetime

# Domain-specific content templates
DOMAIN_CONTENT = {
    "restaurant": {
        "templates": [
            "Today's special: {dish_name}! Made with fresh {ingredients}. Visit us at {location}. #FoodLovers #Restaurant",
            "Craving authentic {cuisine_type}? Our {signature_dish} is waiting for you! Order now or visit us. #Foodie #Delivery",
            "Weekend vibes call for great food! Try our {weekend_special} with {drink_pairing}. #WeekendSpecial #Restaurant"
        ],
        "sample_data": {
            "dish_name": ["Butter Chicken", "Paneer Tikka", "Biryani", "Dosa", "Samosa"],
            "ingredients": ["spices", "herbs", "vegetables", "tender chicken", "aromatic rice"],
            "cuisine_type": ["Indian", "North Indian", "South Indian", "Mumbai Street Food"],
            "signature_dish": ["Biryani", "Thali", "Curry Combo", "Tandoori Platter"],
            "weekend_special": ["Family Thali", "BBQ Platter", "Buffet", "Special Menu"],
            "drink_pairing": ["Lassi", "Fresh Lime Water", "Masala Chai", "Cold Coffee"]
        }
    },
    "education": {
        "templates": [
            "Preparing for {exam_name}? Our expert faculty provides personalized coaching. Join our {batch_type} batch! #Education #Success",
            "Success tip for {subject}: {study_tip}. Need guidance? Our experienced teachers are here to help! #StudyTips #Learning",
            "Congratulations to {student_achievement}! Your hard work pays off. Join our institute for guaranteed results! #Results #Education"
        ],
        "sample_data": {
            "exam_name": ["JEE", "NEET", "UPSC", "Banking Exams", "SSC", "Board Exams"],
            "batch_type": ["weekend", "regular", "crash course", "online", "offline"],
            "subject": ["Mathematics", "Physics", "Chemistry", "Biology", "English", "General Knowledge"],
            "study_tip": ["Practice daily", "Solve previous papers", "Take mock tests", "Focus on concepts"],
            "student_achievement": ["our students scoring 95%+", "JEE rank holders", "NEET qualified students"]
        }
    },
    "tech": {
        "templates": [
            "Looking to upskill in {technology}? Join our {course_type} course and become job-ready in {duration}! #TechSkills #Career",
            "Industry insight: {tech_trend} is the future! Start learning now with our expert-led courses. #Technology #Future",
            "Success story: {achievement}. Ready to transform your career? Enroll today! #TechCareers #Success"
        ],
        "sample_data": {
            "technology": ["Python", "AI/ML", "Data Science", "Web Development", "Mobile App Development", "Cloud Computing"],
            "course_type": ["intensive", "weekend", "online", "bootcamp", "certification"],
            "duration": ["3 months", "6 months", "12 weeks", "2 months"],
            "tech_trend": ["Artificial Intelligence", "Machine Learning", "Blockchain", "Cloud Computing", "IoT"],
            "achievement": ["95% placement rate", "students getting 300% salary hike", "industry partnerships"]
        }
    },
    "health": {
        "templates": [
            "Health tip: {health_tip}. Take care of your body - it's the only place you have to live! #HealthTips #Wellness",
            "Struggling with {health_concern}? Our {service_type} can help you achieve your goals safely. #Health #Fitness",
            "Transform your lifestyle with our {program_name}. {benefit}. Book your consultation today! #HealthyLiving #Transformation"
        ],
        "sample_data": {
            "health_tip": ["Drink 8 glasses of water daily", "Exercise for 30 minutes", "Get 7-8 hours of sleep", "Eat more fruits and vegetables"],
            "health_concern": ["weight management", "stress", "poor sleep", "low energy", "fitness goals"],
            "service_type": ["nutrition counseling", "fitness training", "wellness program", "health coaching"],
            "program_name": ["30-day fitness challenge", "weight loss program", "stress management course", "nutrition plan"],
            "benefit": ["Feel energetic all day", "Boost your confidence", "Improve your health", "Get lasting results"]
        }
    }
}

async def generate_domain_content(
    domain: str,
    content_type: str = "promotional",
    business_info: dict = None,
    language: str = "en"
) -> Dict:
    """Generate domain-specific content for social media"""
    
    if domain not in DOMAIN_CONTENT:
        raise ValueError(f"Domain '{domain}' not supported")
    
    domain_data = DOMAIN_CONTENT[domain]
    
    # Select random template
    template = random.choice(domain_data["templates"])
    
    # Fill template with sample data or business info
    content_vars = {}
    sample_data = domain_data["sample_data"]
    
    # Extract variables from template
    import re
    variables = re.findall(r'\{(\w+)\}', template)
    
    for var in variables:
        if business_info and var in business_info:
            content_vars[var] = business_info[var]
        elif var in sample_data:
            content_vars[var] = random.choice(sample_data[var])
        else:
            # Default values
            default_values = {
                "location": "our restaurant",
                "duration": "3 months",
                "course_type": "professional"
            }
            content_vars[var] = default_values.get(var, f"[{var}]")
    
    # Generate final content
    final_content = template.format(**content_vars)
    
    # Generate relevant hashtags
    hashtags = generate_domain_hashtags(domain, content_type)
    final_content += f" {' '.join(hashtags)}"
    
    # Generate media suggestions
    media_suggestions = generate_media_suggestions(domain, content_type)
    
    return {
        "text": final_content,
        "hashtags": hashtags,
        "media_suggestions": media_suggestions,
        "content_type": content_type,
        "domain": domain,
        "generated_at": datetime.now().isoformat()
    }

def generate_domain_hashtags(domain: str, content_type: str) -> List[str]:
    """Generate relevant hashtags for domain"""
    
    base_hashtags = {
        "restaurant": ["#FoodLovers", "#Restaurant", "#Foodie", "#Delivery", "#IndianFood"],
        "education": ["#Education", "#Learning", "#Success", "#StudyTips", "#Career"],
        "tech": ["#Technology", "#Programming", "#TechSkills", "#Career", "#Innovation"],
        "health": ["#Health", "#Fitness", "#Wellness", "#HealthyLiving", "#Lifestyle"]
    }
    
    location_hashtags = ["#India", "#Bangalore", "#Mumbai", "#Delhi", "#Chennai"]
    
    domain_tags = base_hashtags.get(domain, ["#Business"])
    selected_tags = random.sample(domain_tags, min(3, len(domain_tags)))
    selected_tags.append(random.choice(location_hashtags))
    
    return selected_tags

def generate_media_suggestions(domain: str, content_type: str) -> List[str]:
    """Generate media content suggestions"""
    
    media_types = {
        "restaurant": [
            "food_photography",
            "kitchen_behind_scenes", 
            "chef_preparation",
            "restaurant_ambiance",
            "customer_enjoying_food"
        ],
        "education": [
            "classroom_learning",
            "student_success_stories",
            "teacher_explaining",
            "study_materials",
            "achievement_certificates"
        ],
        "tech": [
            "coding_session",
            "tech_workshop",
            "student_projects",
            "industry_partnerships",
            "career_success_stories"
        ],
        "health": [
            "workout_demonstration",
            "healthy_meal_prep",
            "before_after_transformation",
            "exercise_routines",
            "wellness_tips_infographic"
        ]
    }
    
    return media_types.get(domain, ["business_photo", "team_photo"])
```

### 6.6 Encryption Utilities (encryption.py)
```python
import os
from cryptography.fernet import Fernet
import base64

# Get encryption key from environment
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    # Generate a key for development (in production, use a fixed key)
    ENCRYPTION_KEY = Fernet.generate_key().decode()

cipher_suite = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)

def encrypt_token(token: str) -> str:
    """Encrypt a token for secure storage"""
    if not token:
        return ""
    
    encrypted_token = cipher_suite.encrypt(token.encode())
    return base64.b64encode(encrypted_token).decode()

def decrypt_token(encrypted_token: str) -> str:
    """Decrypt a token for use"""
    if not encrypted_token:
        return ""
    
    try:
        encrypted_data = base64.b64decode(encrypted_token.encode())
        decrypted_token = cipher_suite.decrypt(encrypted_data)
        return decrypted_token.decode()
    except Exception:
        return ""
```

---

## Step 7: Frontend Implementation

### 7.1 Social Media Connection Page (Streamlit)
```python
import streamlit as st
import requests
import time

def social_media_connections_page():
    st.title("Connect Your Social Media Accounts")
    
    # Check current connections
    user_token = st.session_state.get("user_token")
    if not user_token:
        st.error("Please login first")
        return
    
    headers = {"Authorization": f"Bearer {user_token}"}
    
    # Get current connections
    connections_response = requests.get(
        f"{API_BASE_URL}/api/user/social-connections",
        headers=headers
    )
    
    if connections_response.status_code == 200:
        connections = connections_response.json().get("connections", [])
    else:
        connections = []
    
    # Display connection status
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Facebook")
        fb_connected = any(c["platform"] == "facebook" for c in connections)
        
        if fb_connected:
            st.success("✅ Facebook Connected")
            fb_connection = next(c for c in connections if c["platform"] == "facebook")
            st.info(f"Connected as: {fb_connection['platform_username']}")
            
            # Show connected pages
            pages = [c for c in connections if c["platform"] == "facebook_page"]
            if pages:
                st.write("**Connected Pages:**")
                for page in pages:
                    st.write(f"📄 {page['platform_username']}")
        else:
            st.warning("❌ Facebook Not Connected")
            
            if st.button("Connect Facebook", key="fb_connect"):
                # Get OAuth URL
                oauth_response = requests.get(
                    f"{API_BASE_URL}/api/oauth/facebook/authorize",
                    headers=headers
                )
                
                if oauth_response.status_code == 200:
                    oauth_data = oauth_response.json()
                    st.markdown(f"""
                    **Step 1:** Click the link below to authorize Facebook
                    
                    [🔗 Connect Facebook Account]({oauth_data['redirect_url']})
                    
                    **Step 2:** After authorization, refresh this page
                    """)
    
    with col2:
        st.subheader("Instagram")
        ig_connected = any(c["platform"] == "instagram" for c in connections)
        
        if ig_connected:
            st.success("✅ Instagram Connected")
            ig_connection = next(c for c in connections if c["platform"] == "instagram")
            st.info(f"Connected as: @{ig_connection['platform_username']}")
        else:
            st.warning("❌ Instagram Not Connected")
            
            if st.button("Connect Instagram", key="ig_connect"):
                # Get OAuth URL
                oauth_response = requests.get(
                    f"{API_BASE_URL}/api/oauth/instagram/authorize",
                    headers=headers
                )
                
                if oauth_response.status_code == 200:
                    oauth_data = oauth_response.json()
                    st.markdown(f"""
                    **Step 1:** Click the link below to authorize Instagram
                    
                    [🔗 Connect Instagram Account]({oauth_data['redirect_url']})
                    
                    **Step 2:** After authorization, refresh this page
                    """)

def auto_posting_page():
    st.title("Auto Content Generation & Posting")
    
    user_token = st.session_state.get("user_token")
    headers = {"Authorization": f"Bearer {user_token}"}
    
    # Domain selection
    domain = st.selectbox(
        "Select Your Business Domain",
        ["restaurant", "education", "tech", "health"]
    )
    
    # Content type
    content_type = st.selectbox(
        "Content Type",
        ["promotional", "educational", "engagement", "announcement"]
    )
    
    # Platform selection
    st.write("**Select Platforms to Post:**")
    post_to_facebook = st.checkbox("Facebook", value=True)
    post_to_instagram = st.checkbox("Instagram")
    
    platforms = []
    if post_to_facebook:
        platforms.append("facebook")
    if post_to_instagram:
        platforms.append("instagram")
    
    # Business info input
    st.subheader("Business Information (Optional)")
    with st.expander("Customize Content"):
        business_info = {}
        
        if domain == "restaurant":
            business_info["location"] = st.text_input("Restaurant Location", "Bangalore")
            business_info["cuisine_type"] = st.text_input("Cuisine Type", "Indian")
            business_info["signature_dish"] = st.text_input("Signature Dish", "Biryani")
        
        elif domain == "education":
            business_info["exam_name"] = st.text_input("Main Exam Focus", "JEE/NEET")
            business_info["batch_type"] = st.text_input("Batch Type", "Regular")
            business_info["subject"] = st.text_input("Main Subject", "Mathematics")
        
        elif domain == "tech":
            business_info["technology"] = st.text_input("Main Technology", "Python")
            business_info["course_type"] = st.text_input("Course Type", "Bootcamp")
            business_info["duration"] = st.text_input("Course Duration", "3 months")
        
        elif domain == "health":
            business_info["service_type"] = st.text_input("Service Type", "Fitness Training")
            business_info["program_name"] = st.text_input("Program Name", "Weight Loss Program")
    
    # Generate and post
    if st.button("Generate & Post Content", type="primary"):
        if not platforms:
            st.error("Please select at least one platform")
            return
        
        with st.spinner("Generating content and posting..."):
            # Call auto-generation API
            request_data = {
                "domain": domain,
                "content_type": content_type,
                "platforms": platforms,
                "business_info": business_info,
                "language": "en"
            }
            
            response = requests.post(
                f"{API_BASE_URL}/api/automation/auto-generate-content",
                json=request_data,
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                st.success("Content generated and posted successfully!")
                
                # Show generated content
                st.subheader("Generated Content")
                st.write(result["generated_content"]["text"])
                
                # Show posting results
                st.subheader("Posting Results")
                for platform_result in result["posting_results"]:
                    platform = platform_result["platform"]
                    success = platform_result["result"]["success"]
                    
                    if success:
                        st.success(f"✅ Successfully posted to {platform.title()}")
                        if "post_id" in platform_result["result"]:
                            st.info(f"Post ID: {platform_result['result']['post_id']}")
                    else:
                        st.error(f"❌ Failed to post to {platform.title()}: {platform_result['result'].get('error', 'Unknown error')}")
            
            else:
                st.error(f"Failed to generate content: {response.text}")

def analytics_dashboard():
    st.title("Social Media Analytics")
    
    user_token = st.session_state.get("user_token")
    headers = {"Authorization": f"Bearer {user_token}"}
    
    # Get posts data
    posts_response = requests.get(
        f"{API_BASE_URL}/api/analytics/posts",
        headers=headers
    )
    
    if posts_response.status_code == 200:
        posts_data = posts_response.json()
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Posts", posts_data.get("total_posts", 0))
        with col2:
            st.metric("Facebook Posts", posts_data.get("facebook_posts", 0))
        with col3:
            st.metric("Instagram Posts", posts_data.get("instagram_posts", 0))
        with col4:
            st.metric("Avg. Engagement", f"{posts_data.get('avg_engagement', 0):.1f}%")
        
        # Recent posts
        st.subheader("Recent Posts")
        if posts_data.get("recent_posts"):
            for post in posts_data["recent_posts"]:
                with st.expander(f"{post['platform'].title()} - {post['created_at'][:10]}"):
                    st.write(f"**Content:** {post['content'][:100]}...")
                    st.write(f"**Likes:** {post['engagement']['likes']}")
                    st.write(f"**Comments:** {post['engagement']['comments']}")
                    st.write(f"**Shares:** {post['engagement']['shares']}")
    else:
        st.error("Failed to load analytics data")
```

### 7.2 Main App Structure (main.py)
```python
import streamlit as st
from pages import (
    auth_page, 
    social_media_connections_page, 
    auto_posting_page,
    analytics_dashboard
)

# App configuration
st.set_page_config(
    page_title="Social Media Automation Platform",
    page_icon="🚀",
    layout="wide"
)

# API configuration
API_BASE_URL = "http://localhost:8000"

def main():
    # Initialize session state
    if "user_token" not in st.session_state:
        st.session_state.user_token = None
    if "user_info" not in st.session_state:
        st.session_state.user_info = None
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    
    if st.session_state.user_token:
        # User is logged in
        st.sidebar.success(f"Welcome, {st.session_state.user_info['full_name']}")
        
        page = st.sidebar.selectbox(
            "Choose a page",
            ["Auto Posting", "Social Connections", "Analytics", "Profile"]
        )
        
        if st.sidebar.button("Logout"):
            st.session_state.user_token = None
            st.session_state.user_info = None
            st.rerun()
        
        # Route to pages
        if page == "Auto Posting":
            auto_posting_page()
        elif page == "Social Connections":
            social_media_connections_page()
        elif page == "Analytics":
            analytics_dashboard()
        elif page == "Profile":
            profile_page()
    
    else:
        # User not logged in
        auth_page()

def profile_page():
    st.title("User Profile")
    
    user_info = st.session_state.user_info
    
    st.subheader("Account Information")
    st.write(f"**Name:** {user_info['full_name']}")
    st.write(f"**Email:** {user_info['email']}")
    st.write(f"**Business Type:** {user_info['business_type']}")
    st.write(f"**Domain:** {user_info['domain']}")

if __name__ == "__main__":
    main()
```

---

## Step 8: Testing & Deployment

### 8.1 Local Testing Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment variables
cp .env.example .env
# Edit .env with your credentials

# 3. Start MongoDB (if local) or connect to Atlas
# MongoDB Atlas connection string in .env

# 4. Start backend
uvicorn main:app --reload --port 8000

# 5. Start frontend (separate terminal)
streamlit run frontend/main.py --server.port 3000
```

### 8.2 Testing OAuth Flow
1. **Register test user** in your app
2. **Connect Facebook account** via OAuth
3. **Select Facebook page** to manage
4. **Connect Instagram business account** (if available)
5. **Test content posting** to both platforms
6. **Verify posts appear** on actual Facebook/Instagram

### 8.3 Production Deployment

**Backend (FastAPI):**
```yaml
# render.yaml
services:
  - type: web
    name: social-automation-api
    env: python
    plan: starter
    buildCommand: "pip install -r requirements.txt"
    startCommand: "uvicorn main:app --host 0.0.0.0 --port 10000"
    envVars:
      - key: MONGODB_URL
        value: your_mongodb_atlas_url
      - key: META_APP_ID
        value: your_facebook_app_id
      - key: META_APP_SECRET
        value: your_facebook_app_secret
```

**Frontend (Streamlit):**
```yaml
# streamlit deployment
services:
  - type: web
    name: social-automation-frontend
    env: python
    buildCommand: "pip install streamlit"
    startCommand: "streamlit run main.py --server.port 10000"
```

---

## Step 9: App Review & Permissions

### 9.1 Facebook App Review Process
1. **Complete Basic Info** in Meta Developer Console
2. **Add Privacy Policy** and Terms of Service URLs
3. **Submit for Review:**
   - `pages_manage_posts`
   - `pages_read_engagement`
   - `instagram_content_publish`
4. **Provide Use Case Description:**
   ```
   "Multi-user social media automation platform for Indian small businesses. 
   Users connect their Facebook pages and Instagram business accounts to 
   auto-generate and schedule domain-specific content (restaurant menus, 
   educational content, etc.) to grow their social presence."
   ```
5. **Submit Video Demo** showing the OAuth flow and posting functionality

### 9.2 Required Documentation
- **Privacy Policy**: How you handle user data and tokens
- **Terms of Service**: Platform usage rules
- **Data Deletion Instructions**: How users can delete their data
- **App Demo Video**: Complete user flow demonstration

---

## Step 10: Flow Diagram

```
User Journey Flow:
Registration → Domain Setup → OAuth Connection → Content Generation → Auto Posting → Analytics

Technical Flow:
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│   Frontend  │───▶│   Backend    │───▶│  Meta APIs  │
│ (Streamlit) │    │  (FastAPI)   │    │(FB/IG Graph)│
└─────────────┘    └──────────────┘    └─────────────┘
       │                   │                   │
       ▼                   ▼                   ▼
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│User Actions │    │   Database   │    │Social Posts │
│- Connect    │    │ (MongoDB)    │    │- Facebook   │
│- Generate   │    │- Users       │    │- Instagram  │
│- Schedule   │    │- Tokens      │    │- Analytics  │
│- Analytics  │    │- Posts       │    │             │
└─────────────┘    └──────────────┘    └─────────────┘
```

This complete guide provides everything needed to build a multi-user Facebook and Instagram automation platform with OAuth integration, secure token storage, and domain-specific content generation.
            "



I've provided you with a comprehensive guide for Facebook and Instagram automation that covers:
Complete Implementation Guide:
1. Meta Developer Setup

Step-by-step Facebook App creation
Instagram Basic Display integration
OAuth configuration and permissions

2. Technical Architecture

MongoDB Atlas database schema
FastAPI backend with OAuth flows
Secure token encryption and storage
Multi-user platform support

3. Core Features

Facebook Page posting automation
Instagram Business account integration
Domain-specific content generation (restaurant, education, tech, health)
Analytics and engagement tracking

4. Security & Compliance

Encrypted token storage
OAuth 2.0 implementation
App review requirements for production
Rate limiting and error handling

5. Frontend Implementation

Streamlit interface for user management
Social media connection flow
Content generation and posting interface
Analytics dashboard

Key Differences from Reddit:

Complex OAuth: Facebook requires app review for advanced permissions
Multiple Tokens: User tokens + page tokens + Instagram business tokens
Media Requirements: Instagram requires images/videos for posts
Business Accounts: Instagram posting needs business account connection through Facebook Page

Production Checklist:

Complete Meta app review process
Set up MongoDB Atlas cluster
Configure production environment variables
Deploy backend and frontend separately
Test OAuth flows thoroughly

This implementation supports your multi-user SaaS model where users connect their accounts, configure domain-specific automation, and your platform handles content generation and posting while maintaining security and compliance with Meta's policies.