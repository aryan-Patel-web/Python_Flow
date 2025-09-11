"""
Complete Streamlit Interface for Reddit Automation
Add these functions to your dev_interface.py or create as automation_ui.py
"""

import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json

# API helper function
def make_api_request(endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """Make API request to backend"""
    try:
        url = f"http://localhost:8000{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        if method == "GET":
            response = requests.get(url, headers=headers, params=data)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "success": False, 
                "error": f"HTTP {response.status_code}",
                "detail": response.text[:200]
            }
        
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "Connection failed",
            "detail": "Backend server not running on localhost:8000"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "detail": "Unexpected error in API request"
        }

def automation_setup_page():
    """Reddit automation setup and configuration"""
    st.title("🤖 Reddit Automation Setup")
    
    # Check system status first
    with st.sidebar:
        if st.button("🔄 Check System Status"):
            with st.spinner("Checking automation system..."):
                status_response = make_api_request("/api/automation/status")
                if status_response.get("success"):
                    st.success("✅ Automation system ready")
                else:
                    st.error("❌ Automation system not ready")
                    st.write(status_response.get("error", "Unknown error"))
    
    tab1, tab2, tab3 = st.tabs(["🚀 Auto-Posting", "💬 Auto-Replies", "📊 Current Status"])
    
    with tab1:
        st.markdown("### Set Up Automatic Posting")
        st.info("Configure your Reddit account to automatically post content 3-5 times daily")
        
        col1, col2 = st.columns(2)
        
        with col1:
            domain = st.selectbox(
                "Business Domain",
                ["education", "restaurant", "tech", "health", "business"],
                help="Choose your business area for content generation"
            )
            
            business_type = st.text_input(
                "Describe Your Business",
                placeholder="e.g., JEE coaching institute in Delhi, South Indian restaurant in Bangalore...",
                help="Specific description helps generate better content"
            )
            
            target_audience = st.selectbox(
                "Target Audience",
                ["indian_students", "food_lovers", "tech_professionals", "health_conscious", "entrepreneurs"]
            )
            
            language = st.selectbox("Content Language", ["en", "hi"])
        
        with col2:
            posts_per_day = st.slider("Posts Per Day", 1, 5, 3, help="Number of automated posts daily")
            
            posting_times = st.multiselect(
                "Posting Times (24hr format)",
                ["06:00", "08:00", "09:00", "11:00", "12:00", "14:00", "16:00", "18:00", "19:00", "20:00"],
                default=["09:00", "14:00", "19:00"],
                help="Choose optimal times based on your audience activity"
            )
            
            content_style = st.selectbox(
                "Content Style",
                ["engaging", "informative", "promotional", "helpful"],
                help="Tone and approach for generated content"
            )
        
        # Dynamic subreddit suggestions based on domain
        st.markdown("#### Target Subreddits")
        domain_subreddits = {
            "education": ["JEE", "NEET", "IndianStudents", "india", "AskReddit", "studytips"],
            "restaurant": ["IndianFood", "food", "bangalore", "mumbai", "delhi", "FoodPorn"],
            "tech": ["developersIndia", "programming", "india", "bangalore", "cscareerquestions"],
            "health": ["fitness", "HealthyFood", "india", "mentalhealth", "nutrition"],
            "business": ["entrepreneur", "IndiaInvestments", "business", "india", "startup"]
        }
        
        suggested_subreddits = domain_subreddits.get(domain, ["india"])
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Recommended for your domain:**")
            for sub in suggested_subreddits[:3]:
                st.markdown(f"• r/{sub}")
        
        with col2:
            selected_subreddits = st.multiselect(
                "Select Target Subreddits",
                suggested_subreddits,
                default=suggested_subreddits[:3],
                help="Choose 3-5 subreddits for best results"
            )
        
        # Preview section
        if business_type and selected_subreddits:
            with st.expander("📋 Preview Auto-Post Configuration"):
                st.markdown(f"**Business:** {business_type}")
                st.markdown(f"**Domain:** {domain}")
                st.markdown(f"**Daily Posts:** {posts_per_day}")
                st.markdown(f"**Posting Times:** {', '.join(posting_times)}")
                st.markdown(f"**Target Subreddits:** {', '.join([f'r/{sub}' for sub in selected_subreddits])}")
                st.markdown(f"**Content Style:** {content_style}")
        
        # Setup button
        if st.button("🚀 Enable Auto-Posting", type="primary", use_container_width=True):
            if not business_type or not selected_subreddits:
                st.error("Please fill in business description and select at least one subreddit")
                return
            
            with st.spinner("Setting up auto-posting system..."):
                response = make_api_request(
                    "/api/automation/setup-auto-posting",
                    method="POST",
                    data={
                        "domain": domain,
                        "business_type": business_type,
                        "target_audience": target_audience,
                        "language": language,
                        "subreddits": selected_subreddits,
                        "posts_per_day": posts_per_day,
                        "posting_times": posting_times,
                        "content_style": content_style
                    }
                )
            
            if response.get("success"):
                st.success("🎉 Auto-posting enabled successfully!")
                
                config = response.get("config", {})
                st.markdown("#### Configuration Saved:")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Daily Posts", config.get("posts_per_day", 0))
                    st.metric("Subreddits", len(config.get("subreddits", [])))
                with col2:
                    st.metric("Posting Times", len(config.get("posting_times", [])))
                    st.markdown(f"**Next Post:** {response.get('next_post_time', 'Soon')}")
                
                st.info("Your Reddit account will now automatically post quality content at the scheduled times!")
            else:
                st.error(f"Setup failed: {response.get('error', 'Unknown error')}")
                st.json(response)
    
    with tab2:
        st.markdown("### Set Up Automatic Replies")
        st.info("Automatically find and answer relevant questions in your expertise area")
        
        col1, col2 = st.columns(2)
        
        with col1:
            reply_domain = st.selectbox(
                "Your Expertise Domain",
                ["education", "tech", "health", "business"],
                key="reply_domain",
                help="Area where you can provide valuable answers"
            )
            
            expertise_level = st.selectbox(
                "Your Expertise Level",
                ["beginner", "intermediate", "expert"],
                index=1,
                help="Determines the depth and complexity of your replies"
            )
            
            keywords = st.text_area(
                "Keywords to Monitor",
                placeholder="help, advice, tips, guidance, how to, best way, struggling with",
                help="Questions containing these keywords will trigger auto-replies",
                height=100
            )
        
        with col2:
            max_replies_per_hour = st.slider(
                "Max Replies Per Hour", 
                1, 10, 2,
                help="Limit to avoid spam detection"
            )
            
            response_delay = st.slider(
                "Response Delay (minutes)",
                5, 60, 15,
                help="Wait time before replying to appear natural"
            )
            
            monitor_subreddits = st.multiselect(
                "Subreddits to Monitor",
                domain_subreddits.get(reply_domain, ["AskReddit"]),
                default=domain_subreddits.get(reply_domain, ["AskReddit"])[:2],
                help="Where to look for questions to answer"
            )
        
        # Auto-reply preview
        if keywords and monitor_subreddits:
            with st.expander("📋 Preview Auto-Reply Configuration"):
                st.markdown(f"**Expertise:** {reply_domain} ({expertise_level} level)")
                st.markdown(f"**Monitoring:** {', '.join([f'r/{sub}' for sub in monitor_subreddits])}")
                st.markdown(f"**Keywords:** {keywords}")
                st.markdown(f"**Rate Limit:** {max_replies_per_hour} replies/hour")
                st.markdown(f"**Response Delay:** {response_delay} minutes")
        
        if st.button("💬 Enable Auto-Replies", type="primary", use_container_width=True):
            if not keywords or not monitor_subreddits:
                st.error("Please enter keywords and select subreddits to monitor")
                return
            
            keyword_list = [k.strip() for k in keywords.split(",")]
            
            with st.spinner("Setting up auto-reply system..."):
                response = make_api_request(
                    "/api/automation/setup-auto-replies",
                    method="POST",
                    data={
                        "domain": reply_domain,
                        "expertise_level": expertise_level,
                        "subreddits": monitor_subreddits,
                        "keywords": keyword_list,
                        "max_replies_per_hour": max_replies_per_hour,
                        "response_delay_minutes": response_delay
                    }
                )
            
            if response.get("success"):
                st.success("🎉 Auto-replies enabled successfully!")
                
                config = response.get("config", {})
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Max Replies/Hour", config.get("max_replies_per_hour", 0))
                    st.metric("Monitoring Subreddits", len(config.get("subreddits", [])))
                with col2:
                    st.metric("Keywords", len(config.get("keywords", [])))
                    st.markdown(f"**Status:** {response.get('monitoring_status', 'Active')}")
                
                st.info("System is now monitoring Reddit every 5 minutes for questions you can help with!")
            else:
                st.error(f"Setup failed: {response.get('error', 'Unknown error')}")
                st.json(response)
    
    with tab3:
        st.markdown("### Current Automation Status")
        
        if st.button("🔄 Refresh Status", use_container_width=True):
            with st.spinner("Loading automation status..."):
                response = make_api_request("/api/automation/status")
            
            if response.get("success"):
                status = response.get("status", {})
                
                # System status indicators
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 🚀 Auto-Posting")
                    auto_posting = status.get("auto_posting", {})
                    if auto_posting.get("enabled"):
                        st.success("✅ Active")
                        config = auto_posting.get("config", {})
                        if config:
                            st.markdown(f"**Domain:** {config.get('domain', 'N/A')}")
                            st.markdown(f"**Posts/Day:** {config.get('posts_per_day', 'N/A')}")
                            st.markdown(f"**Subreddits:** {len(config.get('subreddits', []))}")
                    else:
                        st.warning("❌ Not Active")
                        st.markdown("Use Auto-Posting tab to enable")
                
                with col2:
                    st.markdown("#### 💬 Auto-Replies")
                    auto_replies = status.get("auto_replies", {})
                    if auto_replies.get("enabled"):
                        st.success("✅ Active")
                        config = auto_replies.get("config", {})
                        if config:
                            st.markdown(f"**Domain:** {config.get('domain', 'N/A')}")
                            st.markdown(f"**Max Replies/Hour:** {config.get('max_replies_per_hour', 'N/A')}")
                            st.markdown(f"**Monitoring:** {len(config.get('subreddits', []))} subreddits")
                    else:
                        st.warning("❌ Not Active")
                        st.markdown("Use Auto-Replies tab to enable")
                
                # Daily statistics
                st.markdown("#### 📊 Today's Activity")
                daily_stats = status.get("daily_stats", {})
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Posts Today", daily_stats.get("posts_today", 0))
                with col2:
                    st.metric("Replies (24h)", daily_stats.get("recent_replies", 0))
                with col3:
                    st.metric("Karma Gained", daily_stats.get("total_karma", 0))
                
                # System health
                st.markdown("#### System Health")
                health_col1, health_col2 = st.columns(2)
                with health_col1:
                    scheduler_status = "Running" if status.get("scheduler_running") else "Stopped"
                    if status.get("scheduler_running"):
                        st.success(f"Scheduler: {scheduler_status}")
                    else:
                        st.error(f"Scheduler: {scheduler_status}")
                
                with health_col2:
                    last_updated = status.get("last_updated", "Unknown")
                    st.info(f"Last Updated: {last_updated[:19] if last_updated != 'Unknown' else 'Unknown'}")
                
            else:
                st.error("Failed to get automation status")
                st.json(response)

