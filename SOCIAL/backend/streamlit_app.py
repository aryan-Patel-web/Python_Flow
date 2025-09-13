# """
# Updated Streamlit Development Interface for Multi-Platform Automation System
# Compatible with OAuth-based Reddit integration
# """

# import streamlit as st
# import requests
# import json
# import pandas as pd
# import plotly.express as px
# from datetime import datetime, timedelta
# import time
# from typing import Dict, List, Any
# import logging

# # Configure page
# st.set_page_config(
#     page_title="Multi-Platform Automation System",
#     page_icon="🚀",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # API Configuration
# API_BASE_URL = "http://localhost:8000"

# # Session state initialization
# if 'authenticated' not in st.session_state:
#     st.session_state.authenticated = True  # Skip auth for testing
# if 'reddit_connected' not in st.session_state:
#     st.session_state.reddit_connected = False
# if 'reddit_username' not in st.session_state:
#     st.session_state.reddit_username = None

# def make_api_request(endpoint: str, method: str = "GET", data: dict = None, auth_required: bool = False) -> dict:
#     """
#     Make API request with error handling (auth disabled for testing)
#     """
#     try:
#         url = f"{API_BASE_URL}{endpoint}"
#         headers = {"Content-Type": "application/json"}
        
#         if method == "GET":
#             response = requests.get(url, headers=headers, params=data)
#         elif method == "POST":
#             response = requests.post(url, headers=headers, json=data)
#         elif method == "PUT":
#             response = requests.put(url, headers=headers, json=data)
#         elif method == "DELETE":
#             response = requests.delete(url, headers=headers)
#         else:
#             raise ValueError(f"Unsupported HTTP method: {method}")
        
#         return response.json()
        
#     except requests.exceptions.RequestException as e:
#         logger.error(f"API request failed: {e}")
#         return {"success": False, "error": str(e)}
#     except Exception as e:
#         logger.error(f"Unexpected error in API request: {e}")
#         return {"success": False, "error": str(e)}

# def main_dashboard():
#     """Main application dashboard"""
    
#     # Sidebar
#     with st.sidebar:
#         st.title("Reddit Automation Tester")
        
#         # System health check
#         st.markdown("### 🔗 System Status")
#         if st.button("Check System Health"):
#             with st.spinner("Checking system..."):
#                 health = make_api_request("/health")
#                 if health.get("success"):
#                     st.success("All systems operational!")
#                     services = health.get("health", {}).get("services", {})
#                     for service, status in services.items():
#                         emoji = "🟢" if status.get("success") else "🔴"
#                         st.markdown(f"{service}: {emoji}")
#                 else:
#                     st.error(f"System health check failed: {health.get('error')}")
        
#         # Reddit OAuth Connection
#         st.markdown("### 📱 Reddit OAuth")
#         if not st.session_state.reddit_connected:
#             if st.button("Connect Reddit Account", type="primary"):
#                 with st.spinner("Getting OAuth URL..."):
#                     oauth_response = make_api_request("/api/oauth/reddit/authorize")
#                     if oauth_response.get("success"):
#                         st.markdown("**Click the link below to authorize:**")
#                         st.markdown(f"[Connect Reddit Account]({oauth_response['redirect_url']})")
#                         st.info("After authorization, you'll be redirected back to test posting features")
#                     else:
#                         st.error(f"OAuth setup failed: {oauth_response.get('error')}")
#         else:
#             st.success(f"Connected as: {st.session_state.reddit_username}")
#             if st.button("Disconnect"):
#                 st.session_state.reddit_connected = False
#                 st.session_state.reddit_username = None
#                 st.rerun()
        
#         # Navigation
#         st.markdown("### 📊 Navigation")
#         page = st.selectbox(
#             "Select Feature",
#             [
#                 "Reddit Testing",
#                 "AI Content Generator", 
#                 "Question Monitor",
#                 "Auto-Reply Demo",
#                 "Domain Content",
#                 "Analytics"
#             ]
#         )
    
#     # Main content area
#     if page == "Reddit Testing":
#         reddit_testing_page()
#     elif page == "AI Content Generator":
#         ai_content_page()
#     elif page == "Question Monitor":
#         question_monitor_page()
#     elif page == "Auto-Reply Demo":
#         auto_reply_demo_page()
#     elif page == "Domain Content":
#         domain_content_page()
#     elif page == "Analytics":
#         analytics_page()

# def reddit_testing_page():
#     """Reddit automation testing page"""
#     st.title("📱 Reddit Automation Testing")
    
