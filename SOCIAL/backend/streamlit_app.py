"""
Streamlit Development Interface for Multi-Platform Automation System
Production-ready development UI with comprehensive testing capabilities
"""

import streamlit as st
import requests
import json
import asyncio
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import base64
import io
from typing import Dict, List, Any
import logging

# Configure page
st.set_page_config(
    page_title="Multi-Platform Automation System",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Session state initialization
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'user_token' not in st.session_state:
    st.session_state.user_token = None
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}
if 'platform_status' not in st.session_state:
    st.session_state.platform_status = {}


def make_api_request(endpoint: str, method: str = "GET", data: dict = None, auth_required: bool = True) -> dict:
    """
    Make API request with error handling
    
    Args:
        endpoint: API endpoint
        method: HTTP method
        data: Request data
        auth_required: Whether authentication is required
        
    Returns:
        API response dictionary
    """
    try:
        url = f"{API_BASE_URL}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if auth_required and st.session_state.user_token:
            headers["Authorization"] = f"Bearer {st.session_state.user_token}"
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error in API request: {e}")
        return {"success": False, "error": str(e)}


def login_page():
    """User authentication page"""
    st.title("🚀 Multi-Platform Automation System")
    st.markdown("### Welcome to the Indian Social Media Automation Platform")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("#### Login to Your Account")
        
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="your.email@example.com")
            password = st.text_input("Password", type="password")
            
            col_login, col_register = st.columns(2)
            
            with col_login:
                login_clicked = st.form_submit_button("Login", use_container_width=True)
            
            with col_register:
                register_clicked = st.form_submit_button("Register", use_container_width=True)
        
        if login_clicked:
            if email and password:
                with st.spinner("Authenticating..."):
                    response = make_api_request(
                        "/api/auth/login",
                        method="POST",
                        data={"email": email, "password": password},
                        auth_required=False
                    )
                
                if response.get("success"):
                    st.session_state.authenticated = True
                    st.session_state.user_token = response.get("access_token")
                    st.session_state.user_info = response.get("user", {})
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error(f"Login failed: {response.get('error', 'Unknown error')}")
            else:
                st.error("Please enter both email and password")
        
        if register_clicked:
            if email and password:
                with st.spinner("Creating account..."):
                    response = make_api_request(
                        "/api/auth/register",
                        method="POST",
                        data={
                            "email": email,
                            "password": password,
                            "name": email.split("@")[0]  # Use email prefix as name
                        },
                        auth_required=False
                    )
                
                if response.get("success"):
                    st.success("Account created successfully! Please login.")
                else:
                    st.error(f"Registration failed: {response.get('error', 'Unknown error')}")
            else:
                st.error("Please enter both email and password")
    
    # Demo section
    st.markdown("---")
    st.markdown("### 🎯 Platform Features")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        **📱 Reddit Integration**
        - Auto-post to Indian subreddits
        - Q&A monitoring and responses
        - Karma building automation
        - Cultural content adaptation
        """)
    
    with col2:
        st.markdown("""
        **🐦 Twitter Automation**
        - Tweet scheduling and posting
        - Thread generation
        - Engagement analytics
        - Trend participation
        """)
    
    with col3:
        st.markdown("""
        **💻 Stack Overflow**
        - Programming Q&A automation
        - Reputation building
        - Technical content generation
        - Code solution posting
        """)
    
    with col4:
        st.markdown("""
        **🏥 WebMD Health Q&A**
        - Medical information sharing
        - Health education content
        - Symptom explanation
        - Wellness advice
        """)


def main_dashboard():
    """Main application dashboard"""
    
    # Sidebar
    with st.sidebar:
        st.title(f"Welcome, {st.session_state.user_info.get('name', 'User')}!")
        
        # Platform connection status
        st.markdown("### 🔗 Platform Status")
        check_platform_status()
        
        # Navigation
        st.markdown("### 📊 Navigation")
        page = st.selectbox(
            "Select Page",
            [
                "Dashboard",
                "Reddit Automation",
                "Twitter Management", 
                "Stack Overflow Q&A",
                "WebMD Health",
                "AI Content Generator",
                "Voice Assistant",
                "Analytics",
                "Settings"
            ]
        )
        
        # Logout
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_token = None
            st.session_state.user_info = {}
            st.rerun()
    
    # Main content area
    if page == "Dashboard":
        dashboard_page()
    elif page == "Reddit Automation":
        reddit_page()
    elif page == "Twitter Management":
        twitter_page()
    elif page == "Stack Overflow Q&A":
        stackoverflow_page()
    elif page == "WebMD Health":
        webmd_page()
    elif page == "AI Content Generator":
        ai_content_page()
    elif page == "Voice Assistant":
        voice_assistant_page()
    elif page == "Analytics":
        analytics_page()
    elif page == "Settings":
        settings_page()


def check_platform_status():
    """Check and display platform connection status"""
    try:
        response = make_api_request("/health")
        
        if response.get("success"):
            services = response.get("services", {})
            
            # Reddit status
            reddit_status = services.get("reddit", {}).get("success", False)
            st.markdown(f"Reddit: {'🟢' if reddit_status else '🔴'}")
            
            # Database status
            db_status = services.get("database", {}).get("success", False)
            st.markdown(f"Database: {'🟢' if db_status else '🔴'}")
            
            # AI Service status
            ai_status = services.get("ai_service", {}).get("success", False)
            st.markdown(f"AI Service: {'🟢' if ai_status else '🔴'}")
            
        else:
            st.markdown("System: 🔴 Offline")
            
    except Exception as e:
        st.markdown("System: 🔴 Error")


def dashboard_page():
    """Main dashboard page"""
    st.title("📊 Dashboard Overview")
    
    # Get dashboard data
    response = make_api_request("/api/analytics/dashboard")
    
    if response.get("success"):
        dashboard_data = response.get("dashboard", {})
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Posts Today",
                dashboard_data.get("posts_today", 0),
                delta=dashboard_data.get("posts_change", 0)
            )
        
        with col2:
            st.metric(
                "Total Engagement",
                dashboard_data.get("total_engagement", 0),
                delta=dashboard_data.get("engagement_change", 0)
            )
        
        with col3:
            st.metric(
                "Q&A Earnings",
                f"₹{dashboard_data.get('qa_earnings', 0)}",
                delta=dashboard_data.get("earnings_change", 0)
            )
        
        with col4:
            st.metric(
                "Active Platforms",
                dashboard_data.get("active_platforms", 0),
                delta=dashboard_data.get("platforms_change", 0)
            )
        
        # Recent activity
        st.markdown("### 📈 Recent Activity")
        
        # Create sample activity data for demo
        activity_data = [
            {"time": "2024-01-15 14:30", "platform": "Reddit", "action": "Posted to r/india", "status": "Success"},
            {"time": "2024-01-15 14:25", "platform": "Twitter", "action": "Tweet posted", "status": "Success"},
            {"time": "2024-01-15 14:20", "platform": "Stack Overflow", "action": "Answer posted", "status": "Success"},
            {"time": "2024-01-15 14:15", "platform": "WebMD", "action": "Health answer", "status": "Success"},
        ]
        
        df = pd.DataFrame(activity_data)
        st.dataframe(df, use_container_width=True)
        
        # Engagement chart
        st.markdown("### 📊 Engagement Trends")
        
        # Generate sample data
        dates = pd.date_range(start="2024-01-01", end="2024-01-15", freq="D")
        engagement_data = pd.DataFrame({
            "Date": dates,
            "Reddit": [10, 15, 12, 18, 20, 25, 22, 30, 28, 35, 32, 40, 38, 45, 42],
            "Twitter": [5, 8, 6, 10, 12, 15, 18, 20, 25, 22, 28, 30, 35, 32, 38],
            "Stack Overflow": [2, 3, 1, 4, 5, 3, 6, 4, 7, 5, 8, 6, 9, 7, 10],
            "WebMD": [1, 1, 2, 1, 3, 2, 3, 4, 2, 5, 3, 6, 4, 7, 5]
        })
        
        fig = px.line(
            engagement_data.melt(id_vars=["Date"], var_name="Platform", value_name="Engagement"),
            x="Date",
            y="Engagement",
            color="Platform",
            title="Daily Engagement by Platform"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.error("Failed to load dashboard data")


def reddit_page():
    """Reddit automation page"""
    st.title("📱 Reddit Automation")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Post Content", "Monitor Questions", "Auto-Reply", "Statistics"])
    
    with tab1:
        st.markdown("### Create Reddit Post")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            subreddit = st.selectbox(
                "Select Subreddit",
                ["india", "indiaspeaks", "bangalore", "delhi", "mumbai", "pune", "AskReddit", "explainlikeimfive"]
            )
            
            title = st.text_input("Post Title", placeholder="Enter your post title...")
            content = st.text_area("Post Content", placeholder="Enter your post content...", height=200)
            
            col_lang, col_tone = st.columns(2)
            with col_lang:
                language = st.selectbox("Language", ["en", "hi", "ta", "te", "bn"])
            with col_tone:
                tone = st.selectbox("Tone", ["professional", "casual", "friendly", "informative"])
        
        with col2:
            st.markdown("#### Post Preview")
            if title and content:
                st.markdown(f"**Title:** {title}")
                st.markdown(f"**Content:** {content[:100]}...")
                st.markdown(f"**Subreddit:** r/{subreddit}")
                st.markdown(f"**Language:** {language}")
        
        if st.button("Post to Reddit", type="primary", use_container_width=True):
            if title and content:
                with st.spinner("Posting to Reddit..."):
                    response = make_api_request(
                        "/api/reddit/post",
                        method="POST",
                        data={
                            "subreddit": subreddit,
                            "title": title,
                            "content": content,
                            "language": language,
                            "content_type": "text"
                        }
                    )
                
                if response.get("success"):
                    st.success(f"Post created successfully! [View Post]({response.get('post_url')})")
                else:
                    st.error(f"Failed to post: {response.get('error')}")
            else:
                st.error("Please enter both title and content")
    
    with tab2:
        st.markdown("### Monitor Questions")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            subreddits_input = st.text_input(
                "Subreddits to Monitor (comma-separated)",
                value="AskReddit,explainlikeimfive,NoStupidQuestions"
            )
        
        with col2:
            keywords_input = st.text_input(
                "Keywords to Filter (comma-separated)",
                value="help,how,what,why"
            )
        
        limit = st.slider("Number of Questions", 5, 50, 10)
        
        if st.button("Find Questions", use_container_width=True):
            with st.spinner("Searching for questions..."):
                response = make_api_request(
                    f"/api/reddit/questions?subreddits={subreddits_input}&keywords={keywords_input}&limit={limit}"
                )
            
            if response.get("success"):
                questions = response.get("questions", [])
                
                if questions:
                    st.success(f"Found {len(questions)} questions")
                    
                    for i, question in enumerate(questions):
                        with st.expander(f"Q{i+1}: {question['title'][:80]}..."):
                            st.markdown(f"**Subreddit:** r/{question['subreddit']}")
                            st.markdown(f"**Score:** {question['score']} | **Comments:** {question['num_comments']}")
                            st.markdown(f"**Author:** {question['author']}")
                            st.markdown(f"**Content:** {question['content'][:200]}...")
                            st.markdown(f"**URL:** [View on Reddit]({question['url']})")
                            
                            if st.button(f"Generate Answer for Q{i+1}", key=f"answer_{i}"):
                                st.info("Answer generation feature coming soon!")
                else:
                    st.info("No questions found matching your criteria")
            else:
                st.error(f"Failed to fetch questions: {response.get('error')}")
    
    with tab3:
        st.markdown("### Auto-Reply to Questions")
        
        post_id = st.text_input("Reddit Post ID", placeholder="Enter the post ID to reply to...")
        answer_content = st.text_area("Your Answer", placeholder="Enter your answer...", height=150)
        
        if st.button("Post Answer", use_container_width=True):
            if post_id and answer_content:
                with st.spinner("Posting answer..."):
                    response = make_api_request(
                        "/api/reddit/answer",
                        method="POST",
                        data={
                            "post_id": post_id,
                            "answer": answer_content,
                            "language": "en"
                        }
                    )
                
                if response.get("success"):
                    st.success(f"Answer posted successfully! [View Comment]({response.get('comment_url')})")
                else:
                    st.error(f"Failed to post answer: {response.get('error')}")
            else:
                st.error("Please enter both post ID and answer")
    
    with tab4:
        st.markdown("### Reddit Statistics")
        
        if st.button("Refresh Stats", use_container_width=True):
            with st.spinner("Loading statistics..."):
                response = make_api_request("/api/reddit/stats")
            
            if response.get("success"):
                stats = response.get("stats", {})
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    karma = stats.get("total_karma", {})
                    st.metric("Total Karma", karma.get("total", 0))
                    st.metric("Link Karma", karma.get("link", 0))
                    st.metric("Comment Karma", karma.get("comment", 0))
                
                with col2:
                    activity = stats.get("recent_activity", {})
                    st.metric("Posts (30 days)", activity.get("posts_last_30_days", 0))
                    st.metric("Comments (30 days)", activity.get("comments_last_30_days", 0))
                
                with col3:
                    st.metric("Avg Post Score", activity.get("avg_post_score", 0))
                    st.metric("Avg Comment Score", activity.get("avg_comment_score", 0))
                    st.metric("Account Age (days)", stats.get("account_age_days", 0))
            else:
                st.error("Failed to load statistics")












def ai_content_page():
    """AI content generation page"""
    st.title("🤖 AI Content Generator")
    
    tab1, tab2, tab3 = st.tabs(["Platform Content", "Q&A Answers", "Voice Assistant"])
    
    with tab1:
        st.markdown("### Generate Platform-Specific Content")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            platform = st.selectbox(
                "Select Platform",
                ["reddit", "twitter", "stackoverflow", "webmd"]
            )
            
            content_type = st.selectbox(
                "Content Type",
                ["post", "comment", "answer", "tweet", "thread"]
            )
            
            topic = st.text_input("Topic", placeholder="Enter the topic for content generation...")
            
            col_tone, col_lang = st.columns(2)
            with col_tone:
                tone = st.selectbox("Tone", ["professional", "casual", "friendly", "informative", "humorous"])
            with col_lang:
                language = st.selectbox("Language", ["en", "hi", "ta", "te", "bn"])
            
            target_audience = st.text_input("Target Audience", placeholder="e.g., Indian students, tech professionals...")
            additional_context = st.text_area("Additional Context", placeholder="Any specific requirements or context...")
        
        with col2:
            st.markdown("#### Generation Settings")
            st.info(f"Platform: {platform.title()}")
            st.info(f"Type: {content_type.title()}")
            st.info(f"Language: {language.upper()}")
            
            if platform == "twitter":
                st.warning("Twitter content limited to 280 characters")
            elif platform == "reddit":
                st.info("Reddit content optimized for discussion")
            elif platform == "stackoverflow":
                st.info("Technical content with code examples")
            elif platform == "webmd":
                st.warning("Health content with medical disclaimers")
        
        if st.button("Generate Content", type="primary", use_container_width=True):
            if topic:
                with st.spinner("Generating AI content..."):
                    response = make_api_request(
                        "/api/ai/generate-content",
                        method="POST",
                        data={
                            "platform": platform,
                            "content_type": content_type,
                            "topic": topic,
                            "tone": tone,
                            "language": language,
                            "target_audience": target_audience,
                            "additional_context": additional_context
                        }
                    )
                
                if response.get("success"):
                    generated_content = response.get("content", "")
                    
                    st.success("Content generated successfully!")
                    
                    # Display generated content
                    st.markdown("#### Generated Content:")
                    st.text_area("", value=generated_content, height=200, key="generated_content")
                    
                    # Content metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Word Count", response.get("word_count", 0))
                    with col2:
                        st.metric("Character Count", response.get("character_count", 0))
                    with col3:
                        st.metric("Platform", platform.title())
                    
                    # Copy button (simulated)
                    if st.button("Copy Content", use_container_width=True):
                        st.success("Content copied to clipboard! (Simulated)")
                
                else:
                    st.error(f"Content generation failed: {response.get('error')}")
            else:
                st.error("Please enter a topic")
    
    with tab2:
        st.markdown("### Generate Q&A Answers")
        
        qa_platform = st.selectbox(
            "Q&A Platform",
            ["stackoverflow", "reddit", "webmd"],
            key="qa_platform"
        )
        
        question = st.text_area("Question", placeholder="Enter the question you want to answer...", height=100)
        context = st.text_area("Additional Context", placeholder="Any additional context about the question...")
        
        col1, col2 = st.columns(2)
        with col1:
            qa_language = st.selectbox("Response Language", ["en", "hi", "ta", "te", "bn"], key="qa_language")
        with col2:
            expertise_level = st.selectbox("Expertise Level", ["beginner", "intermediate", "advanced"])
        
        if st.button("Generate Answer", use_container_width=True):
            if question:
                with st.spinner("Generating answer..."):
                    # Mock response for development - replace with actual API call
                    import time
                    time.sleep(2)
                    
                    # Simulate API response
                    mock_answer = f"""Based on your question about {question[:50]}..., here's a comprehensive answer:

This is a great question that requires careful consideration. Let me break this down step by step:

1. First, let's understand the core concept
2. Then we'll look at practical applications
3. Finally, I'll provide some examples

The key points to remember are:
- Always consider the context
- Apply best practices
- Test your implementation

I hope this helps! Feel free to ask if you need any clarification."""
                    
                    st.success("Answer generated successfully!")
                    st.markdown("#### Generated Answer:")
                    st.text_area("", value=mock_answer, height=250, key="generated_answer")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Word Count", len(mock_answer.split()))
                    with col2:
                        st.metric("Expertise Level", expertise_level.title())
            else:
                st.error("Please enter a question")
    
    with tab3:
        st.markdown("### Voice Assistant (Demo Mode)")
        
        st.info("Voice processing features - Development version with mock responses")
        
        # Speech to Text section
        st.markdown("#### 🎤 Speech to Text")
        
        uploaded_audio = st.file_uploader(
            "Upload Audio File", 
            type=['wav', 'mp3', 'webm', 'm4a'],
            help="Upload an audio file to convert speech to text"
        )
        
        if uploaded_audio:
            st.audio(uploaded_audio)
            
            audio_language = st.selectbox(
                "Audio Language",
                ["auto", "en", "hi", "ta", "te", "bn"],
                help="Select the language of the audio"
            )
            
            if st.button("Convert Speech to Text"):
                with st.spinner("Processing audio..."):
                    import time
                    time.sleep(2)
                    
                    # Mock transcription based on language
                    if audio_language == "hi":
                        mock_transcription = "नमस्ते! मुझे JEE की तैयारी में मदद चाहिए। Physics के कुछ concepts clear नहीं हैं।"
                    elif audio_language == "ta":
                        mock_transcription = "வணக்கம்! எனக்கு JEE தயாரிப்பில் உதவி வேண்டும்।"
                    else:
                        mock_transcription = "Hello! I need help with JEE preparation. Some physics concepts are not clear to me."
                    
                    st.success(f"Speech converted successfully! (Detected: {audio_language})")
                    st.text_area("Transcribed Text:", value=mock_transcription, height=100)
                    
                    if st.button("Use for Content Generation"):
                        st.session_state.voice_text = mock_transcription
                        st.success("Text saved for content generation!")
        
        # Text to Speech section
        st.markdown("#### 🔊 Text to Speech")
        
        tts_text = st.text_area(
            "Enter text to convert to speech:",
            value=st.session_state.get('voice_text', ''),
            height=100,
            placeholder="Type your text here or use transcribed text from above..."
        )
        
        col1, col2 = st.columns(2)
        with col1:
            tts_language = st.selectbox(
                "Speech Language",
                ["en", "hi", "ta", "te", "bn"],
                help="Select the language for speech generation"
            )
        with col2:
            voice_gender = st.selectbox("Voice Gender", ["female", "male"])
        
        if st.button("Convert to Speech") and tts_text:
            with st.spinner("Generating speech..."):
                import time
                time.sleep(1)
                
                st.success("Speech generated successfully! (Demo Mode)")
                st.info("🎵 In production, an audio player would appear here with the generated speech")
                
                # Show what the API would return
                st.json({
                    "text_length": len(tts_text),
                    "language": tts_language,
                    "voice": voice_gender,
                    "duration_estimate": f"{len(tts_text) // 10} seconds"
                })


# Additional utility functions for the Streamlit app
def twitter_page():
    """Twitter management page placeholder"""
    st.title("🐦 Twitter Management")
    
    st.info("🚧 Twitter integration coming soon!")
    
    st.markdown("""
    ### Planned Features:
    - Tweet scheduling and automation
    - Thread generation for long content
    - Hashtag optimization
    - Engagement analytics
    - Indian trends monitoring
    - Multi-language tweet support
    """)
    
    # Mock interface
    with st.expander("Preview: Tweet Composer"):
        tweet_text = st.text_area("Compose Tweet", placeholder="What's happening?", max_chars=280)
        
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Language", ["English", "Hindi", "Tamil", "Telugu"])
        with col2:
            st.selectbox("Tone", ["Professional", "Casual", "Humorous"])
        
        if st.button("Schedule Tweet (Demo)", disabled=True):
            st.info("Twitter integration will be available in the next update!")


def stackoverflow_page():
    """Stack Overflow Q&A page placeholder"""
    st.title("💻 Stack Overflow Q&A")
    
    st.info("🚧 Stack Overflow integration coming soon!")
    
    st.markdown("""
    ### Planned Features:
    - Question monitoring by tags
    - AI-powered answer generation
    - Code example integration
    - Reputation building automation
    - Technical content optimization
    - Programming language detection
    """)
    
    # Mock interface
    with st.expander("Preview: Answer Generator"):
        question_text = st.text_area("Programming Question", placeholder="Enter the Stack Overflow question...")
        
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Language", ["Python", "JavaScript", "Java", "C++"])
        with col2:
            st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])
        
        if st.button("Generate Answer (Demo)", disabled=True):
            st.info("Stack Overflow integration will be available in the next update!")


def webmd_page():
    """WebMD Health Q&A page placeholder"""
    st.title("🏥 WebMD Health Q&A")
    
    st.info("🚧 WebMD integration coming soon!")
    
    st.markdown("""
    ### Planned Features:
    - Health question monitoring
    - Medical information responses (with disclaimers)
    - Symptom explanation automation
    - Wellness content generation
    - Regional health awareness
    - Ayurveda integration for Indian users
    """)
    
    # Mock interface
    with st.expander("Preview: Health Answer Generator"):
        health_question = st.text_area("Health Question", placeholder="Enter the health-related question...")
        
        col1, col2 = st.columns(2)
        with col1:
            st.selectbox("Category", ["General Health", "Nutrition", "Mental Health", "Fitness"])
        with col2:
            st.selectbox("Audience", ["General Public", "Students", "Elderly", "Athletes"])
        
        st.warning("⚠️ All health content will include appropriate medical disclaimers")
        
        if st.button("Generate Health Answer (Demo)", disabled=True):
            st.info("WebMD integration will be available in the next update!")


# Analytics helper functions
def create_sample_analytics_data():
    """Create sample data for analytics charts"""
    import pandas as pd
    import random
    from datetime import datetime, timedelta
    
    # Generate sample engagement data
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    
    engagement_data = []
    for date in dates:
        for platform in ["Reddit", "Twitter", "Stack Overflow", "WebMD"]:
            base_values = {"Reddit": 20, "Twitter": 15, "Stack Overflow": 8, "WebMD": 5}
            value = base_values[platform] + random.randint(-5, 10)
            engagement_data.append({
                "Date": date,
                "Platform": platform,
                "Engagement": max(0, value)
            })
    
    return pd.DataFrame(engagement_data)


def format_indian_currency(amount):
    """Format currency in Indian format"""
    if amount >= 10000000:  # 1 crore
        return f"₹{amount/10000000:.1f}Cr"
    elif amount >= 100000:  # 1 lakh
        return f"₹{amount/100000:.1f}L"
    elif amount >= 1000:  # 1 thousand
        return f"₹{amount/1000:.1f}K"
    else:
        return f"₹{amount:.0f}"


# Error handling wrapper
def safe_api_call(func):
    """Decorator for safe API calls with error handling"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            st.error(f"API call failed: {str(e)}")
            return {"success": False, "error": str(e)}
    return wrapper