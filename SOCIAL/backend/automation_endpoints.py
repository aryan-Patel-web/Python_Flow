"""
API Endpoints for Reddit Automation Features
Add these endpoints to your main.py
"""

from fastapi import HTTPException, Query
from typing import Dict, List, Any
import logging
from datetime import datetime

from reddit_automation import (
    RedditAutomationScheduler, 
    AutoPostConfig, 
    AutoReplyConfig,
    RedditQuestionMonitor,
    RedditUserTargeting
)

logger = logging.getLogger(__name__)

# Global automation scheduler (initialize in main.py startup)
automation_scheduler = None
question_monitor = None
user_targeting = None

def initialize_automation(reddit_connector, ai_service, database, user_tokens):
    """Initialize automation components (call this in main.py startup)"""
    global automation_scheduler, question_monitor, user_targeting
    
    automation_scheduler = RedditAutomationScheduler(
        reddit_connector, ai_service, database, user_tokens
    )
    question_monitor = RedditQuestionMonitor(reddit_connector)
    user_targeting = RedditUserTargeting(reddit_connector)
    
    # Start the scheduler
    automation_scheduler.start_scheduler()
    
    logger.info("Reddit automation system initialized")

# Add these endpoints to your main.py

@app.post("/api/automation/setup-auto-posting")
async def setup_auto_posting(config_data: Dict[str, Any]):
    """Set up automatic posting for a user"""
    try:
        if not automation_scheduler:
            raise HTTPException(status_code=500, detail="Automation not initialized")
        
        # Create config from request data
        config = AutoPostConfig(
            user_id="dev_user_123",  # Fixed for development
            domain=config_data["domain"],
            business_type=config_data["business_type"],
            target_audience=config_data.get("target_audience", "indian_users"),
            language=config_data.get("language", "en"),
            subreddits=config_data["subreddits"],
            posts_per_day=config_data.get("posts_per_day", 3),
            posting_times=config_data.get("posting_times", ["09:00", "14:00", "19:00"]),
            content_style=config_data.get("content_style", "engaging")
        )
        
        result = await automation_scheduler.setup_auto_posting(config)
        return result
        
    except Exception as e:
        logger.error(f"Auto-posting setup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/automation/setup-auto-replies")
async def setup_auto_replies(config_data: Dict[str, Any]):
    """Set up automatic replies for a user"""
    try:
        if not automation_scheduler:
            raise HTTPException(status_code=500, detail="Automation not initialized")
        
        # Create config from request data
        config = AutoReplyConfig(
            user_id="dev_user_123",  # Fixed for development
            domain=config_data["domain"],
            expertise_level=config_data.get("expertise_level", "intermediate"),
            subreddits=config_data["subreddits"],
            keywords=config_data["keywords"],
            max_replies_per_hour=config_data.get("max_replies_per_hour", 2),
            response_delay_minutes=config_data.get("response_delay_minutes", 15)
        )
        
        result = await automation_scheduler.setup_auto_replies(config)
        return result
        
    except Exception as e:
        logger.error(f"Auto-reply setup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/automation/status")
async def get_automation_status():
    """Get current automation status"""
    try:
        if not automation_scheduler:
            return {
                "success": False,
                "error": "Automation not initialized"
            }
        
        result = await automation_scheduler.get_automation_status("dev_user_123")
        return result
        
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/automation/target-questions")
async def find_target_questions(
    domain: str = Query(...),
    subreddits: str = Query(None),
    expertise_keywords: str = Query(...),
    min_score: int = Query(1),
    max_age_hours: int = Query(24)
):
    """Find questions that are good targets for helpful replies"""
    try:
        if not question_monitor:
            raise HTTPException(status_code=500, detail="Question monitor not initialized")
        
        subreddit_list = subreddits.split(",") if subreddits else None
        keyword_list = expertise_keywords.split(",")
        
        questions = await question_monitor.find_target_questions(
            domain=domain,
            expertise_keywords=keyword_list,
            subreddits=subreddit_list,
            min_score=min_score,
            max_age_hours=max_age_hours
        )
        
        return {
            "success": True,
            "questions": questions,
            "count": len(questions),
            "message": f"Found {len(questions)} target questions in {domain} domain"
        }
        
    except Exception as e:
        logger.error(f"Target question search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/automation/active-users")
async def find_active_users(
    domain: str = Query(...),
    subreddits: str = Query(...),
    time_period_hours: int = Query(24)
):
    """Find users who frequently ask questions in your domain"""
    try:
        if not user_targeting:
            raise HTTPException(status_code=500, detail="User targeting not initialized")
        
        subreddit_list = subreddits.split(",")
        
        users = await user_targeting.find_users_asking_questions(
            domain=domain,
            subreddits=subreddit_list,
            time_period_hours=time_period_hours
        )
        
        return {
            "success": True,
            "active_users": users,
            "count": len(users),
            "message": f"Found {len(users)} active users in {domain} domain"
        }
        
    except Exception as e:
        logger.error(f"User targeting failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/automation/manual-reply")
async def manual_reply_to_question(reply_data: Dict[str, Any]):
    """Manually reply to a specific question with AI-generated answer"""
    try:
        user_id = "dev_user_123"
        
        # Check if user has Reddit tokens
        if user_id not in user_reddit_tokens:
            raise HTTPException(status_code=400, detail="Reddit account not connected")
        
        # Generate AI answer
        answer_result = await ai_service.generate_qa_answer(
            platform="reddit",
            question=reply_data["question"],
            context=reply_data.get("context", ""),
            language=reply_data.get("language", "en"),