#     tab1, tab2, tab3 = st.tabs(["Manual Posting", "Auto-Post Demo", "OAuth Status"])
    
#     with tab1:
#         st.markdown("### Manual Reddit Post Testing")
        
#         col1, col2 = st.columns([2, 1])
        
#         with col1:
#             subreddit = st.selectbox(
#                 "Select Subreddit",
#                 ["test", "india", "indiaspeaks", "bangalore", "delhi", "mumbai", "AskReddit"]
#             )
            
#             title = st.text_input("Post Title", placeholder="Enter your post title...")
#             content = st.text_area("Post Content", placeholder="Enter your post content...", height=150)
            
#             col_lang, col_tone = st.columns(2)
#             with col_lang:
#                 language = st.selectbox("Language", ["en", "hi", "ta", "te", "bn"])
#             with col_tone:
#                 content_type = st.selectbox("Content Type", ["text", "link"])
        
#         with col2:
#             st.markdown("#### Post Preview")
#             if title and content:
#                 st.markdown(f"**Title:** {title}")
#                 st.markdown(f"**Content:** {content[:100]}...")
#                 st.markdown(f"**Subreddit:** r/{subreddit}")
#                 st.markdown(f"**Language:** {language}")
            
#             st.markdown("#### Requirements")
#             if st.session_state.reddit_connected:
#                 st.success("✅ Reddit Connected")
#             else:
#                 st.warning("❌ Connect Reddit first")
        
#         if st.button("Test Post to Reddit", type="primary", use_container_width=True):
#             if not title or not content:
#                 st.error("Please enter both title and content")
#                 return
                
#             with st.spinner("Posting to Reddit..."):
#                 response = make_api_request(
#                     "/api/reddit/post",
#                     method="POST",
#                     data={
#                         "subreddit": subreddit,
#                         "title": title,
#                         "content": content,
#                         "language": language,
#                         "content_type": content_type
#                     }
#                 )
            
#             if response.get("success"):
#                 st.success(f"Post created successfully!")
#                 if response.get("post_url"):
#                     st.markdown(f"[View Post]({response['post_url']})")
#                 st.json(response)
#             else:
#                 st.error(f"Posting failed: {response.get('message', 'Unknown error')}")
#                 if response.get("action_required") == "oauth_connection":
#                     st.info("Please connect your Reddit account using OAuth first")
#                 st.json(response)
    
#     with tab2:
#         st.markdown("### Auto-Post Demo (Domain-Based)")
        
#         st.info("This demonstrates how the system would automatically generate and post domain-specific content")
        
#         col1, col2 = st.columns(2)
        
#         with col1:
#             domain = st.selectbox(
#                 "Business Domain",
#                 ["education", "restaurant", "tech", "health", "business"]
#             )
            
#             business_type = st.text_input(
#                 "Business Type",
#                 placeholder="e.g., JEE coaching center, South Indian restaurant..."
#             )
            
#             target_audience = st.selectbox(
#                 "Target Audience",
#                 ["indian_students", "food_lovers", "tech_professionals", "health_conscious", "entrepreneurs"]
#             )
        
#         with col2:
#             content_style = st.selectbox(
#                 "Content Style",
#                 ["engaging", "informative", "promotional", "helpful"]
#             )
            
#             language = st.selectbox("Content Language", ["en", "hi"], key="auto_lang")
            
#             num_posts = st.slider("Number of Posts to Generate", 1, 5, 1)
        
#         if st.button("Generate Auto-Posts", type="primary", use_container_width=True):
#             if not business_type:
#                 st.error("Please enter your business type")
#                 return
            
#             with st.spinner(f"Generating {num_posts} domain-specific posts..."):
#                 for i in range(num_posts):
#                     st.markdown(f"#### Generated Post {i+1}")
                    
#                     # Generate domain content
#                     response = make_api_request(
#                         "/api/ai/generate-domain-content",
#                         method="POST",
#                         data={
#                             "domain": domain,
#                             "business_type": business_type,
#                             "target_audience": target_audience,
#                             "language": language,
#                             "content_style": content_style
#                         }
#                     )
                    
#                     if response.get("success"):
#                         st.success(f"Content generated for {domain} domain!")
                        
#                         with st.expander(f"View Generated Content {i+1}"):
#                             st.markdown(f"**Title:** {response.get('title', 'No title')}")
#                             st.markdown(f"**Body:** {response.get('body', 'No content')}")
#                             st.markdown(f"**Suggested Subreddits:** {', '.join(response.get('suggested_subreddits', []))}")
#                             st.markdown(f"**Keywords:** {', '.join(response.get('keywords', []))}")
                        
