"""
Reddit Automation System for Multi-Platform Content Management
Handles auto-posting, auto-replies, question monitoring, and user targeting
"""

import praw
import asyncio
import schedule
import time
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import json

logger = logging.getLogger(__name__)

@dataclass
class AutoPostConfig:
    """Configuration for automatic posting"""
    user_id: str
    domain: str
    business_type: str
    target_audience: str = "indian_users"
    language: str = "en"
    subreddits: List[str] = None
    posts_per_day: int = 3
    posting_times: List[str] = None
    content_style: str = "engaging"

@dataclass
class AutoReplyConfig:
    """Configuration for automatic replies"""
    user_id: str
    domain: str
    expertise_level: str = "intermediate"
    subreddits: List[str] = None
    keywords: List[str] = None
    max_replies_per_hour: int = 2
    response_delay_minutes: int = 15

class RedditAutomationScheduler:
    """Main automation scheduler for Reddit activities"""
    
    def __init__(self, reddit_oauth_connector, ai_service, database_manager, user_tokens):
        self.reddit_oauth = reddit_oauth_connector
        self.ai_service = ai_service
        self.database = database_manager
        self.user_tokens = user_tokens
        self.active_configs = {}
        self.reply_counters = {}
        self.is_running = False
        
    def start_scheduler(self):
        """Start the automation scheduler"""
        self.is_running = True
        
        # Schedule auto-posting jobs
        schedule.every().day.at("09:00").do(self._run_auto_posting, time_slot="morning")
        schedule.every().day.at("14:00").do(self._run_auto_posting, time_slot="afternoon")
        schedule.every().day.at("19:00").do(self._run_auto_posting, time_slot="evening")
        
        # Schedule question monitoring every 5 minutes
        schedule.every(5).minutes.do(self._run_question_monitoring)
        
        # Reset reply counters every hour
        schedule.every().hour.do(self._reset_reply_counters)
        
        logger.info("Reddit automation scheduler started")
        
        # Start background scheduler thread
        import threading
        scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        scheduler_thread.start()
    
    def _scheduler_loop(self):
        """Background loop for running scheduled tasks"""
        while self.is_running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    async def setup_auto_posting(self, config: AutoPostConfig) -> Dict[str, Any]:
        """Set up automatic posting for a user"""
        try:
            # Validate configuration
            if not config.subreddits:
                config.subreddits = self._get_default_subreddits(config.domain)
            
            if not config.posting_times:
                config.posting_times = ["09:00", "14:00", "19:00"]
            
            # Store configuration
            self.active_configs[config.user_id] = {
                "auto_posting": config,
                "enabled": True,
                "created_at": datetime.now()
            }
            
            # Save to database
            await self.database.store_automation_config(config.user_id, "auto_posting", config.__dict__)
            
            logger.info(f"Auto-posting configured for user {config.user_id} in {config.domain} domain")
            
            return {
                "success": True,
                "message": "Auto-posting enabled successfully",
                "config": {
                    "domain": config.domain,
                    "business_type": config.business_type,
                    "posts_per_day": config.posts_per_day,
                    "subreddits": config.subreddits,
                    "posting_times": config.posting_times
                },
                "next_post_time": self._get_next_posting_time(config.posting_times)
            }
            
        except Exception as e:
            logger.error(f"Auto-posting setup failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to set up auto-posting"
            }
    
    async def setup_auto_replies(self, config: AutoReplyConfig) -> Dict[str, Any]:
        """Set up automatic replies for a user"""
        try:
            # Validate configuration
            if not config.subreddits:
                config.subreddits = self._get_default_subreddits(config.domain)
            
            if not config.keywords:
                config.keywords = self._get_default_keywords(config.domain)
            
            # Store configuration
            if config.user_id not in self.active_configs:
                self.active_configs[config.user_id] = {}
            
            self.active_configs[config.user_id]["auto_replies"] = config
            self.reply_counters[config.user_id] = 0
            
            # Save to database
            await self.database.store_automation_config(config.user_id, "auto_replies", config.__dict__)
            
            logger.info(f"Auto-replies configured for user {config.user_id} in {config.domain} domain")
            
            return {
                "success": True,
                "message": "Auto-replies enabled successfully",
                "config": {
                    "domain": config.domain,
                    "expertise_level": config.expertise_level,
                    "subreddits": config.subreddits,
                    "keywords": config.keywords,
                    "max_replies_per_hour": config.max_replies_per_hour
                },
                "monitoring_status": "Active - scanning every 5 minutes"
            }
            
        except Exception as e:
            logger.error(f"Auto-replies setup failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to set up auto-replies"
            }
    
    async def get_automation_status(self, user_id: str) -> Dict[str, Any]:
        """Get current automation status for a user"""
        try:
            user_config = self.active_configs.get(user_id, {})
            
            # Get daily statistics
            daily_stats = await self.database.get_daily_automation_stats(user_id)
            
            status = {
                "success": True,
                "user_id": user_id,
                "auto_posting": {
                    "enabled": "auto_posting" in user_config,
                    "config": user_config.get("auto_posting").__dict__ if "auto_posting" in user_config else None
                },
                "auto_replies": {
                    "enabled": "auto_replies" in user_config,
                    "config": user_config.get("auto_replies").__dict__ if "auto_replies" in user_config else None
                },
                "daily_stats": {
                    "posts_today": daily_stats.get("posts_today", 0),
                    "recent_replies": daily_stats.get("replies_24h", 0),
                    "total_karma": daily_stats.get("karma_gained", 0)
                },
                "scheduler_running": self.is_running,
                "last_updated": datetime.now().isoformat()
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Status check failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to get automation status"
            }
    
    def _run_auto_posting(self, time_slot: str):
        """Run auto-posting for all configured users"""
        asyncio.create_task(self._async_auto_posting(time_slot))
    
    async def _async_auto_posting(self, time_slot: str):
        """Async auto-posting implementation"""
        try:
            for user_id, config_data in self.active_configs.items():
                if "auto_posting" not in config_data:
                    continue
                
                config = config_data["auto_posting"]
                
                # Check if this time slot is configured for posting
                current_time = datetime.now().strftime("%H:%M")
                if current_time not in config.posting_times:
                    continue
                
                # Check if user has Reddit tokens
                if user_id not in self.user_tokens:
                    logger.warning(f"No Reddit tokens for user {user_id}")
                    continue
                
                # Generate and post content
                await self._generate_and_post_content(user_id, config, time_slot)
                
        except Exception as e:
            logger.error(f"Auto-posting failed: {e}")
    
    async def _generate_and_post_content(self, user_id: str, config: AutoPostConfig, time_slot: str):
        """Generate AI content and post to Reddit"""
        try:
            # Generate domain-specific content
            content_result = await self.ai_service.generate_reddit_domain_content(
                domain=config.domain,
                business_type=config.business_type,
                target_audience=config.target_audience,
                language=config.language,
                content_style=config.content_style,
                time_slot=time_slot
            )
            
            if not content_result.get("success"):
                logger.error(f"Content generation failed for user {user_id}")
                return
            
            # Select random subreddit for variety
            target_subreddit = random.choice(config.subreddits)
            
            # Post to Reddit
            post_result = await self.reddit_oauth.post_content_with_token(
                user_tokens=self.user_tokens[user_id],
                subreddit=target_subreddit,
                title=content_result["title"],
                content=content_result["content"],
                content_type="text"
            )
            
            if post_result.get("success"):
                # Log successful post
                await self.database.log_automation_activity(
                    user_id=user_id,
                    activity_type="auto_post",
                    status="success",
                    details={
                        "subreddit": target_subreddit,
                        "title": content_result["title"],
                        "post_id": post_result.get("post_id"),
                        "time_slot": time_slot,
                        "domain": config.domain
                    }
                )
                
                logger.info(f"Auto-post successful for user {user_id}: {post_result.get('post_url')}")
            else:
                logger.error(f"Auto-post failed for user {user_id}: {post_result.get('error')}")
                
        except Exception as e:
            logger.error(f"Generate and post failed for user {user_id}: {e}")
    
    def _run_question_monitoring(self):
        """Run question monitoring and auto-replies"""
        asyncio.create_task(self._async_question_monitoring())
    
    async def _async_question_monitoring(self):
        """Async question monitoring implementation"""
        try:
            for user_id, config_data in self.active_configs.items():
                if "auto_replies" not in config_data:
                    continue
                
                config = config_data["auto_replies"]
                
                # Check reply limit
                if self.reply_counters.get(user_id, 0) >= config.max_replies_per_hour:
                    continue
                
                # Check if user has Reddit tokens
                if user_id not in self.user_tokens:
                    continue
                
                # Monitor questions and reply
                await self._monitor_and_reply_questions(user_id, config)
                
        except Exception as e:
            logger.error(f"Question monitoring failed: {e}")
    
    async def _monitor_and_reply_questions(self, user_id: str, config: AutoReplyConfig):
        """Monitor questions and generate auto-replies"""
        try:
            # Find target questions using the question monitor
            question_monitor = RedditQuestionMonitor(self.reddit_oauth)
            
            questions = await question_monitor.find_target_questions(
                domain=config.domain,
                expertise_keywords=config.keywords,
                subreddits=config.subreddits,
                min_score=1,
                max_age_hours=2  # Only recent questions
            )
            
            for question in questions[:2]:  # Limit to 2 questions per monitoring cycle
                # Check if we've already replied to this question
                already_replied = await self.database.check_if_replied(user_id, question["id"])
                if already_replied:
                    continue
                
                # Generate AI reply
                reply_result = await self.ai_service.generate_qa_answer(
                    platform="reddit",
                    question=question["title"] + " " + question["content"],
                    domain=config.domain,
                    expertise_level=config.expertise_level,
                    language="en"
                )
                
                if not reply_result.get("success"):
                    continue
                
                # Add natural delay before replying
                delay_minutes = random.randint(config.response_delay_minutes, config.response_delay_minutes + 10)
                await asyncio.sleep(delay_minutes * 60)
                
                # Post reply to Reddit
                reply_post_result = await self.reddit_oauth.reply_to_post_with_token(
                    user_tokens=self.user_tokens[user_id],
                    post_id=question["id"],
                    reply_content=reply_result["answer"]
                )
                
                if reply_post_result.get("success"):
                    # Update reply counter
                    self.reply_counters[user_id] = self.reply_counters.get(user_id, 0) + 1
                    
                    # Log successful reply
                    await self.database.log_automation_activity(
                        user_id=user_id,
                        activity_type="auto_reply",
                        status="success",
                        details={
                            "question_id": question["id"],
                            "subreddit": question["subreddit"],
                            "question_title": question["title"],
                            "reply_id": reply_post_result.get("comment_id"),
                            "domain": config.domain
                        }
                    )
                    
                    logger.info(f"Auto-reply successful for user {user_id} on question {question['id']}")
                
                # Break if we've hit the hourly limit
                if self.reply_counters.get(user_id, 0) >= config.max_replies_per_hour:
                    break
                    
        except Exception as e:
            logger.error(f"Monitor and reply failed for user {user_id}: {e}")
    
    def _reset_reply_counters(self):
        """Reset hourly reply counters"""
        self.reply_counters = {}
        logger.info("Reply counters reset")
    
    def _get_default_subreddits(self, domain: str) -> List[str]:
        """Get default subreddits for a domain"""
        domain_subreddits = {
            "education": ["JEE", "NEET", "IndianStudents", "india"],
            "restaurant": ["IndianFood", "food", "bangalore", "mumbai"],
            "tech": ["developersIndia", "programming", "india"],
            "health": ["fitness", "HealthyFood", "india"],
            "business": ["entrepreneur", "IndiaInvestments", "business"]
        }
        return domain_subreddits.get(domain, ["india", "AskReddit"])
    
    def _get_default_keywords(self, domain: str) -> List[str]:
        """Get default keywords for a domain"""
        domain_keywords = {
            "education": ["help", "study", "exam", "preparation", "tips", "guidance", "career"],
            "restaurant": ["food", "recipe", "restaurant", "cooking", "taste", "recommend"],
            "tech": ["programming", "code", "development", "career", "job", "technology"],
            "health": ["fitness", "health", "diet", "exercise", "wellness", "nutrition"],
            "business": ["business", "startup", "investment", "money", "career", "entrepreneur"]
        }
        return domain_keywords.get(domain, ["help", "advice", "tips"])
    
    def _get_next_posting_time(self, posting_times: List[str]) -> str:
        """Get the next scheduled posting time"""
        current_time = datetime.now().time()
        
        for time_str in posting_times:
            post_time = datetime.strptime(time_str, "%H:%M").time()
            if post_time > current_time:
                return time_str
        
        # If no time today, return first time tomorrow
        return posting_times[0] + " (tomorrow)"

