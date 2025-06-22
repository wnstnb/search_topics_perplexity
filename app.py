import streamlit as st
import json
from datetime import datetime
from database import DatabaseHandler
# import streamlit.components.v1 as components # No longer needed
from st_copy_to_clipboard import st_copy_to_clipboard # Import the component

# Page config MUST be the first Streamlit command
st.set_page_config(layout="wide", page_title="Social Media Dashboard")

# Initialize database
db = DatabaseHandler()

# Initialize session state for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = "LinkedIn Posts"
if 'selected_session_id' not in st.session_state:
    st.session_state.selected_session_id = None

# Sidebar for navigation with buttons
st.sidebar.title("Navigation")

# Session selection
sessions = db.get_sessions()
if sessions:
    session_options = {f"{session['session_name']} ({session['created_at']})": session['id'] 
                      for session in sessions}
    selected_session_name = st.sidebar.selectbox(
        "Select Session:", 
        options=list(session_options.keys()),
        index=0
    )
    st.session_state.selected_session_id = session_options[selected_session_name]
    
    # Display session info
    selected_session = next((s for s in sessions if s['id'] == st.session_state.selected_session_id), None)
    if selected_session:
        st.sidebar.markdown(f"**Topic:** {selected_session.get('topic', 'N/A')}")
        st.sidebar.markdown(f"**App:** {selected_session.get('app_name', 'N/A')}")
else:
    st.sidebar.warning("No sessions found. Run main.py to generate content first.")
    st.session_state.selected_session_id = None

st.sidebar.markdown("---")

# Navigation buttons
if st.sidebar.button("LinkedIn Posts", use_container_width=True):
    st.session_state.current_page = "LinkedIn Posts"
if st.sidebar.button("Twitter Results", use_container_width=True):
    st.session_state.current_page = "Twitter Results"
if st.sidebar.button("Search Research", use_container_width=True):
    st.session_state.current_page = "Search Research"
if st.sidebar.button("Talking Points", use_container_width=True):
    st.session_state.current_page = "Talking Points"

page = st.session_state.current_page
selected_session_id = st.session_state.selected_session_id

if page == "LinkedIn Posts":
    st.title("LinkedIn Post Suggestions Dashboard")
    st.markdown("Displaying topics and generated LinkedIn posts from database")

    if not selected_session_id:
        st.warning("Please select a session from the sidebar.")
        st.stop()

    # Load the LinkedIn data from database
    data = db.get_editor_outputs(selected_session_id) if selected_session_id else []
    
    if not data:
        st.warning("No LinkedIn posts found for this session.")
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
    st.title("Twitter Search Results")
    st.markdown("Browse through Twitter posts related to your search queries")
    
    if not selected_session_id:
        st.warning("Please select a session from the sidebar.")
        st.stop()

    # Load the Twitter data from database
    twitter_data = db.get_twitter_results(selected_session_id) if selected_session_id else []
    
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
    st.title("Search Research Results")
    st.markdown("AI-generated research content with citations and sources")
    
    if not selected_session_id:
        st.warning("Please select a session from the sidebar.")
        st.stop()

    # Load the Search Agent data from database
    search_results = db.get_search_results(selected_session_id) if selected_session_id else []
    
    if not search_results:
        st.warning("No search results found for this session.")
    else:
        st.markdown("## Search Results")
        st.write(f"Found {len(search_results)} search results")
        
        for i, result in enumerate(search_results):
            with st.container():
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    url = result.get('url', '')
                    snippet = result.get('snippet', 'No content available')
                    if url:
                        st.markdown(f"**[{url}]({url})**")
                    else:
                        st.markdown("**No URL**")
                    
                    st.markdown(f"*{snippet}*")
                
                with col2:
                    created_at = result.get('created_at', '')
                    if created_at:
                        st.write(f"📅 {created_at}")
                    else:
                        st.write("📅 No date")
                
                # Copy button for the snippet
                if snippet:
                    st_copy_to_clipboard(snippet, key=f"search_snippet_copy_{i}")
                
                # Copy button for the URL
                if url:
                    st_copy_to_clipboard(url, key=f"search_url_copy_{i}")
                
                st.markdown("---")

elif page == "Talking Points":
    st.title("Marketing Talking Points")
    st.markdown("Distilled topics and key talking points for Tuon.io based on market research")
    
    if not selected_session_id:
        st.warning("Please select a session from the sidebar.")
        st.stop()

    # Load the Reviewer Output data from database
    reviewer_data = db.get_reviewer_output(selected_session_id) if selected_session_id else {"distilled_topics": [], "talking_points": []}
    
    if not reviewer_data or (not reviewer_data.get("distilled_topics") and not reviewer_data.get("talking_points")):
        st.warning("No reviewer data found for this session.")
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