#                         # Simulate auto-posting
#                         if st.session_state.reddit_connected:
#                             st.info("✅ Would auto-post to recommended subreddits")
#                         else:
#                             st.warning("❌ Connect Reddit to enable auto-posting")
#                     else:
#                         st.error(f"Content generation failed: {response.get('error')}")
                    
#                     time.sleep(1)  # Small delay between generations
    
#     with tab3:
#         st.markdown("### Reddit OAuth Connection Status")
        
#         # Test OAuth endpoints
#         if st.button("Test OAuth Authorization URL"):
#             with st.spinner("Testing OAuth setup..."):
#                 response = make_api_request("/api/oauth/reddit/authorize")
#                 if response.get("success"):
#                     st.success("OAuth URL generated successfully!")
#                     st.code(response["redirect_url"])
#                     st.markdown("**This URL would redirect users to Reddit for authorization**")
#                 else:
#                     st.error(f"OAuth setup failed: {response.get('error')}")
#                 st.json(response)
        
#         st.markdown("### Manual OAuth Testing")
#         st.markdown("To test the full OAuth flow:")
#         st.markdown("1. Click 'Test OAuth Authorization URL' above")
#         st.markdown("2. Copy the generated URL and visit it in a new tab")
#         st.markdown("3. Authorize the application on Reddit")
#         st.markdown("4. Check the callback handling")
        
#         # Simulate connected state for testing
#         col1, col2 = st.columns(2)
#         with col1:
#             if st.button("Simulate Reddit Connected"):
#                 st.session_state.reddit_connected = True
#                 st.session_state.reddit_username = "test_user"
#                 st.success("Simulated Reddit connection!")
#                 st.rerun()
        
#         with col2:
#             if st.button("Clear Connection"):
#                 st.session_state.reddit_connected = False
#                 st.session_state.reddit_username = None
#                 st.success("Connection cleared!")
#                 st.rerun()

# def question_monitor_page():
#     """Question monitoring and auto-reply testing"""
#     st.title("🔍 Reddit Question Monitor")
    
#     st.markdown("### Monitor Reddit Questions for Auto-Reply Opportunities")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         subreddits_input = st.text_input(
#             "Subreddits to Monitor",
#             value="AskReddit,explainlikeimfive,NoStupidQuestions,india",
#             help="Comma-separated list of subreddits"
#         )
        
#         keywords_input = st.text_input(
#             "Filter Keywords",
#             value="help,how,what,why,study,learn",
#             help="Questions containing these keywords"
#         )
    
#     with col2:
#         limit = st.slider("Number of Questions", 5, 25, 10)
        
#         domain_filter = st.selectbox(
#             "Domain Focus",
#             ["all", "education", "tech", "health", "business"]
#         )
    
#     if st.button("Find Questions to Answer", type="primary", use_container_width=True):
#         with st.spinner("Scanning Reddit for questions..."):
#             response = make_api_request(
#                 "/api/reddit/questions",
#                 data={
#                     "subreddits": subreddits_input,
#                     "keywords": keywords_input,
#                     "limit": limit
#                 }
#             )
        
#         if response.get("success"):
#             questions = response.get("questions", [])
            
#             if questions:
#                 st.success(f"Found {len(questions)} relevant questions!")
                
#                 for i, question in enumerate(questions):
#                     with st.expander(f"Q{i+1}: {question['title'][:80]}..."):
#                         col1, col2 = st.columns([2, 1])
                        
#                         with col1:
#                             st.markdown(f"**Subreddit:** r/{question['subreddit']}")
#                             st.markdown(f"**Question:** {question['title']}")
#                             st.markdown(f"**Content:** {question['content'][:300]}...")
#                             st.markdown(f"**Score:** {question['score']} | **Comments:** {question['num_comments']}")
                        
#                         with col2:
#                             st.markdown(f"**Author:** {question['author']}")
#                             st.markdown(f"**URL:** [View]({question['url']})")
                            
#                             # Auto-reply simulation
#                             if st.button(f"Generate Auto-Reply", key=f"reply_{i}"):
#                                 with st.spinner("Generating domain-specific answer..."):
#                                     # Simulate AI answer generation
#                                     time.sleep(2)
#                                     sample_answer = f"""This is a great question about {question['title'][:30]}! 

# Based on my experience, here's what I'd suggest:

