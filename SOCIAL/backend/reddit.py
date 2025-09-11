"""
Reddit Integration Module for Multi-Platform Automation
Handles Reddit OAuth, content posting, Q&A monitoring, and engagement tracking
"""

import praw
import asyncio
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging
from fastapi import HTTPException
import re
from dataclasses import dataclass
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RedditPost:
    """Data class for Reddit post information"""
    id: str
    title: str
    content: str
    subreddit: str
    score: int
    num_comments: int
    created_utc: float
    url: str
    author: str
    is_self: bool

@dataclass
class RedditComment:
    """Data class for Reddit comment information"""
    id: str
    body: str
    score: int
    created_utc: float
    parent_id: str
    post_id: str
    subreddit: str

class RedditConnector:
    """
    Production-ready Reddit API connector with comprehensive error handling,
    rate limiting, and multi-language support
    """
    
    def __init__(self, config: Dict[str, str]):
        """
        Initialize Reddit connector with configuration
        
        Args:
            config: Dictionary containing Reddit API credentials
        """
        self.client_id = config.get('REDDIT_CLIENT_ID')
        self.client_secret = config.get('REDDIT_CLIENT_SECRET')
        self.user_agent = config.get('REDDIT_USER_AGENT')
        self.username = config.get('REDDIT_USERNAME')
        self.password = config.get('REDDIT_PASSWORD')
        
        self.reddit = None
        self.is_authenticated = False
        
        # Rate limiting
        self.last_request_time = {}
        self.min_request_interval = 2  # seconds between requests
        
        # Indian subreddits for targeted content
        self.indian_subreddits = [
            'india', 'indiaspeaks', 'indianews', 'mumbai', 'delhi', 'bangalore',
            'chennai', 'kolkata', 'pune', 'hyderabad', 'ahmedabad', 'jaipur',
            'IndianStudents', 'IndianAcademia', 'IndianFood', 'bollywood',
            'cricket', 'IndianGaming', 'IndianPersonalFinance'
        ]
        
        # Educational subreddits for Q&A
        self.educational_subreddits = [
            'AskReddit', 'explainlikeimfive', 'NoStupidQuestions', 'answers',
            'HomeworkHelp', 'learnpython', 'learnjavascript', 'EngineeringStudents',
            'AskScience', 'AskHistorians', 'math', 'physics', 'chemistry'
        ]
        
        self._initialize_connection()
    
    def _initialize_connection(self) -> None:
        """Initialize Reddit API connection with proper error handling"""
        try:
            self.reddit = praw.Reddit(
                client_id=self.client_id,
                client_secret=self.client_secret,
                user_agent=self.user_agent,
                username=self.username,
                password=self.password,
                check_for_async=False
            )
            
            # Test connection
            self.reddit.user.me()
            self.is_authenticated = True
            logger.info("Reddit connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Reddit connection: {e}")
            self.is_authenticated = False
            raise HTTPException(status_code=500, detail=f"Reddit authentication failed: {e}")
    
    def _rate_limit_check(self, endpoint: str) -> None:
        """Implement rate limiting to avoid Reddit API limits"""
        current_time = datetime.now()
        
        if endpoint in self.last_request_time:
            time_diff = (current_time - self.last_request_time[endpoint]).total_seconds()
            if time_diff < self.min_request_interval:
                sleep_time = self.min_request_interval - time_diff
                asyncio.sleep(sleep_time)
        
        self.last_request_time[endpoint] = current_time
    
    async def authenticate_user(self, access_token: str = None) -> Dict[str, Any]:
        """
        Authenticate Reddit user and return user information
        
        Args:
            access_token: Optional OAuth access token
            
        Returns:
            Dictionary containing user information and authentication status
        """
        try:
            if not self.is_authenticated:
                self._initialize_connection()
            
            user = self.reddit.user.me()
            user_info = {
                "username": str(user),
                "id": user.id if hasattr(user, 'id') else None,
                "karma": {
                    "comment": user.comment_karma if hasattr(user, 'comment_karma') else 0,
                    "link": user.link_karma if hasattr(user, 'link_karma') else 0
                },
                "created_utc": user.created_utc if hasattr(user, 'created_utc') else None,
                "is_verified": True,
                "platform": "reddit"
            }
            
            logger.info(f"Reddit user authenticated: {user_info['username']}")
            return {
                "success": True,
                "user_info": user_info,
                "message": "Reddit authentication successful"
            }
            
        except Exception as e:
            logger.error(f"Reddit authentication failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Reddit authentication failed"
            }
    
    async def post_content(
        self, 
        subreddit_name: str, 
        title: str, 
        content: str,
        content_type: str = "text",
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Post content to Reddit with comprehensive error handling
        
        Args:
            subreddit_name: Target subreddit name
            title: Post title
            content: Post content/body
            content_type: Type of content (text, link, image)
            language: Content language for cultural adaptation
            
        Returns:
            Dictionary containing post result and metadata
        """
        try:
            self._rate_limit_check("post_content")
            
            if not self.is_authenticated:
                await self.authenticate_user()
            
            # Cultural adaptation for Indian content
            if language in ['hi', 'hi-IN'] and subreddit_name in self.indian_subreddits:
                title = self._adapt_for_indian_audience(title, language)
                content = self._adapt_for_indian_audience(content, language)
            
            subreddit = self.reddit.subreddit(subreddit_name)
            
            # Post based on content type
            if content_type == "text":
                submission = subreddit.submit(title=title, selftext=content)
            elif content_type == "link":
                submission = subreddit.submit(title=title, url=content)
            else:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Return comprehensive result
            result = {
                "success": True,
                "post_id": submission.id,
                "post_url": f"https://reddit.com{submission.permalink}",
                "title": submission.title,
                "subreddit": str(submission.subreddit),
                "created_utc": submission.created_utc,
                "score": submission.score,
                "num_comments": submission.num_comments,
                "platform": "reddit",
                "message": "Content posted successfully to Reddit"
            }
            
            logger.info(f"Reddit post created: {result['post_url']}")
            return result
            
        except Exception as e:
            logger.error(f"Reddit posting failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to post content to Reddit"
            }
    
    async def monitor_questions(
        self, 
        subreddits: List[str] = None,
        keywords: List[str] = None,
        limit: int = 10
    ) -> List[RedditPost]:
        """
        Monitor Reddit for new questions and discussion opportunities
        
        Args:
            subreddits: List of subreddits to monitor
            keywords: Keywords to filter posts
            limit: Maximum number of posts to return
            
        Returns:
            List of RedditPost objects
        """
        try:
            self._rate_limit_check("monitor_questions")
            
            if subreddits is None:
                subreddits = self.educational_subreddits
            
            questions = []
            
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    
                    # Get new posts
                    for submission in subreddit.new(limit=limit):
                        # Filter by keywords if provided
                        if keywords:
                            title_lower = submission.title.lower()
                            if not any(keyword.lower() in title_lower for keyword in keywords):
                                continue
                        
                        # Check if it's a question or needs help
                        if self._is_question_post(submission.title, submission.selftext):
                            post = RedditPost(
                                id=submission.id,
                                title=submission.title,
                                content=submission.selftext,
                                subreddit=str(submission.subreddit),
                                score=submission.score,
                                num_comments=submission.num_comments,
                                created_utc=submission.created_utc,
                                url=f"https://reddit.com{submission.permalink}",
                                author=str(submission.author) if submission.author else "[deleted]",
                                is_self=submission.is_self
                            )
                            questions.append(post)
                
                except Exception as e:
                    logger.warning(f"Error monitoring subreddit {subreddit_name}: {e}")
                    continue
            
            # Sort by creation time (newest first)
            questions.sort(key=lambda x: x.created_utc, reverse=True)
            return questions[:limit]
            
        except Exception as e:
            logger.error(f"Error monitoring Reddit questions: {e}")
            return []
    
    async def post_answer(
        self, 
        post_id: str, 
        answer: str,
        language: str = "en"
    ) -> Dict[str, Any]:
        """
        Post an answer/comment to a Reddit post
        
        Args:
            post_id: Reddit post ID to comment on
            answer: Answer content
            language: Response language
            
        Returns:
            Dictionary containing comment result
        """
        try:
            self._rate_limit_check("post_answer")
            
            if not self.is_authenticated:
                await self.authenticate_user()
            
            submission = self.reddit.submission(id=post_id)
            
            # Format answer with appropriate tone for platform
            formatted_answer = self._format_reddit_answer(answer, language)
            
            comment = submission.reply(formatted_answer)
            
            result = {
                "success": True,
                "comment_id": comment.id,
                "comment_url": f"https://reddit.com{comment.permalink}",
                "parent_post_id": post_id,
                "content": formatted_answer,
                "created_utc": comment.created_utc,
                "platform": "reddit",
                "message": "Answer posted successfully on Reddit"
            }
            
            logger.info(f"Reddit comment posted: {result['comment_url']}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to post Reddit answer: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to post answer on Reddit"
            }
    
    async def get_user_stats(self, username: str = None) -> Dict[str, Any]:
        """
        Get comprehensive user statistics and engagement metrics
        
        Args:
            username: Reddit username (uses authenticated user if None)
            
        Returns:
            Dictionary containing user statistics
        """
        try:
            if username:
                user = self.reddit.redditor(username)
            else:
                user = self.reddit.user.me()
            
            # Calculate engagement metrics
            recent_posts = list(user.submissions.new(limit=100))
            recent_comments = list(user.comments.new(limit=100))
            
            total_post_karma = sum(post.score for post in recent_posts)
            total_comment_karma = sum(comment.score for comment in recent_comments)
            
            avg_post_score = total_post_karma / len(recent_posts) if recent_posts else 0
            avg_comment_score = total_comment_karma / len(recent_comments) if recent_comments else 0
            
            stats = {
                "username": str(user),
                "total_karma": {
                    "link": user.link_karma,
                    "comment": user.comment_karma,
                    "total": user.link_karma + user.comment_karma
                },
                "recent_activity": {
                    "posts_last_30_days": len(recent_posts),
                    "comments_last_30_days": len(recent_comments),
                    "avg_post_score": round(avg_post_score, 2),
                    "avg_comment_score": round(avg_comment_score, 2)
                },
                "account_age_days": (datetime.now() - datetime.fromtimestamp(user.created_utc)).days,
                "is_verified": user.is_employee if hasattr(user, 'is_employee') else False,
                "platform": "reddit"
            }
            
            return {
                "success": True,
                "stats": stats,
                "message": "User statistics retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to get Reddit user stats: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve user statistics"
            }
    
    async def search_relevant_discussions(
        self, 
        query: str, 
        subreddits: List[str] = None,
        time_filter: str = "week",
        limit: int = 25
    ) -> List[RedditPost]:
        """
        Search for relevant discussions based on query
        
        Args:
            query: Search query
            subreddits: List of subreddits to search in
            time_filter: Time filter (hour, day, week, month, year, all)
            limit: Maximum results to return
            
        Returns:
            List of relevant RedditPost objects
        """
        try:
            self._rate_limit_check("search_discussions")
            
            if subreddits is None:
                subreddits = self.indian_subreddits + self.educational_subreddits
            
            all_results = []
            
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    
                    search_results = subreddit.search(
                        query=query,
                        time_filter=time_filter,
                        limit=limit//len(subreddits)
                    )
                    
                    for submission in search_results:
                        post = RedditPost(
                            id=submission.id,
                            title=submission.title,
                            content=submission.selftext,
                            subreddit=str(submission.subreddit),
                            score=submission.score,
                            num_comments=submission.num_comments,
                            created_utc=submission.created_utc,
                            url=f"https://reddit.com{submission.permalink}",
                            author=str(submission.author) if submission.author else "[deleted]",
                            is_self=submission.is_self
                        )
                        all_results.append(post)
                
                except Exception as e:
                    logger.warning(f"Error searching subreddit {subreddit_name}: {e}")
                    continue
            
            # Sort by relevance (score and recency)
            all_results.sort(key=lambda x: (x.score, x.created_utc), reverse=True)
            return all_results[:limit]
            
        except Exception as e:
            logger.error(f"Error searching Reddit discussions: {e}")
            return []
    
    def _is_question_post(self, title: str, content: str) -> bool:
        """
        Determine if a post is asking a question or seeking help
        
        Args:
            title: Post title
            content: Post content
            
        Returns:
            Boolean indicating if post is a question
        """
        question_indicators = [
            '?', 'how', 'what', 'why', 'where', 'when', 'which', 'who',
            'help', 'need', 'please', 'advice', 'suggest', 'recommend',
            'explain', 'understand', 'confusion', 'doubt', 'problem'
        ]
        
        # Hindi question indicators
        hindi_indicators = [
            'कैसे', 'क्या', 'क्यों', 'कहाँ', 'कब', 'कौन', 'कौन सा',
            'मदद', 'सहायता', 'सुझाव', 'सलाह', 'समझाइए', 'बताइए'
        ]
        
        all_indicators = question_indicators + hindi_indicators
        text_to_check = (title + ' ' + content).lower()
        
        return any(indicator in text_to_check for indicator in all_indicators)
    
    def _adapt_for_indian_audience(self, text: str, language: str) -> str:
        """
        Adapt content for Indian audience with cultural context
        
        Args:
            text: Original text
            language: Target language
            
        Returns:
            Culturally adapted text
        """
        # Add Indian context and cultural sensitivity
        adaptations = {
            'hi': {
                'hello': 'नमस्ते',
                'thank you': 'धन्यवाद',
                'please': 'कृपया',
                'good': 'अच्छा',
                'help': 'मदद'
            }
        }
        
        if language in adaptations:
            for eng, hindi in adaptations[language].items():
                text = re.sub(rf'\b{eng}\b', hindi, text, flags=re.IGNORECASE)
        
        return text
    
    def _format_reddit_answer(self, answer: str, language: str) -> str:
        """
        Format answer appropriately for Reddit platform
        
        Args:
            answer: Raw answer content
            language: Response language
            
        Returns:
            Formatted answer with Reddit-appropriate styling
        """
        # Add Reddit-specific formatting
        formatted = answer
        
        # Add helpful disclaimer for advice
        if any(word in answer.lower() for word in ['advice', 'suggest', 'recommend']):
            if language == 'hi':
                disclaimer = "\n\n*यह केवल सामान्य जानकारी है। विशिष्ट सलाह के लिए विशेषज्ञ से संपर्क करें।*"
            else:
                disclaimer = "\n\n*This is general information only. Please consult with experts for specific advice.*"
            formatted += disclaimer
        
        # Add helpful engagement
        if language == 'hi':
            formatted += "\n\nकोई और सवाल हो तो पूछिए! 😊"
        else:
            formatted += "\n\nFeel free to ask if you have more questions! 😊"
        
        return formatted
    
    async def get_trending_topics(self, subreddits: List[str] = None) -> Dict[str, Any]:
        """
        Get trending topics and discussions from specified subreddits
        
        Args:
            subreddits: List of subreddits to analyze
            
        Returns:
            Dictionary containing trending topics and keywords
        """
        try:
            if subreddits is None:
                subreddits = self.indian_subreddits[:5]  # Limit for performance
            
            trending_data = {}
            
            for subreddit_name in subreddits:
                try:
                    subreddit = self.reddit.subreddit(subreddit_name)
                    hot_posts = list(subreddit.hot(limit=25))
                    
                    # Extract keywords from titles
                    keywords = {}
                    for post in hot_posts:
                        words = re.findall(r'\b\w+\b', post.title.lower())
                        for word in words:
                            if len(word) > 3:  # Filter short words
                                keywords[word] = keywords.get(word, 0) + post.score
                    
                    # Sort by weighted score
                    top_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:10]
                    
                    trending_data[subreddit_name] = {
                        "top_keywords": top_keywords,
                        "hot_posts_count": len(hot_posts),
                        "avg_score": sum(post.score for post in hot_posts) / len(hot_posts)
                    }
                
                except Exception as e:
                    logger.warning(f"Error analyzing subreddit {subreddit_name}: {e}")
                    continue
            
            return {
                "success": True,
                "trending_data": trending_data,
                "timestamp": datetime.now().isoformat(),
                "message": "Trending topics retrieved successfully"
            }
            
        except Exception as e:
            logger.error(f"Error getting trending topics: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to retrieve trending topics"
            }
    
    async def bulk_engage(
        self, 
        posts: List[str], 
        engagement_type: str = "upvote"
    ) -> Dict[str, Any]:
        """
        Bulk engagement with multiple posts (upvote, save, etc.)
        
        Args:
            posts: List of post IDs
            engagement_type: Type of engagement (upvote, downvote, save)
            
        Returns:
            Dictionary containing bulk engagement results
        """
        try:
            results = {"successful": [], "failed": []}
            
            for post_id in posts:
                try:
                    self._rate_limit_check(f"bulk_engage_{post_id}")
                    
                    submission = self.reddit.submission(id=post_id)
                    
                    if engagement_type == "upvote":
                        submission.upvote()
                    elif engagement_type == "downvote":
                        submission.downvote()
                    elif engagement_type == "save":
                        submission.save()
                    elif engagement_type == "clear_vote":
                        submission.clear_vote()
                    
                    results["successful"].append(post_id)
                    
                except Exception as e:
                    logger.warning(f"Failed to engage with post {post_id}: {e}")
                    results["failed"].append({"post_id": post_id, "error": str(e)})
            
            return {
                "success": True,
                "results": results,
                "total_processed": len(posts),
                "successful_count": len(results["successful"]),
                "failed_count": len(results["failed"]),
                "message": f"Bulk engagement completed: {len(results['successful'])}/{len(posts)} successful"
            }
            
        except Exception as e:
            logger.error(f"Bulk engagement failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Bulk engagement operation failed"
            }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check Reddit API connection health and rate limit status
        
        Returns:
            Dictionary containing health status
        """
        try:
            # Test basic API call
            user = self.reddit.user.me()
            
            # Check rate limit status (approximate)
            current_time = datetime.now()
            recent_requests = sum(
                1 for timestamp in self.last_request_time.values()
                if (current_time - timestamp).total_seconds() < 600  # Last 10 minutes
            )
            
            return {
                "success": True,
                "status": "healthy",
                "authenticated_user": str(user),
                "recent_api_calls": recent_requests,
                "rate_limit_status": "normal" if recent_requests < 50 else "approaching_limit",
                "last_check": current_time.isoformat(),
                "message": "Reddit API connection is healthy"
            }
            
        except Exception as e:
            logger.error(f"Reddit health check failed: {e}")
            return {
                "success": False,
                "status": "unhealthy",
                "error": str(e),
                "message": "Reddit API connection failed health check"
            }