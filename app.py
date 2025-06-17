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