# 1. Start with understanding the fundamentals
# 2. Practice regularly with real examples  
# 3. Don't hesitate to ask for clarification

# Feel free to reach out if you need more specific guidance!"""
                                    
#                                     st.success("Auto-reply generated!")
#                                     st.text_area("Generated Answer:", sample_answer, height=150, key=f"answer_{i}")
                                    
#                                     if st.session_state.reddit_connected:
#                                         st.info("✅ Would post this reply automatically")
#                                     else:
#                                         st.warning("❌ Connect Reddit to enable auto-reply")
#             else:
#                 st.info("No questions found matching your criteria. Try different keywords or subreddits.")
#         else:
#             st.error(f"Failed to fetch questions: {response.get('error')}")

# def auto_reply_demo_page():
#     """Auto-reply demonstration"""
#     st.title("🤖 Auto-Reply System Demo")
    
#     st.markdown("### How Auto-Reply Works")
    
#     tab1, tab2, tab3 = st.tabs(["Process Demo", "Manual Reply", "Bulk Processing"])
    
#     with tab1:
#         st.markdown("#### Auto-Reply Process Flow")
        
#         col1, col2, col3 = st.columns(3)
        
#         with col1:
#             st.markdown("**1. Monitor**")
#             st.info("🔍 Scan subreddits for questions")
#             if st.button("Start Monitoring Demo"):
#                 with st.spinner("Monitoring subreddits..."):
#                     time.sleep(2)
#                     st.success("Found 15 new questions!")
        
#         with col2:
#             st.markdown("**2. Filter**")
#             st.info("🎯 Match domain expertise")
#             if st.button("Apply Filters"):
#                 with st.spinner("Filtering questions..."):
#                     time.sleep(1)
#                     st.success("5 questions match your expertise!")
        
#         with col3:
#             st.markdown("**3. Respond**")
#             st.info("✍️ Generate and post answers")
#             if st.button("Auto-Reply"):
#                 with st.spinner("Generating responses..."):
#                     time.sleep(2)
#                     st.success("Posted 3 helpful answers!")
        
#         st.markdown("---")
#         st.markdown("#### Domain-Specific Auto-Reply")
        
#         domain = st.selectbox("Your Expertise Domain", ["education", "tech", "health", "business"])
#         expertise_level = st.selectbox("Your Expertise Level", ["beginner", "intermediate", "expert"])
        
#         if st.button("Simulate Domain Auto-Reply"):
#             with st.spinner(f"Finding {domain} questions..."):
#                 time.sleep(2)
                
#                 # Mock domain-specific questions
#                 domain_questions = {
#                     "education": "How do I prepare for JEE Main in 6 months?",
#                     "tech": "What's the best way to learn React.js?", 
#                     "health": "What are good exercises for back pain?",
#                     "business": "How to start a small business in India?"
#                 }
                
#                 question = domain_questions.get(domain, "Generic question")
                
#                 st.success(f"Found question: '{question}'")
                
#                 # Generate domain-specific answer
#                 time.sleep(1)
#                 st.info("Generated expert-level answer based on your domain knowledge")
#                 st.success("Auto-posted reply with domain authority!")
    
#     with tab2:
#         st.markdown("#### Manual Reply Testing")
        
#         post_id = st.text_input("Reddit Post ID", placeholder="Enter post ID to reply to...")
        
#         question_preview = st.text_area(
#             "Question Preview",
#             placeholder="Paste the question here to see how AI would respond...",
#             height=100
#         )
        
#         if question_preview:
#             if st.button("Generate Answer"):
#                 with st.spinner("Generating AI answer..."):
#                     response = make_api_request(
#                         "/api/ai/generate-answer",
#                         method="POST",
#                         data={
#                             "platform": "reddit",
#                             "question": question_preview,
#                             "language": "en",
#                             "expertise_level": "intermediate"
#                         }
#                     )
                
#                 if response.get("success"):
#                     st.success("Answer generated!")
#                     answer = response.get("answer", "No answer generated")
#                     st.text_area("Generated Answer:", answer, height=200)
                    
#                     if post_id and st.session_state.reddit_connected:
#                         if st.button("Post This Answer"):
#                             st.success("Answer would be posted to Reddit!")
#                     else:
#                         st.info("Enter post ID and connect Reddit to post answers")
#                 else:
#                     st.error(f"Answer generation failed: {response.get('error')}")
    
#     with tab3:
#         st.markdown("#### Bulk Auto-Reply Processing")
        
