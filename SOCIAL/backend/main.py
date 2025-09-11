"""
Main FastAPI Application for Multi-Platform Automation System
Production-ready with comprehensive error handling, authentication, and monitoring
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import uvicorn
import os
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
from contextlib import asynccontextmanager

# Import platform modules
from reddit import RedditConnector
from ai_service import AIService
from database import DatabaseManager
from auth import AuthManager
from config import get_settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global settings
settings = get_settings()

# Security
security = HTTPBearer()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events"""
    # Startup
    logger.info("Starting Multi-Platform Automation System...")
    
    # Initialize database connections
    app.state.db_manager = DatabaseManager()
    await app.state.db_manager.connect()
    
    # Initialize AI service
    app.state.ai_service = AIService()
    
    # Initialize platform connectors
    app.state.reddit_connector = RedditConnector({
        'REDDIT_CLIENT_ID': settings.reddit_client_id,
        'REDDIT_CLIENT_SECRET': settings.reddit_client_secret,
        'REDDIT_USER_AGENT': settings.reddit_user_agent,
        'REDDIT_USERNAME': settings.reddit_username,
        'REDDIT_PASSWORD': settings.reddit_password
    })
    
    # Initialize authentication manager
    app.state.auth_manager = AuthManager()
    
    logger.info("Application startup completed successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await app.state.db_manager.disconnect()
    logger.info("Application shutdown completed")


# Create FastAPI application
app = FastAPI(
    title="Multi-Platform Automation API",
    description="Production-ready automation platform for Reddit, Twitter, Stack Overflow, and WebMD",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.vercel.app"]
)


# Dependency for authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate JWT token and return current user"""
    try:
        payload = app.state.auth_manager.verify_token(credentials.credentials)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        # Get user from database
        user = await app.state.db_manager.get_user(user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for better error responses"""
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
            "timestamp": datetime.now().isoformat()
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Application health check endpoint"""
    try:
        # Check database connection
        db_status = await app.state.db_manager.health_check()
        
        # Check Reddit connection
        reddit_status = await app.state.reddit_connector.health_check()
        
        # Check AI service
        ai_status = app.state.ai_service.health_check()
        
        overall_status = (
            db_status.get("success", False) and 
            reddit_status.get("success", False) and 
            ai_status.get("success", False)
        )
        
        return {
            "success": True,
            "status": "healthy" if overall_status else "degraded",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "database": db_status,
                "reddit": reddit_status,
                "ai_service": ai_status
            },
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "success": False,
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
        )


# ===============================
# AUTHENTICATION ENDPOINTS
# ===============================

@app.post("/api/auth/register")
async def register_user(user_data: Dict[str, Any]):
    """Register new user"""
    try:
        result = await app.state.auth_manager.register_user(user_data)
        
        if result["success"]:
            # Create user profile in database
            await app.state.db_manager.create_user(result["user"])
            
        return result
        
    except Exception as e:
        logger.error(f"User registration failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/auth/login")
async def login_user(credentials: Dict[str, str]):
    """Authenticate user and return JWT token"""
    try:
        result = await app.state.auth_manager.authenticate_user(
            credentials["email"], 
            credentials["password"]
        )
        return result
        
    except Exception as e:
        logger.error(f"User login failed: {e}")
        raise HTTPException(status_code=401, detail="Invalid credentials")


@app.get("/api/auth/me")
async def get_current_user_info(current_user: Dict = Depends(get_current_user)):
    """Get current authenticated user information"""
    return {
        "success": True,
        "user": current_user,
        "message": "User information retrieved successfully"
    }


# ===============================
# REDDIT API ENDPOINTS
# ===============================

@app.post("/api/reddit/connect")
async def connect_reddit_account(
    credentials: Dict[str, str],
    current_user: Dict = Depends(get_current_user)
):
    """Connect user's Reddit account"""
    try:
        # Authenticate with Reddit
        result = await app.state.reddit_connector.authenticate_user()
        
        if result["success"]:
            # Store Reddit credentials for user
            await app.state.db_manager.store_platform_credentials(
                current_user["id"], 
                "reddit", 
                result["user_info"]
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Reddit connection failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/reddit/post")
async def post_to_reddit(
    post_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """Post content to Reddit"""
    try:
        result = await app.state.reddit_connector.post_content(
            subreddit_name=post_data["subreddit"],
            title=post_data["title"],
            content=post_data["content"],
            content_type=post_data.get("content_type", "text"),
            language=post_data.get("language", "en")
        )
        
        if result["success"]:
            # Log activity to database
            await app.state.db_manager.log_platform_activity(
                current_user["id"],
                "reddit",
                "post",
                result
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Reddit posting failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/reddit/questions")
async def get_reddit_questions(
    subreddits: Optional[str] = None,
    keywords: Optional[str] = None,
    limit: int = 10,
    current_user: Dict = Depends(get_current_user)
):
    """Monitor Reddit for questions and discussion opportunities"""
    try:
        subreddit_list = subreddits.split(",") if subreddits else None
        keyword_list = keywords.split(",") if keywords else None
        
        questions = await app.state.reddit_connector.monitor_questions(
            subreddits=subreddit_list,
            keywords=keyword_list,
            limit=limit
        )
        
        return {
            "success": True,
            "questions": [
                {
                    "id": q.id,
                    "title": q.title,
                    "content": q.content,
                    "subreddit": q.subreddit,
                    "score": q.score,
                    "num_comments": q.num_comments,
                    "created_utc": q.created_utc,
                    "url": q.url,
                    "author": q.author
                } for q in questions
            ],
            "count": len(questions),
            "message": f"Found {len(questions)} questions"
        }
        
    except Exception as e:
        logger.error(f"Reddit question monitoring failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/reddit/answer")
async def answer_reddit_question(
    answer_data: Dict[str, str],
    current_user: Dict = Depends(get_current_user)
):
    """Post answer to a Reddit question"""
    try:
        result = await app.state.reddit_connector.post_answer(
            post_id=answer_data["post_id"],
            answer=answer_data["answer"],
            language=answer_data.get("language", "en")
        )
        
        if result["success"]:
            # Log activity and potentially update earnings
            await app.state.db_manager.log_platform_activity(
                current_user["id"],
                "reddit",
                "answer",
                result
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Reddit answer posting failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/reddit/stats")
async def get_reddit_stats(
    current_user: Dict = Depends(get_current_user)
):
    """Get Reddit account statistics"""
    try:
        result = await app.state.reddit_connector.get_user_stats()
        return result
        
    except Exception as e:
        logger.error(f"Reddit stats retrieval failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/reddit/trending")
async def get_reddit_trending(
    subreddits: Optional[str] = None,
    current_user: Dict = Depends(get_current_user)
):
    """Get trending topics from Reddit"""
    try:
        subreddit_list = subreddits.split(",") if subreddits else None
        result = await app.state.reddit_connector.get_trending_topics(subreddit_list)
        return result
        
    except Exception as e:
        logger.error(f"Reddit trending retrieval failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ===============================
# AI CONTENT GENERATION ENDPOINTS
# ===============================

@app.post("/api/ai/generate-content")
async def generate_ai_content(
    content_request: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """Generate AI content for specific platform and purpose"""
    try:
        result = await app.state.ai_service.generate_platform_content(
            platform=content_request["platform"],
            content_type=content_request["content_type"],
            topic=content_request["topic"],
            tone=content_request.get("tone", "professional"),
            language=content_request.get("language", "en"),
            target_audience=content_request.get("target_audience", "general"),
            additional_context=content_request.get("additional_context", "")
        )
        
        # Log AI usage for billing/analytics
        await app.state.db_manager.log_ai_usage(
            current_user["id"],
            content_request["platform"],
            len(result.get("content", ""))
        )
        
        return result
        
    except Exception as e:
        logger.error(f"AI content generation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/ai/generate-answer")
async def generate_ai_answer(
    question_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """Generate AI answer for Q&A platforms"""
    try:
        result = await app.state.ai_service.generate_qa_answer(
            platform=question_data["platform"],
            question=question_data["question"],
            context=question_data.get("context", ""),
            language=question_data.get("language", "en"),
            expertise_level=question_data.get("expertise_level", "intermediate")
        )
        
        await app.state.db_manager.log_ai_usage(
            current_user["id"],
            question_data["platform"],
            len(result.get("answer", ""))
        )
        
        return result
        
    except Exception as e:
        logger.error(f"AI answer generation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ===============================
# VOICE PROCESSING ENDPOINTS
# ===============================

@app.post("/api/voice/speech-to-text")
async def speech_to_text(
    audio_data: Dict[str, Any],
    current_user: Dict = Depends(get_current_user)
):
    """Convert speech to text with language detection"""
    try:
        result = await app.state.ai_service.speech_to_text(
            audio_data["audio_base64"],
            language=audio_data.get("language", "auto")
        )
        return result
        
    except Exception as e:
        logger.error(f"Speech to text failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/voice/text-to-speech")
async def text_to_speech(
    text_data: Dict[str, str],
    current_user: Dict = Depends(get_current_user)
):
    """Convert text to speech with voice selection"""
    try:
        result = await app.state.ai_service.text_to_speech(
            text_data["text"],
            language=text_data.get("language", "en"),
            voice=text_data.get("voice", "default")
        )
        return result
        
    except Exception as e:
        logger.error(f"Text to speech failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ===============================
# ANALYTICS & DASHBOARD ENDPOINTS
# ===============================

@app.get("/api/analytics/dashboard")
async def get_user_dashboard(
    current_user: Dict = Depends(get_current_user)
):
    """Get comprehensive user dashboard analytics"""
    try:
        dashboard_data = await app.state.db_manager.get_user_dashboard(current_user["id"])
        return {
            "success": True,
            "dashboard": dashboard_data,
            "message": "Dashboard data retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Dashboard retrieval failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/analytics/platform-performance")
async def get_platform_performance(
    platform: str,
    days: int = 30,
    current_user: Dict = Depends(get_current_user)
):
    """Get platform-specific performance analytics"""
    try:
        performance_data = await app.state.db_manager.get_platform_performance(
            current_user["id"],
            platform,
            days
        )
        return {
            "success": True,
            "performance": performance_data,
            "platform": platform,
            "period_days": days,
            "message": f"Performance data for {platform} retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Platform performance retrieval failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ===============================
# AUTOMATION & SCHEDULING ENDPOINTS
# ===============================

@app.post("/api/automation/schedule-content")
async def schedule_content(
    schedule_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    current_user: Dict = Depends(get_current_user)
):
    """Schedule content posting across platforms"""
    try:
        # Store scheduled content in database
        schedule_id = await app.state.db_manager.create_scheduled_content(
            current_user["id"],
            schedule_data
        )
        
        # Add background task for execution
        background_tasks.add_task(
            execute_scheduled_content,
            schedule_id,
            schedule_data
        )
        
        return {
            "success": True,
            "schedule_id": schedule_id,
            "scheduled_for": schedule_data["scheduled_time"],
            "platforms": schedule_data["platforms"],
            "message": "Content scheduled successfully"
        }
        
    except Exception as e:
        logger.error(f"Content scheduling failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/automation/scheduled-content")
async def get_scheduled_content(
    current_user: Dict = Depends(get_current_user)
):
    """Get all scheduled content for user"""
    try:
        scheduled_content = await app.state.db_manager.get_scheduled_content(current_user["id"])
        return {
            "success": True,
            "scheduled_content": scheduled_content,
            "count": len(scheduled_content),
            "message": "Scheduled content retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"Scheduled content retrieval failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/automation/scheduled-content/{schedule_id}")
async def cancel_scheduled_content(
    schedule_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """Cancel scheduled content"""
    try:
        result = await app.state.db_manager.cancel_scheduled_content(
            schedule_id,
            current_user["id"]
        )
        return result
        
    except Exception as e:
        logger.error(f"Content cancellation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ===============================
# BACKGROUND TASKS
# ===============================

async def execute_scheduled_content(schedule_id: str, schedule_data: Dict[str, Any]):
    """Background task to execute scheduled content posting"""
    try:
        # Wait until scheduled time
        scheduled_time = datetime.fromisoformat(schedule_data["scheduled_time"])
        current_time = datetime.now()
        
        if scheduled_time > current_time:
            wait_seconds = (scheduled_time - current_time).total_seconds()
            await asyncio.sleep(wait_seconds)
        
        # Execute posting to each platform
        results = {}
        
        for platform in schedule_data["platforms"]:
            try:
                if platform == "reddit":
                    result = await app.state.reddit_connector.post_content(
                        subreddit_name=schedule_data["subreddit"],
                        title=schedule_data["title"],
                        content=schedule_data["content"],
                        language=schedule_data.get("language", "en")
                    )
                # Add other platforms here as implemented
                
                results[platform] = result
                
            except Exception as e:
                logger.error(f"Scheduled posting failed for {platform}: {e}")
                results[platform] = {"success": False, "error": str(e)}
        
        # Update database with results
        await app.state.db_manager.update_scheduled_content_results(schedule_id, results)
        
    except Exception as e:
        logger.error(f"Scheduled content execution failed: {e}")


# ===============================
# UTILITY ENDPOINTS
# ===============================

@app.post("/api/utils/language-detect")
async def detect_language(text_data: Dict[str, str]):
    """Detect language of input text"""
    try:
        result = app.state.ai_service.detect_language(text_data["text"])
        return result
        
    except Exception as e:
        logger.error(f"Language detection failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/utils/translate")
async def translate_text(
    translation_data: Dict[str, str],
    current_user: Dict = Depends(get_current_user)
):
    """Translate text between languages"""
    try:
        result = await app.state.ai_service.translate_text(
            translation_data["text"],
            source_language=translation_data.get("source_language", "auto"),
            target_language=translation_data["target_language"]
        )
        return result
        
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/utils/supported-languages")
async def get_supported_languages():
    """Get list of supported languages"""
    return {
        "success": True,
        "languages": {
            "en": "English",
            "hi": "Hindi",
            "ta": "Tamil",
            "te": "Telugu",
            "bn": "Bengali",
            "mr": "Marathi",
            "gu": "Gujarati",
            "kn": "Kannada",
            "ml": "Malayalam",
            "pa": "Punjabi",
            "or": "Odia",
            "as": "Assamese"
        },
        "message": "Supported languages retrieved successfully"
    }


# ===============================
# ADMIN ENDPOINTS
# ===============================

@app.get("/api/admin/system-stats")
async def get_system_stats(current_user: Dict = Depends(get_current_user)):
    """Get system-wide statistics (admin only)"""
    # Add admin check here
    if not current_user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        stats = await app.state.db_manager.get_system_stats()
        return {
            "success": True,
            "stats": stats,
            "message": "System statistics retrieved successfully"
        }
        
    except Exception as e:
        logger.error(f"System stats retrieval failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ===============================
# WEBSOCKET ENDPOINTS
# ===============================

from fastapi import WebSocket

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    try:
        while True:
            # Handle real-time communication
            data = await websocket.receive_text()
            # Process websocket data and send updates
            await websocket.send_text(f"Echo: {data}")
            
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()


# ===============================
# APPLICATION STARTUP
# ===============================

if __name__ == "__main__":
    # Development server configuration
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        workers=1 if settings.debug else settings.workers,
        log_level=settings.log_level.lower(),
        access_log=True,
        loop="asyncio"
    )