def question_discovery_page():
    """Discover and target Reddit questions"""
    st.title("Question Discovery & Targeting")
    
    tab1, tab2, tab3 = st.tabs(["Find Target Questions", "Active Users", "Trending Topics"])
    
    with tab1:
        st.markdown("### Find Questions to Answer")
        st.info("Discover high-potential questions in your expertise area for manual or automated replies")
        
        col1, col2 = st.columns(2)
        
        with col1:
            domain = st.selectbox("Domain", ["education", "tech", "health", "business"])
            
            expertise_keywords = st.text_input(
                "Your Expertise Keywords",
                placeholder="JEE, physics, study tips, career guidance",
                help="Keywords that indicate questions you can answer well"
            )
            
            subreddits = st.text_input(
                "Subreddits (optional)",
                placeholder="JEE,NEET,IndianStudents",
                help="Leave empty to use domain defaults"
            )
        
        with col2:
            min_score = st.slider("Minimum Upvotes", 0, 20, 1)
            max_age_hours = st.slider("Maximum Age (hours)", 1, 72, 24)
            limit = st.slider("Number of Results", 5, 20, 10)
        
        if st.button("Find Target Questions", type="primary", use_container_width=True):
            if not expertise_keywords:
                st.error("Please enter your expertise keywords")
                return
            
            with st.spinner("Scanning Reddit for relevant questions..."):
                response = make_api_request(
                    f"/api/automation/target-questions?domain={domain}&expertise_keywords={expertise_keywords}&subreddits={subreddits}&min_score={min_score}&max_age_hours={max_age_hours}"
                )
            
            if response.get("success"):
                questions = response.get("questions", [])
                
                if questions:
                    st.success(f"Found {len(questions)} promising questions!")
                    
                    # Summary metrics
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        avg_score = sum(q["score"] for q in questions) / len(questions)
                        st.metric("Avg Score", f"{avg_score:.1f}")
                    with col2:
                        avg_engagement = sum(q["engagement_potential"] for q in questions) / len(questions)
                        st.metric("Avg Engagement", f"{avg_engagement:.1f}")
                    with col3:
                        total_comments = sum(q["num_comments"] for q in questions)
                        st.metric("Total Comments", total_comments)
                    
                    # Display questions
                    for i, q in enumerate(questions[:limit]):
                        with st.expander(f"Q{i+1}: {q['title'][:80]}... (Score: {q['engagement_potential']:.1f})"):
                            col1, col2 = st.columns([3, 1])
                            
                            with col1:
                                st.markdown(f"**Question:** {q['title']}")
                                if q.get('content'):
                                    st.markdown(f"**Content:** {q['content'][:200]}...")
                                st.markdown(f"**Subreddit:** r/{q['subreddit']}")
                                st.markdown(f"**Age:** {q['age_hours']:.1f} hours ago")
                                st.markdown(f"**URL:** [View on Reddit]({q['url']})")
                            
                            with col2:
                                st.metric("Score", q['score'])
                                st.metric("Comments", q['num_comments'])
                                st.metric("Engagement", f"{q['engagement_potential']:.1f}")
                            
                            # Quick reply option
                            if st.button(f"Generate Reply for Q{i+1}", key=f"reply_{i}"):
                                with st.spinner("Generating AI reply..."):
                                    reply_response = make_api_request(
                                        "/api/automation/manual-reply",
                                        method="POST",
                                        data={
                                            "post_id": q["id"],
                                            "question": q["title"] + " " + q.get("content", ""),
                                            "domain": domain,
                                            "expertise_level": "intermediate"
                                        }
                                    )
                                
                                if reply_response.get("success"):
                                    st.success("Reply posted successfully!")
                                    if reply_response.get("comment_url"):
                                        st.markdown(f"[View Reply]({reply_response['comment_url']})")
                                    st.markdown(f"**Answer Preview:** {reply_response.get('answer_preview', 'N/A')}")
                                else:
                                    st.error(f"Reply failed: {reply_response.get('error')}")
                else:
                    st.info("No questions found matching your criteria. Try adjusting your keywords or expanding the time range.")
            else:
                st.error(f"Search failed: {response.get('error')}")
    
    with tab2:
        st.markdown("### Find Active Users in Your Domain")
        st.info("Identify users who frequently ask questions in your expertise area")
        
        col1, col2 = st.columns(2)
        
        with col1:
            user_domain = st.selectbox("Domain", ["education", "tech", "health", "business"], key="user_domain")
            user_subreddits = st.text_input(
                "Subreddits to Analyze",
                placeholder="JEE,NEET,IndianStudents"
            )
        
        with col2:
            time_period = st.slider("Time Period (hours)", 6, 168, 24)
        
        if st.button("Find Active Users", use_container_width=True):
            if not user_subreddits:
                st.error("Please enter subreddits to analyze")
                return
            
            with st.spinner("Analyzing user activity..."):
                response = make_api_request(
                    f"/api/automation/active-users?domain={user_domain}&subreddits={user_subreddits}&time_period_hours={time_period}"
                )
            
            if response.get("success"):
                users = response.get("active_users", [])
                
                if users:
                    st.success(f"Found {len(users)} active users!")
                    
                    for user in users:
                        with st.expander(f"u/{user['username']} ({user['question_count']} questions)"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown(f"**Activity Level:** {user['engagement_level']}")
                                st.markdown(f"**Average Score:** {user.get('average_score', 'N/A')}")
                                st.markdown(f"**Subreddits:** {', '.join(user.get('subreddits', []))}")
                            
                            with col2:
                                st.markdown(f"**Question Count:** {user['question_count']}")
                                st.markdown(f"**Total Score:** {user.get('total_score', 'N/A')}")
                            
                            st.markdown("**Recent Questions:**")
                            for q in user.get('recent_questions', []):
                                st.markdown(f"- {q['question']} (r/{q['subreddit']}, {q['score']} upvotes)")
                else:
                    st.info("No highly active users found in this period")
            else:
                st.error(f"Analysis failed: {response.get('error')}")
    
    with tab3:
        st.markdown("### Trending Topics in Your Domain")
        st.info("Discover what topics are currently popular in your field")
        
        trending_domain = st.selectbox("Domain", ["education", "tech", "restaurant"], key="trending_domain")
        trending_subreddits = st.text_input(
            "Subreddits",
            placeholder="india,JEE,NEET"
        )
        
        if st.button("Get Trending Topics", use_container_width=True):
            with st.spinner("Analyzing trending topics..."):
                response = make_api_request(
                    f"/api/automation/trending-topics?domain={trending_domain}&subreddits={trending_subreddits}&time_period=today"
                )
            
            if response.get("success"):
                trending = response.get("trending", {})
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### Hot Topics")
                    for topic in trending.get("hot_topics", []):
                        engagement_icon = {
                            "high": "🔥",
                            "medium": "📈", 
                            "low": "📊"
                        }.get(topic.get("engagement", "low"), "📊")
                        
                        st.markdown(f"{engagement_icon} **{topic['topic']}** ({topic['mentions']} mentions)")
                
                with col2:
                    st.markdown("#### Rising Keywords")
                    keywords = trending.get("rising_keywords", [])
                    for keyword in keywords:
                        st.markdown(f"• {keyword}")
                    
                    st.markdown("#### Best Posting Times")
                    times = trending.get("best_posting_times", [])
                    for time_slot in times:
                        st.markdown(f"• {time_slot}")
            else:
                st.error(f"Failed to get trending topics: {response.get('error')}")

def automation_analytics_page():
    """Analytics for automation performance"""
    st.title("Automation Analytics")
    
    if st.button("Refresh Analytics", use_container_width=True):
        with st.spinner("Loading analytics..."):
            response = make_api_request("/api/automation/performance-analytics")
        
        if response.get("success"):
            perf = response.get("performance", {})
            
            # Key metrics
            st.markdown("### Key Performance Metrics")
            col1, col2, col3, col4 = st.columns(4)
            
            auto_posts = perf.get("auto_posts", {})
            auto_replies = perf.get("auto_replies", {})
            engagement = perf.get("engagement_metrics", {})
            
            with col1:
                st.metric(
                    "Auto Posts",
                    auto_posts.get("total_this_month", 0),
                    delta=f"{auto_posts.get('success_rate', 0):.1f}% success"
                )
            
            with col2:
                st.metric(
                    "Auto Replies", 
                    auto_replies.get("total_this_month", 0),
                    delta=f"{auto_replies.get('success_rate', 0):.1f}% success"
                )
            
            with col3:
                st.metric(
                    "Karma Gained",
                    engagement.get("karma_gained", 0),
                    delta=f"+{engagement.get('followers_gained', 0)} followers"
                )
            
            with col4:
                st.metric(
                    "Questions Answered",
                    auto_replies.get("questions_answered", 0),
                    delta=f"{auto_replies.get('helpful_votes', 0)} helpful votes"
                )
            
            # Performance charts
            st.markdown("### Performance Breakdown")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Auto-Posting Performance")
                post_data = pd.DataFrame({
                    "Status": ["Successful", "Failed"],
                    "Count": [
                        auto_posts.get("successful_posts", 0),
                        auto_posts.get("failed_posts", 0)
                    ]
                })
                if post_data["Count"].sum() > 0:
                    fig1 = px.pie(post_data, values="Count", names="Status", 
                                title="Post Success Rate",
                                color_discrete_map={"Successful": "#00CC88", "Failed": "#FF6B6B"})
                    st.plotly_chart(fig1, use_container_width=True)
            
            with col2:
                st.markdown("#### Auto-Reply Performance")
                reply_data = pd.DataFrame({
                    "Status": ["Successful", "Failed"],
                    "Count": [
                        auto_replies.get("successful_replies", 0),
                        auto_replies.get("failed_replies", 0)
                    ]
                })
                if reply_data["Count"].sum() > 0:
                    fig2 = px.pie(reply_data, values="Count", names="Status", 
                                title="Reply Success Rate",
                                color_discrete_map={"Successful": "#00CC88", "Failed": "#FF6B6B"})
                    st.plotly_chart(fig2, use_container_width=True)
            
            # Performance insights
            st.markdown("### Performance Insights")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Best Performing Content")
                trending_perf = perf.get("trending_performance", {})
                topics = trending_perf.get("most_engaging_topics", [])
                for topic in topics:
                    st.markdown(f"• {topic}")
            
            with col2:
                st.markdown("#### Optimal Subreddits")
                subreddits = trending_perf.get("optimal_subreddits", [])
                for subreddit in subreddits:
                    st.markdown(f"• {subreddit}")
                
                st.markdown("#### Best Posting Times")
                times = trending_perf.get("best_posting_times", [])
                for time_slot in times:
                    st.markdown(f"• {time_slot}")
            
            # Engagement trends
            st.markdown("### Engagement Trends")
            
            # Mock daily engagement data
            dates = pd.date_range(start="2024-01-01", periods=30, freq="D")
            daily_data = pd.DataFrame({
                "Date": dates,
                "Posts": [random.randint(0, 5) for _ in range(30)],
                "Replies": [random.randint(0, 8) for _ in range(30)],
                "Karma": [random.randint(0, 25) for _ in range(30)]
            })
            
            import random
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=daily_data["Date"], y=daily_data["Posts"], 
                                   mode="lines+markers", name="Daily Posts"))
            fig.add_trace(go.Scatter(x=daily_data["Date"], y=daily_data["Replies"], 
                                   mode="lines+markers", name="Daily Replies"))
            fig.add_trace(go.Scatter(x=daily_data["Date"], y=daily_data["Karma"], 
                                   mode="lines+markers", name="Daily Karma"))
            
            fig.update_layout(title="30-Day Activity Trends", xaxis_title="Date", yaxis_title="Count")
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.error("Failed to load analytics")
            st.json(response)