class RedditQuestionMonitor:
    """Monitor Reddit for questions to answer"""
    
    def __init__(self, reddit_oauth_connector):
        self.reddit_oauth = reddit_oauth_connector
    
    async def find_target_questions(
        self,
        domain: str,
        expertise_keywords: List[str],
        subreddits: List[str] = None,
        min_score: int = 1,
        max_age_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Find questions that match expertise and have good engagement potential"""
        try:
            target_questions = []
            
            if not subreddits:
                subreddits = self._get_domain_subreddits(domain)
            
            # Use Reddit's JSON API to search for questions
            for subreddit in subreddits:
                questions = await self._search_subreddit_questions(
                    subreddit, expertise_keywords, max_age_hours
                )
                
                for question in questions:
                    if question["score"] >= min_score:
                        # Calculate engagement potential
                        engagement_score = self._calculate_engagement_potential(question)
                        question["engagement_potential"] = engagement_score
                        question["domain"] = domain
                        
                        target_questions.append(question)
            
            # Sort by engagement potential
            target_questions.sort(key=lambda x: x["engagement_potential"], reverse=True)
            
            return target_questions[:20]  # Return top 20 questions
            
        except Exception as e:
            logger.error(f"Question monitoring failed: {e}")
            return []
    
    async def _search_subreddit_questions(
        self,
        subreddit: str,
        keywords: List[str],
        max_age_hours: int
    ) -> List[Dict[str, Any]]:
        """Search a specific subreddit for relevant questions"""
        try:
            import requests
            
            # Use Reddit's JSON API
            url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=50"
            headers = {"User-Agent": "IndianAutomationPlatform/1.0"}
            
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch from r/{subreddit}")
                return []
            
            data = response.json()
            posts = data.get("data", {}).get("children", [])
            
            questions = []
            cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
            
            for post_data in posts:
                post = post_data["data"]
                
                # Check if it's a question (contains question words or ends with ?)
                title = post.get("title", "").lower()
                content = post.get("selftext", "").lower()
                
                is_question = (
                    title.endswith("?") or
                    any(word in title for word in ["how", "what", "why", "where", "when", "help", "advice"]) or
                    any(word in content for word in ["help", "advice", "question"])
                )
                
                if not is_question:
                    continue
                
                # Check if it matches our keywords
                full_text = (title + " " + content).lower()
                if not any(keyword.lower() in full_text for keyword in keywords):
                    continue
                
                # Check age
                created_time = datetime.fromtimestamp(post["created_utc"])
                if created_time < cutoff_time:
                    continue
                
                # Extract question data
                question = {
                    "id": post["id"],
                    "title": post["title"],
                    "content": post.get("selftext", ""),
                    "subreddit": subreddit,
                    "author": post["author"],
                    "score": post["score"],
                    "num_comments": post["num_comments"],
                    "created_utc": post["created_utc"],
                    "url": f"https://www.reddit.com{post['permalink']}",
                    "age_hours": (datetime.now() - created_time).total_seconds() / 3600
                }
                
                questions.append(question)
            
            return questions
            
        except Exception as e:
            logger.error(f"Subreddit search failed for r/{subreddit}: {e}")
            return []
    
    def _calculate_engagement_potential(self, question: Dict[str, Any]) -> float:
        """Calculate engagement potential score for a question"""
        try:
            score = question["score"]
            comments = question["num_comments"]
            age_hours = question["age_hours"]
            
            # Base score from upvotes and comments
            base_score = (score * 1.0) + (comments * 1.5)
            
            # Age penalty (newer questions are better)
            age_factor = max(0.1, 1 - (age_hours / 24))
            
            # Question quality indicators
            title_length = len(question["title"])
            content_length = len(question["content"])
            
            quality_factor = 1.0
            if 20 <= title_length <= 100:  # Good title length
                quality_factor += 0.2
            if content_length > 50:  # Has detailed content
                quality_factor += 0.3
            
            engagement_score = base_score * age_factor * quality_factor
            
            return round(engagement_score, 2)
            
        except Exception as e:
            logger.error(f"Engagement calculation failed: {e}")
            return 0.0
    
    def _get_domain_subreddits(self, domain: str) -> List[str]:
        """Get default subreddits for monitoring by domain"""
        domain_subreddits = {
            "education": ["JEE", "NEET", "IndianStudents", "AskReddit", "india"],
            "restaurant": ["IndianFood", "food", "AskReddit", "india"],
            "tech": ["developersIndia", "programming", "AskReddit", "india"],
            "health": ["fitness", "AskReddit", "india"],
            "business": ["entrepreneur", "AskReddit", "india"]
        }
        return domain_subreddits.get(domain, ["AskReddit", "india"])

class RedditUserTargeting:
    """Find and target active Reddit users in specific domains"""
    
    def __init__(self, reddit_oauth_connector):
        self.reddit_oauth = reddit_oauth_connector
    
    async def find_users_asking_questions(
        self,
        domain: str,
        subreddits: List[str],
        time_period_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Find users who frequently ask questions in the domain"""
        try:
            user_activity = {}
            
            for subreddit in subreddits:
                questions = await self._get_recent_questions_from_subreddit(
                    subreddit, time_period_hours
                )
                
                for question in questions:
                    author = question["author"]
                    if author == "[deleted]" or author == "AutoModerator":
                        continue
                    
                    if author not in user_activity:
                        user_activity[author] = {
                            "username": author,
                            "question_count": 0,
                            "total_score": 0,
                            "recent_questions": [],
                            "subreddits": set()
                        }
                    
                    user_activity[author]["question_count"] += 1
                    user_activity[author]["total_score"] += question["score"]
                    user_activity[author]["subreddits"].add(question["subreddit"])
                    user_activity[author]["recent_questions"].append({
                        "question": question["title"],
                        "subreddit": question["subreddit"],
                        "score": question["score"]
                    })
            
            # Process and rank users
            active_users = []
            for user_data in user_activity.values():
                if user_data["question_count"] >= 2:  # At least 2 questions
                    # Calculate engagement level
                    avg_score = user_data["total_score"] / user_data["question_count"]
                    
                    if avg_score >= 5:
                        engagement_level = "high"
                    elif avg_score >= 2:
                        engagement_level = "medium"
                    else:
                        engagement_level = "low"
                    
                    user_data["engagement_level"] = engagement_level
                    user_data["average_score"] = round(avg_score, 1)
                    user_data["subreddits"] = list(user_data["subreddits"])
                    
                    # Limit recent questions to top 5
                    user_data["recent_questions"] = user_data["recent_questions"][:5]
                    
                    active_users.append(user_data)
            
            # Sort by question count and average score
            active_users.sort(
                key=lambda x: (x["question_count"], x["average_score"]),
                reverse=True
            )
            
            return active_users[:10]  # Return top 10 active users
            
        except Exception as e:
            logger.error(f"User targeting failed: {e}")
            return []
    
    async def _get_recent_questions_from_subreddit(
        self,
        subreddit: str,
        time_period_hours: int
    ) -> List[Dict[str, Any]]:
        """Get recent questions from a subreddit"""
        try:
            import requests
            
            url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=100"
            headers = {"User-Agent": "IndianAutomationPlatform/1.0"}
            
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                return []
            
            data = response.json()
            posts = data.get("data", {}).get("children", [])
            
            questions = []
            cutoff_time = datetime.now() - timedelta(hours=time_period_hours)
            
            for post_data in posts:
                post = post_data["data"]
                
                # Check if it's a question
                title = post.get("title", "").lower()
                is_question = (
                    title.endswith("?") or
                    any(word in title for word in ["how", "what", "why", "help", "advice"])
                )
                
                if not is_question:
                    continue
                
                # Check age
                created_time = datetime.fromtimestamp(post["created_utc"])
                if created_time < cutoff_time:
                    continue
                
                questions.append({
                    "id": post["id"],
                    "title": post["title"],
                    "author": post["author"],
                    "subreddit": subreddit,
                    "score": post["score"],
                    "created_utc": post["created_utc"]
                })
            
            return questions
            
        except Exception as e:
            logger.error(f"Failed to get questions from r/{subreddit}: {e}")
            return []