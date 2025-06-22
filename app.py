import streamlit as st
import json
from datetime import datetime
# import streamlit.components.v1 as components # No longer needed
from st_copy_to_clipboard import st_copy_to_clipboard # Import the component

# Page config MUST be the first Streamlit command
st.set_page_config(layout="wide", page_title="Social Media Dashboard")

# Initialize session state for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = "LinkedIn Posts"

# Sidebar for navigation with buttons
st.sidebar.title("Navigation")
if st.sidebar.button("LinkedIn Posts", use_container_width=True):
    st.session_state.current_page = "LinkedIn Posts"
if st.sidebar.button("Twitter Results", use_container_width=True):
    st.session_state.current_page = "Twitter Results"
if st.sidebar.button("Search Research", use_container_width=True):
    st.session_state.current_page = "Search Research"
if st.sidebar.button("Talking Points", use_container_width=True):
    st.session_state.current_page = "Talking Points"
if st.sidebar.button("Typefully Publishing", use_container_width=True):
    st.session_state.current_page = "Typefully Publishing"

page = st.session_state.current_page

if page == "LinkedIn Posts":
    # Load the LinkedIn data
    try:
        # Ensure the path to the JSON file is correct.
        # If app.py is in the root of your project, and the JSON file is also in the root,
        # then '_cache_editor_linkedin_output.json' is correct.
        # If app.py is in a subdirectory, you might need to adjust the path, e.g., '../_cache_editor_linkedin_output.json'
        with open('_cache_editor_linkedin_output.json', 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        st.error("Error: '_cache_editor_linkedin_output.json' not found. Please ensure the file exists and the path is correct relative to 'app.py'.")
        st.stop()
    except json.JSONDecodeError:
        st.error("Error: Could not decode JSON from '_cache_editor_linkedin_output.json'. Please check the file format.")
        st.stop()

    st.title("LinkedIn Post Suggestions Dashboard")
    st.markdown("Displaying topics and generated LinkedIn posts from `_cache_editor_linkedin_output.json`")

    if not data:
        st.warning("No data found in the JSON file.")
    else:
        # Using columns for a more structured layout
        num_columns = 2 # You can adjust the number of columns
        cols = st.columns(num_columns)
        
        for i, item in enumerate(data):
            col_index = i % num_columns
            with cols[col_index]:
                st.subheader(f"Topic {i+1}: {item.get('topic', 'No Topic Title')}")
                
                with st.expander("View LinkedIn Post", expanded=False): # Make posts collapsible
                    post_text_to_display = item.get('linkedin_post', 'No post content available.')
                    st.markdown(post_text_to_display)

                    post_text_for_copy = item.get('linkedin_post', '') 
                    # Use the st_copy_to_clipboard component
                    # Providing a unique key is good practice for components in a loop
                    st_copy_to_clipboard(post_text_for_copy, key=f"copy_btn_{i}") 

                st.markdown("---") # Visual separator for each item within a column 

elif page == "Twitter Results":
    # Load the Twitter data
    try:
        with open('_cache_twitter_results.json', 'r') as f:
            twitter_data = json.load(f)
    except FileNotFoundError:
        st.error("Error: '_cache_twitter_results.json' not found. Please ensure the file exists and the path is correct relative to 'app.py'.")
        st.stop()
    except json.JSONDecodeError:
        st.error("Error: Could not decode JSON from '_cache_twitter_results.json'. Please check the file format.")
        st.stop()

    st.title("Twitter Search Results")
    st.markdown("Browse through Twitter posts related to your search queries")
    
    # Add filters
    col1, col2, col3 = st.columns(3)
    with col1:
        min_followers = st.number_input("Min followers", min_value=0, value=0, step=1000)
    with col2:
        min_engagement = st.number_input("Min total engagement", min_value=0, value=0, step=10)
    with col3:
        sort_by = st.selectbox("Sort by", ["Recent", "Followers", "Engagement", "Retweets"])

    if not twitter_data:
        st.warning("No Twitter data found in the JSON file.")
    else:
        # Filter and sort data
        filtered_data = []
        for item in twitter_data:
            followers = item.get('followers_count', 0)
            engagement = (item.get('favorite_count', 0) + 
                         item.get('retweet_count', 0) + 
                         item.get('reply_count', 0))
            
            if followers >= min_followers and engagement >= min_engagement:
                filtered_data.append(item)
        
        # Sort data
        if sort_by == "Followers":
            filtered_data.sort(key=lambda x: x.get('followers_count', 0), reverse=True)
        elif sort_by == "Engagement":
            filtered_data.sort(key=lambda x: (x.get('favorite_count', 0) + 
                                            x.get('retweet_count', 0) + 
                                            x.get('reply_count', 0)), reverse=True)
        elif sort_by == "Retweets":
            filtered_data.sort(key=lambda x: x.get('retweet_count', 0), reverse=True)
        # Default is Recent (original order)
        
        st.write(f"Showing {len(filtered_data)} out of {len(twitter_data)} tweets")
        
        # Display tweets
        for i, tweet in enumerate(filtered_data):
            with st.container():
                # Create header with user info and engagement metrics
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown(f"**@{tweet.get('screen_name', 'Unknown')}** ({tweet.get('followers_count', 0):,} followers)")
                
                with col2:
                    created_at = tweet.get('created_at', '')
                    if created_at:
                        try:
                            # Parse the date and format it nicely
                            dt = datetime.strptime(created_at, "%a %b %d %H:%M:%S %z %Y")
                            formatted_date = dt.strftime("%b %d, %Y")
                            st.write(f"📅 {formatted_date}")
                        except:
                            st.write(f"📅 {created_at}")
                
                with col3:
                    engagement = (tweet.get('favorite_count', 0) + 
                                tweet.get('retweet_count', 0) + 
                                tweet.get('reply_count', 0))
                    st.write(f"🔥 {engagement} total")
                
                # Tweet content
                snippet = tweet.get('snippet', 'No content available')
                st.markdown(f"*{snippet}*")
                
                # Engagement details
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.write(f"❤️ {tweet.get('favorite_count', 0)}")
                with col2:
                    st.write(f"🔄 {tweet.get('retweet_count', 0)}")
                with col3:
                    st.write(f"💬 {tweet.get('reply_count', 0)}")
                with col4:
                    st.write(f"🔗 {tweet.get('quote_count', 0)}")
                with col5:
                    url = tweet.get('url', '')
                    if url:
                        st.markdown(f"[View Tweet]({url})")
                
                # Copy button for the snippet
                if snippet:
                    st_copy_to_clipboard(snippet, key=f"twitter_copy_{i}")
                
                st.markdown("---") 

elif page == "Search Research":
    # Load the Search Agent data
    try:
        with open('_cache_search_agent_raw_api_response.json', 'r') as f:
            search_data = json.load(f)
    except FileNotFoundError:
        st.error("Error: '_cache_search_agent_raw_api_response.json' not found. Please ensure the file exists and the path is correct relative to 'app.py'.")
        st.stop()
    except json.JSONDecodeError:
        st.error("Error: Could not decode JSON from '_cache_search_agent_raw_api_response.json'. Please check the file format.")
        st.stop()

    st.title("Search Research Results")
    st.markdown("AI-generated research content with citations and sources")
    
    if not search_data:
        st.warning("No search data found in the JSON file.")
    else:
        # Extract the main content
        choices = search_data.get('choices', [])
        if choices:
            message = choices[0].get('message', {})
            content = message.get('content', '')
            
            # Display main content
            st.markdown("## Research Content")
            if content:
                st.markdown(content)
                
                # Copy button for the entire content
                st_copy_to_clipboard(content, key="research_content_copy")
            else:
                st.warning("No content found in the response.")
            
            st.markdown("---")
            
            # Display citations
            citations = search_data.get('citations', [])
            if citations:
                st.markdown("## Citations")
                for i, citation in enumerate(citations, 1):
                    st.markdown(f"{i}. [{citation}]({citation})")
            
            st.markdown("---")
            
            # Display search results with more detail
            search_results = search_data.get('search_results', [])
            if search_results:
                st.markdown("## Source Articles")
                
                for i, result in enumerate(search_results):
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            title = result.get('title', 'No title')
                            url = result.get('url', '')
                            if url:
                                st.markdown(f"**[{title}]({url})**")
                            else:
                                st.markdown(f"**{title}**")
                        
                        with col2:
                            date = result.get('date', 'No date')
                            if date:
                                try:
                                    # Try to parse and format the date
                                    dt = datetime.strptime(date, "%Y-%m-%d")
                                    formatted_date = dt.strftime("%b %d, %Y")
                                    st.write(f"📅 {formatted_date}")
                                except:
                                    st.write(f"📅 {date}")
                            else:
                                st.write("📅 No date")
                        
                        # Copy button for the URL
                        if url:
                            st_copy_to_clipboard(url, key=f"search_url_copy_{i}")
                        
                        st.markdown("---")
            
            # Display usage information
            usage = search_data.get('usage', {})
            if usage:
                st.markdown("## API Usage")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Completion Tokens", usage.get('completion_tokens', 0))
                with col2:
                    st.metric("Prompt Tokens", usage.get('prompt_tokens', 0))
                with col3:
                    st.metric("Total Tokens", usage.get('total_tokens', 0))
                with col4:
                    st.metric("Search Context", usage.get('search_context_size', 'N/A'))
            else:
                st.warning("No response choices found in the data.")

elif page == "Talking Points":
    # Load the Reviewer Output data
    try:
        with open('_cache_reviewer_output.json', 'r') as f:
            reviewer_data = json.load(f)
    except FileNotFoundError:
        st.error("Error: '_cache_reviewer_output.json' not found. Please ensure the file exists and the path is correct relative to 'app.py'.")
        st.stop()
    except json.JSONDecodeError:
        st.error("Error: Could not decode JSON from '_cache_reviewer_output.json'. Please check the file format.")
        st.stop()

    st.title("Marketing Talking Points")
    st.markdown("Distilled topics and key talking points for Tuon.io based on market research")
    
    if not reviewer_data:
        st.warning("No reviewer data found in the JSON file.")
    else:
        # Display Distilled Topics
        distilled_topics = reviewer_data.get('distilled_topics', [])
        if distilled_topics:
            st.markdown("## 🎯 Distilled Market Topics")
            st.markdown("*Key market insights and positioning opportunities based on research*")
            
            for i, topic in enumerate(distilled_topics, 1):
                with st.container():
                    st.markdown(f"### Topic {i}")
                    st.markdown(topic)
                    
                    # Copy button for individual topic
                    st_copy_to_clipboard(topic, key=f"topic_copy_{i}")
                    st.markdown("---")
            
            # Copy all topics button
            all_topics = "\n\n".join([f"Topic {i}: {topic}" for i, topic in enumerate(distilled_topics, 1)])
            st.markdown("### Copy All Topics")
            st_copy_to_clipboard(all_topics, key="all_topics_copy")
        
        st.markdown("---")
        
        # Display Talking Points
        talking_points = reviewer_data.get('talking_points', [])
        if talking_points:
            st.markdown("## 💬 Marketing Talking Points")
            st.markdown("*Ready-to-use messaging for marketing campaigns and communications*")
            
            for i, point in enumerate(talking_points, 1):
                with st.container():
                    st.markdown(f"### Talking Point {i}")
                    # Use a quote-style formatting for talking points
                    st.markdown(f"> {point}")
                    
                    # Copy button for individual talking point
                    st_copy_to_clipboard(point, key=f"talking_point_copy_{i}")
                    st.markdown("---")
            
            # Copy all talking points button
            all_talking_points = "\n\n".join([f"Talking Point {i}: {point}" for i, point in enumerate(talking_points, 1)])
            st.markdown("### Copy All Talking Points")
            st_copy_to_clipboard(all_talking_points, key="all_talking_points_copy")
        
        # Summary metrics
        if distilled_topics or talking_points:
            st.markdown("---")
            st.markdown("## 📊 Content Summary")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Distilled Topics", len(distilled_topics))
            with col2:
                st.metric("Talking Points", len(talking_points))
            with col3:
                total_words = len(" ".join(distilled_topics + talking_points).split())
                st.metric("Total Words", total_words)

elif page == "Typefully Publishing":
    # Import Typefully components at the top of the page
    import os
    from datetime import datetime, timedelta
    from agents.typefully_auth import TypefullyAuth, TypefullyAuthError
    from agents.typefully_client import TypefullyClient, TypefullyAPIError, ValidationError
    from config import TypefullyConfig
    
    st.title("🐦 Typefully Publishing Dashboard")
    st.markdown("Schedule and publish content to Twitter/X using Typefully")
    
    # API Key Configuration Section
    st.markdown("## 🔑 API Configuration")
    
    with st.expander("Configure Typefully API", expanded=not os.getenv("TYPEFULLY_API_KEY_TUON")):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            api_key_input = st.text_input(
                "Typefully API Key (TUON Account)", 
                value=os.getenv("TYPEFULLY_API_KEY_TUON", ""),
                type="password",
                help="Get your API key from https://typefully.com/settings/integrations"
            )
            
            if st.button("💾 Save API Key"):
                if api_key_input:
                    # Create/update .env file
                    env_path = ".env"
                    env_lines = []
                    key_exists = False
                    
                    # Read existing .env if it exists
                    if os.path.exists(env_path):
                        with open(env_path, 'r') as f:
                            env_lines = f.readlines()
                    
                    # Update or add the API key
                    for i, line in enumerate(env_lines):
                        if line.startswith("TYPEFULLY_API_KEY_TUON="):
                            env_lines[i] = f"TYPEFULLY_API_KEY_TUON={api_key_input}\n"
                            key_exists = True
                            break
                    
                    if not key_exists:
                        env_lines.append(f"TYPEFULLY_API_KEY_TUON={api_key_input}\n")
                    
                    # Write back to .env
                    with open(env_path, 'w') as f:
                        f.writelines(env_lines)
                    
                    st.success("✅ API key saved! Please restart the app to apply changes.")
                    os.environ["TYPEFULLY_API_KEY_TUON"] = api_key_input
                else:
                    st.error("Please enter a valid API key")
        
        with col2:
            st.markdown("### Quick Setup")
            st.markdown("1. Go to [Typefully Settings](https://typefully.com/settings/integrations)")
            st.markdown("2. Create new API key")
            st.markdown("3. Copy and paste here")
            st.markdown("4. Save and restart app")
    
    # Check if API key is configured
    api_key = os.getenv("TYPEFULLY_API_KEY_TUON")
    
    if not api_key:
        st.warning("⚠️ Please configure your Typefully API key above to continue.")
        st.stop()
    
                # Initialize Typefully components
    try:
        auth = TypefullyAuth()
        client = TypefullyClient(auth)
        typefully_config = TypefullyConfig()
        
        # Test connection
        health_status = client.health_check()
        
        if health_status["api_connectivity"]:
            st.success("✅ Connected to Typefully API successfully!")
        else:
            st.error("❌ Unable to connect to Typefully API. Please check your API key.")
            st.stop()
            
    except Exception as e:
        st.error(f"❌ Error initializing Typefully: {str(e)}")
        st.stop()
    
    st.markdown("---")
    
    # Main Publishing Interface
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Create Content", "📅 Scheduled Posts", "📊 Analytics", "⚙️ Settings"])
    
    with tab1:
        st.markdown("### Create and Schedule Content")
        
        # Content input section
        col1, col2 = st.columns([2, 1])
        
        with col1:
            content_source = st.radio(
                "Content Source:",
                ["Manual Input", "From LinkedIn Posts", "From Talking Points", "From Search Research"],
                horizontal=True
            )
            
            content_input = ""
            
            if content_source == "Manual Input":
                content_input = st.text_area(
                    "Content to publish:",
                    height=200,
                    placeholder="Enter your tweet content here...\n\nFor threads, separate tweets with double line breaks."
                )
            
            elif content_source == "From LinkedIn Posts":
                try:
                    with open('_cache_editor_linkedin_output.json', 'r') as f:
                        linkedin_data = json.load(f)
                    
                    if linkedin_data:
                        selected_post = st.selectbox(
                            "Select LinkedIn post to convert:",
                            range(len(linkedin_data)),
                            format_func=lambda x: f"Topic {x+1}: {linkedin_data[x].get('topic', 'No Topic')[:50]}..."
                        )
                        
                        if selected_post is not None:
                            content_input = linkedin_data[selected_post].get('linkedin_post', '')
                            st.text_area("Selected content (you can edit):", value=content_input, height=150, key="linkedin_content")
                    else:
                        st.warning("No LinkedIn posts found. Generate some content first!")
                        
                except FileNotFoundError:
                    st.warning("No LinkedIn posts found. Generate some content first!")
            
            elif content_source == "From Talking Points":
                try:
                    with open('_cache_reviewer_output.json', 'r') as f:
                        reviewer_data = json.load(f)
                    
                    talking_points = reviewer_data.get('talking_points', [])
                    if talking_points:
                        selected_point = st.selectbox(
                            "Select talking point to convert:",
                            range(len(talking_points)),
                            format_func=lambda x: f"Point {x+1}: {talking_points[x][:50]}..."
                        )
                        
                        if selected_point is not None:
                            content_input = talking_points[selected_point]
                            st.text_area("Selected content (you can edit):", value=content_input, height=150, key="talking_point_content")
                    else:
                        st.warning("No talking points found. Generate some content first!")
                        
                except FileNotFoundError:
                    st.warning("No talking points found. Generate some content first!")
            
            elif content_source == "From Search Research":
                try:
                    with open('_cache_search_agent_raw_api_response.json', 'r') as f:
                        search_data = json.load(f)
                    
                    choices = search_data.get('choices', [])
                    if choices:
                        content = choices[0].get('message', {}).get('content', '')
                        if content:
                            content_input = content[:2000]  # Limit length for Twitter
                            st.text_area("Selected content (you can edit):", value=content_input, height=150, key="search_content")
                        else:
                            st.warning("No research content found.")
                    else:
                        st.warning("No research content found.")
                        
                except FileNotFoundError:
                    st.warning("No research content found. Generate some content first!")
        
        with col2:
            st.markdown("### Content Analysis")
            
            if content_input:
                # Basic content analysis
                char_count = len(content_input)
                word_count = len(content_input.split())
                hashtag_count = content_input.count('#')
                mention_count = content_input.count('@')
                
                # Display metrics
                st.metric("Characters", char_count)
                st.metric("Words", word_count)
                st.metric("Hashtags", hashtag_count)
                st.metric("Mentions", mention_count)
                
                # Content type recommendation
                if char_count <= 280:
                    st.info("**Recommended:** Single Tweet")
                else:
                    st.info("**Recommended:** Thread")
                    estimated_tweets = (char_count // 280) + 1
                    st.write(f"Estimated tweets: {estimated_tweets}")
        
        # Publishing options
        st.markdown("### Publishing Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            content_type = st.selectbox(
                "Content Type:",
                ["Auto-detect", "Single Tweet", "Thread"],
                help="Auto-detect will analyze content and choose the best format"
            )
        
        with col2:
            schedule_option = st.selectbox(
                "Scheduling:",
                ["Publish Now", "Schedule for Later", "Next Free Slot"],
                help="Choose when to publish your content"
            )
        
        with col3:
            auto_features = st.multiselect(
                "Auto Features:",
                ["Auto-retweet", "Auto-plug"],
                help="Enable automatic features for content amplification"
            )
        
        # Scheduling details
        if schedule_option == "Schedule for Later":
            col1, col2 = st.columns(2)
            with col1:
                schedule_date = st.date_input("Date:", min_value=datetime.now().date())
            with col2:
                schedule_time = st.time_input("Time:", value=datetime.now().time())
            
            schedule_datetime = datetime.combine(schedule_date, schedule_time)
        else:
            schedule_datetime = None
        
        # Publish button
        if st.button("🚀 Publish Content", type="primary", use_container_width=True):
            if content_input:
                try:
                    with st.spinner("Publishing content..."):
                        # Prepare options
                        options = {
                            "auto_retweet": "Auto-retweet" in auto_features,
                            "auto_plug": "Auto-plug" in auto_features,
                            "share": True
                        }
                        
                        if schedule_option == "Schedule for Later":
                            options["schedule_date"] = schedule_datetime.isoformat()
                        elif schedule_option == "Next Free Slot":
                            options["schedule_date"] = "next-free-slot"
                        
                        # Create draft based on content type
                        if content_type == "Single Tweet" or (content_type == "Auto-detect" and len(content_input) <= 280):
                            result = client.create_draft(
                                content=content_input,
                                share=options.get("share", True),
                                auto_retweet_enabled=options.get("auto_retweet", False),
                                auto_plug_enabled=options.get("auto_plug", False),
                                schedule_date=options.get("schedule_date")
                            )
                        else:
                            # For threads, use threadify=True in create_draft
                            result = client.create_draft(
                                content=content_input,
                                threadify=True,
                                share=options.get("share", True),
                                auto_retweet_enabled=options.get("auto_retweet", False),
                                auto_plug_enabled=options.get("auto_plug", False),
                                schedule_date=options.get("schedule_date")
                            )
                        
                        st.success("✅ Content published successfully!")
                        
                        # Display result
                        if "share_url" in result:
                            st.markdown(f"📋 **Share URL:** {result['share_url']}")
                            st_copy_to_clipboard(result['share_url'], key="share_url_copy")
                        
                        st.json(result)
                        
                except TypefullyAPIError as e:
                    st.error(f"❌ API Error: {e}")
                except Exception as e:
                    st.error(f"❌ Unexpected Error: {e}")
            else:
                st.error("Please enter content to publish!")
    
    with tab2:
        st.markdown("### Scheduled Posts")
        
        try:
            # Get recent drafts
            with st.spinner("Loading scheduled posts..."):
                scheduled_drafts = client.get_recently_scheduled_drafts()
                published_drafts = client.get_recently_published_drafts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📅 Scheduled Drafts")
                if scheduled_drafts:
                    for i, draft in enumerate(scheduled_drafts):
                        with st.container():
                            st.markdown(f"**Draft {i+1}**")
                            st.write(f"Content: {draft.get('content', 'No content')[:100]}...")
                            st.write(f"Scheduled: {draft.get('schedule_date', 'No date')}")
                            st.markdown("---")
                else:
                    st.info("No scheduled drafts found")
            
            with col2:
                st.markdown("#### ✅ Published Drafts")
                if published_drafts:
                    for i, draft in enumerate(published_drafts):
                        with st.container():
                            st.markdown(f"**Published {i+1}**")
                            st.write(f"Content: {draft.get('content', 'No content')[:100]}...")
                            if 'url' in draft:
                                st.markdown(f"[View Tweet]({draft['url']})")
                            st.markdown("---")
                else:
                    st.info("No published drafts found")
                    
        except Exception as e:
            st.error(f"Error loading drafts: {e}")
    
    with tab3:
        st.markdown("### Analytics & Performance")
        
        try:
            # Get basic client information
            client_info = client.get_client_info()
            
            st.markdown("#### Client Information")
            st.json(client_info)
                
        except Exception as e:
            st.error(f"Error loading analytics: {e}")
    
    with tab4:
        st.markdown("### Settings & Configuration")
        
        # Display current configuration
        st.markdown("#### Current Configuration")
        config_status = typefully_config.validate_config()
        
        if config_status["valid"]:
            st.success("✅ Configuration is valid")
        else:
            st.error("❌ Configuration issues found")
            for error in config_status["errors"]:
                st.error(error)
        
        for warning in config_status["warnings"]:
            st.warning(warning)
        
        # Configuration details
        st.markdown("#### Configuration Details")
        st.json(config_status["config_summary"])
        
        # Health check
        st.markdown("#### Health Check")
        if st.button("🏥 Run Health Check"):
            try:
                health = client.health_check()
                
                if health.get("client_status") == "healthy":
                    st.success("✅ All systems healthy")
                else:
                    st.warning("⚠️ Some issues detected")
                
                st.json(health)
                
            except Exception as e:
                st.error(f"Health check failed: {e}")
        
        # Clear cache
        st.markdown("#### Maintenance")
        if st.button("🗑️ Clear Session Cache"):
            # Clear any cached data
            for key in list(st.session_state.keys()):
                if key.startswith("typefully_"):
                    del st.session_state[key]
            st.success("Cache cleared!") 