#         batch_size = st.slider("Batch Size", 1, 10, 5)
#         delay_between = st.slider("Delay Between Replies (seconds)", 10, 300, 60)
        
#         if st.button("Start Bulk Processing Demo"):
#             progress_bar = st.progress(0)
#             status_text = st.empty()
            
#             for i in range(batch_size):
#                 progress = (i + 1) / batch_size
#                 progress_bar.progress(progress)
#                 status_text.text(f"Processing question {i+1}/{batch_size}...")
                
#                 time.sleep(1)  # Simulate processing
                
#                 st.success(f"✅ Answered question {i+1}")
            
#             status_text.text("Bulk processing complete!")
#             st.success(f"Successfully processed {batch_size} questions!")

# def domain_content_page():
#     """Domain-specific content generation"""
#     st.title("🏢 Domain-Specific Content Generation")
    
#     st.markdown("### Generate Content for Indian Business Domains")
    
#     col1, col2 = st.columns(2)
    
#     with col1:
#         domain = st.selectbox(
#             "Business Domain",
#             ["education", "restaurant", "tech", "health", "business"]
#         )
        
#         business_type = st.text_input("Specific Business Type", placeholder="e.g., 'IIT JEE coaching center'")
        
#         content_topics = {
#             "education": ["study tips", "exam preparation", "career guidance", "course recommendations"],
#             "restaurant": ["new dishes", "food reviews", "cooking tips", "restaurant updates"],
#             "tech": ["tutorials", "tech news", "product reviews", "job opportunities"],
#             "health": ["fitness tips", "nutrition advice", "wellness guides", "health awareness"],
#             "business": ["startup advice", "investment tips", "market insights", "success stories"]
#         }
        
#         suggested_topics = content_topics.get(domain, [])
#         topic = st.selectbox("Content Topic", suggested_topics + ["custom"])
        
#         if topic == "custom":
#             topic = st.text_input("Custom Topic")
    
#     with col2:
#         language = st.selectbox("Content Language", ["en", "hi"])
#         content_style = st.selectbox("Content Style", ["engaging", "informative", "promotional"])
#         target_audience = st.selectbox("Target Audience", ["students", "professionals", "general_public"])
        
#         # Show domain-specific subreddits
#         if st.button("Show Recommended Subreddits"):
#             response = make_api_request(f"/api/reddit/domain-subreddits?domain={domain}")
#             if response.get("success"):
#                 st.success("Recommended subreddits:")
#                 subreddits = response.get("subreddits", [])
#                 st.write(", ".join([f"r/{sub}" for sub in subreddits]))
#             else:
#                 st.error("Failed to get subreddit recommendations")
    
#     if st.button("Generate Domain Content", type="primary", use_container_width=True):
#         if not business_type or not topic:
#             st.error("Please fill in business type and topic")
#             return
        
#         with st.spinner("Generating domain-specific content..."):
#             response = make_api_request(
#                 "/api/ai/generate-domain-content",
#                 method="POST",
#                 data={
#                     "domain": domain,
#                     "business_type": business_type,
#                     "target_audience": target_audience,
#                     "language": language,
#                     "content_style": content_style
#                 }
#             )
        
#         if response.get("success"):
#             st.success("Content generated successfully!")
            
#             col1, col2 = st.columns([2, 1])
            
#             with col1:
#                 st.markdown("#### Generated Content")
#                 st.markdown(f"**Title:** {response.get('title', 'No title')}")
#                 st.markdown("**Body:**")
#                 st.text_area("", response.get('body', 'No content'), height=200, key="domain_content")
            
#             with col2:
#                 st.markdown("#### Metadata")
#                 st.markdown(f"**Domain:** {response.get('domain')}")
#                 st.markdown(f"**Language:** {response.get('language')}")
#                 st.markdown(f"**Keywords:**")
#                 for keyword in response.get('keywords', []):
#                     st.markdown(f"- {keyword}")
                
#                 st.markdown(f"**Suggested Subreddits:**")
#                 for subreddit in response.get('suggested_subreddits', []):
#                     st.markdown(f"- r/{subreddit}")
            
#             # Auto-post option
#             if st.session_state.reddit_connected:
#                 if st.button("Auto-Post to Recommended Subreddits"):
#                     st.success("Content would be posted to recommended subreddits!")
#             else:
#                 st.info("Connect Reddit to enable auto-posting")
#         else:
#             st.error(f"Content generation failed: {response.get('error')}")

# def ai_content_page():
#     """AI content generation testing"""
#     st.title("🤖 AI Content Generator Testing")
    