def bulk_automation_page():
    """Bulk automation operations"""
    st.title("Bulk Automation Operations")
    
    tab1, tab2 = st.tabs(["Bulk Auto-Reply", "Content Scheduler"])
    
    with tab1:
        st.markdown("### Process Multiple Questions at Once")
        st.info("Find and answer multiple relevant questions in one operation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            bulk_domain = st.selectbox("Domain", ["education", "tech", "health", "business"])
            max_replies = st.slider("Maximum Replies", 1, 10, 5)
            
        with col2:
            subreddits_bulk = st.text_input("Subreddits", placeholder="JEE,NEET,IndianStudents")
            keywords_bulk = st.text_input("Keywords", placeholder="help,advice,tips")
        
        if st.button("Find & Process Questions", type="primary"):
            if not subreddits_bulk or not keywords_bulk:
                st.error("Please enter subreddits and keywords")
                return
            
            # Step 1: Find target questions
            with st.spinner("Finding target questions..."):
                find_response = make_api_request(
                    f"/api/automation/target-questions?domain={bulk_domain}&expertise_keywords={keywords_bulk}&subreddits={subreddits_bulk}&min_score=1&max_age_hours=24"
                )
            
            if find_response.get("success"):
                questions = find_response.get("questions", [])[:max_replies]
                
                if questions:
                    st.success(f"Found {len(questions)} questions to process")
                    
                    # Show preview
                    with st.expander("Preview Questions to Answer"):
                        for i, q in enumerate(questions):
                            st.markdown(f"**Q{i+1}:** {q['title']}")
                            st.markdown(f"r/{q['subreddit']} • {q['score']} upvotes • {q['num_comments']} comments")
                    
                    if st.button("Process All Questions", key="bulk_process"):
                        with st.spinner(f"Processing {len(questions)} questions..."):
                            # Show progress
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            bulk_response = make_api_request(
                                "/api/automation/bulk-auto-reply",
                                method="POST",
                                data={
                                    "questions": questions,
                                    "domain": bulk_domain,
                                    "max_replies": max_replies
                                }
                            )
                            
                            progress_bar.progress(100)
                        
                        if bulk_response.get("success"):
                            results = bulk_response.get("results", [])
                            successful = bulk_response.get("successful_replies", 0)
                            
                            st.success(f"Bulk processing complete! {successful}/{len(results)} replies posted successfully")
                            
                            # Show results
                            for result in results:
                                if result["status"] == "success":
                                    st.success(f"✅ Reply posted: {result.get('reply_url', 'URL not available')}")
                                else:
                                    st.error(f"❌ Failed: {result.get('error', 'Unknown error')}")
                        else:
                            st.error(f"Bulk processing failed: {bulk_response.get('error')}")
                else:
                    st.info("No suitable questions found for bulk processing")
            else:
                st.error("Failed to find questions")
    
    with tab2:
        st.markdown("### Content Scheduler")
        st.info("Schedule multiple posts across different times and subreddits")
        
        col1, col2 = st.columns(2)
        
        with col1:
            schedule_domain = st.selectbox("Domain", ["education", "tech", "health"], key="schedule_domain")
            content_count = st.slider("Number of Posts to Schedule", 1, 10, 3)
            
        with col2:
            schedule_subreddits = st.multiselect(
                "Target Subreddits",
                ["india", "JEE", "NEET", "IndianStudents", "developersIndia", "programming"],
                default=["india"]
            )
        
        if st.button("Generate Scheduled Content", type="primary"):
            st.info("Content scheduling feature demonstrates how posts would be distributed:")
            
            # Mock scheduled content
            scheduled_posts = [
                {"time": "09:00", "subreddit": "JEE", "title": "5 Physics Tips for JEE Main 2024"},
                {"time": "14:00", "subreddit": "IndianStudents", "title": "Time Management During Board Exams"},
                {"time": "19:00", "subreddit": "india", "title": "Career Options After Engineering in 2024"}
            ]
            
            st.markdown("**Example Schedule:**")
            for post in scheduled_posts[:content_count]:
                st.markdown(f"- {post['time']}: Post about '{post['title']}' to r/{post['subreddit']}")

# Add to main navigation in dev_interface.py:
def update_main_navigation():
    """Update your main navigation to include automation pages"""
    return [
        "Reddit Testing",
        "AI Content Generator", 
        "Question Monitor",
        "Auto-Reply Demo",
        "Domain Content",
        "Automation Setup",        # NEW
        "Question Discovery",      # NEW
        "Automation Analytics",    # NEW
        "Bulk Operations",         # NEW
        "Analytics"
    ]

# Integration example for dev_interface.py:
def integrate_automation_pages():
    """
    Add these cases to your page handler in main_dashboard():
    
    elif page == "Automation Setup":
        automation_setup_page()
    elif page == "Question Discovery":
        question_discovery_page()
    elif page == "Automation Analytics":
        automation_analytics_page()
    elif page == "Bulk Operations":
        bulk_automation_page()
    """
    pass