#     tab1, tab2 = st.tabs(["General Content", "Content Suggestions"])
    
#     with tab1:
#         col1, col2 = st.columns(2)
        
#         with col1:
#             platform = st.selectbox("Platform", ["reddit", "twitter", "stackoverflow", "webmd"])
#             content_type = st.selectbox("Content Type", ["post", "comment", "answer", "tweet"])
#             topic = st.text_input("Topic", placeholder="Enter content topic...")
#             tone = st.selectbox("Tone", ["professional", "casual", "friendly", "informative"])
        
#         with col2:
#             language = st.selectbox("Language", ["en", "hi", "ta", "te", "bn"])
#             target_audience = st.text_input("Target Audience", placeholder="e.g., Indian students")
#             domain = st.selectbox("Domain (Optional)", ["", "education", "tech", "health", "business"])
            
#         additional_context = st.text_area("Additional Context", placeholder="Any specific requirements...")
        
#         if st.button("Generate Content", use_container_width=True):
#             if not topic:
#                 st.error("Please enter a topic")
#                 return
            
#             with st.spinner("Generating AI content..."):
#                 data = {
#                     "platform": platform,
#                     "content_type": content_type,
#                     "topic": topic,
#                     "tone": tone,
#                     "language": language,
#                     "target_audience": target_audience,
#                     "additional_context": additional_context
#                 }
#                 if domain:
#                     data["domain"] = domain
                
#                 response = make_api_request("/api/ai/generate-content", method="POST", data=data)
            
#             if response.get("success"):
#                 st.success("Content generated successfully!")
                
#                 col1, col2 = st.columns([2, 1])
#                 with col1:
#                     st.text_area("Generated Content:", response.get("content", ""), height=200)
#                 with col2:
#                     st.metric("Word Count", response.get("word_count", 0))
#                     st.metric("Character Count", response.get("character_count", 0))
#             else:
#                 st.error(f"Generation failed: {response.get('error')}")
    
#     with tab2:
#         st.markdown("### Content Suggestions by Domain")
        
#         col1, col2 = st.columns(2)
#         with col1:
#             platform = st.selectbox("Platform", ["reddit", "twitter", "stackoverflow"], key="suggest_platform")
#             domain = st.selectbox("Domain", ["education", "tech", "health", "business"], key="suggest_domain")
#         with col2:
#             language = st.selectbox("Language", ["en", "hi"], key="suggest_language")
        
#         if st.button("Get Content Suggestions"):
#             response = make_api_request(f"/api/content/suggestions?platform={platform}&domain={domain}&language={language}")
            
#             if response.get("success"):
#                 st.success("Suggestions loaded!")
                
#                 col1, col2 = st.columns(2)
#                 with col1:
#                     st.markdown("#### Content Ideas")
#                     for suggestion in response.get("content_suggestions", []):
#                         st.markdown(f"• {suggestion}")
                
#                 with col2:
#                     st.markdown("#### Trending Topics")
#                     for topic in response.get("trending_topics", []):
#                         st.markdown(f"• {topic}")
#             else:
#                 st.error("Failed to get suggestions")

# def analytics_page():
#     """Analytics and monitoring"""
#     st.title("📊 Analytics Dashboard")
    
#     col1, col2, col3, col4 = st.columns(4)
    
#     with col1:
#         st.metric("Posts Today", 12, delta=3)
#     with col2:
#         st.metric("Total Engagement", 456, delta=45)
#     with col3:
#         st.metric("Auto-Replies", 8, delta=2)
#     with col4:
#         st.metric("Success Rate", "87%", delta="5%")
    
#     # Mock engagement chart
#     dates = pd.date_range(start="2024-01-01", end="2024-01-15", freq="D")
#     data = pd.DataFrame({
#         "Date": dates,
#         "Reddit Posts": [5, 8, 6, 10, 12, 15, 18, 20, 25, 22, 28, 30, 35, 32, 28],
#         "Auto-Replies": [2, 3, 1, 4, 5, 3, 6, 4, 7, 5, 8, 6, 9, 7, 5]
#     })
    
#     fig = px.line(data.melt(id_vars=["Date"], var_name="Activity", value_name="Count"),
#                   x="Date", y="Count", color="Activity", title="Daily Activity")
#     st.plotly_chart(fig, use_container_width=True)

# # Main app logic
# if __name__ == "__main__":
#     if st.session_state.authenticated:
#         main_dashboard()
#     else:
#         # Skip login for testing
#         st.session_state.authenticated = True
#         main_dashboard()