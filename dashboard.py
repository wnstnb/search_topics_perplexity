import streamlit as st
import pandas as pd
import json
import sqlite3
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from database import DatabaseHandler
import io
import base64
import os

# Page configuration
st.set_page_config(
    page_title="Content Generation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database handler
@st.cache_resource
def get_database_handler():
    return DatabaseHandler()

db = get_database_handler()

# Helper functions
def get_session_summary(session_id):
    """Get summary statistics for a session."""
    search_count = len(db.get_search_results(session_id))
    twitter_count = len(db.get_twitter_results(session_id))
    editor_count = len(db.get_editor_outputs(session_id))
    reviewer_exists = db.has_reviewer_output(session_id)
    
    return {
        'search_results': search_count,
        'twitter_results': twitter_count,
        'editor_outputs': editor_count,
        'reviewer_output': 1 if reviewer_exists else 0
    }

def export_session_data(session_id, format='json'):
    """Export session data in specified format."""
    session_data = {
        'session_info': next((s for s in db.get_sessions() if s['id'] == session_id), None),
        'search_results': db.get_search_results(session_id),
        'twitter_results': db.get_twitter_results(session_id),
        'reviewer_output': db.get_reviewer_output(session_id),
        'editor_outputs': db.get_editor_outputs(session_id)
    }
    
    if format == 'json':
        return json.dumps(session_data, indent=2, default=str)
    elif format == 'csv':
        # For CSV, we'll create separate dataframes for each data type
        dfs = {}
        for key, data in session_data.items():
            if key != 'session_info' and data:
                if isinstance(data, list):
                    dfs[key] = pd.DataFrame(data)
                else:
                    dfs[key] = pd.DataFrame([data])
        return dfs
    
    return session_data

def create_download_link(data, filename, format='json'):
    """Create a download link for data."""
    if format == 'json':
        b64 = base64.b64encode(data.encode()).decode()
        href = f'<a href="data:application/json;base64,{b64}" download="{filename}.json">Download JSON</a>'
    elif format == 'csv':
        # For CSV, create a zip file with multiple CSV files
        pass  # Implement if needed
    
    return href

# Sidebar navigation
st.sidebar.title("📊 Dashboard Navigation")

# Check if page is set in session state from button navigation
if 'page' in st.session_state:
    default_page = st.session_state['page']
    # Clear the page from session state after using it
    del st.session_state['page']
else:
    default_page = "🏠 Overview"

page_options = ["🏠 Overview", "📊 Sessions", "🔍 Data Explorer", "📈 Analytics", "🛠️ Database Tools", "📤 Export"]
default_index = page_options.index(default_page) if default_page in page_options else 0

page = st.sidebar.selectbox(
    "Select Page",
    page_options,
    index=default_index
)

# Main dashboard content
if page == "🏠 Overview":
    st.title("🏠 Content Generation Dashboard")
    st.markdown("Welcome to your content generation dashboard. Here you can manage sessions, explore data, and analyze your content generation pipeline.")
    
    # Quick stats
    sessions = db.get_sessions()
    total_sessions = len(sessions)
    
    if total_sessions > 0:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Sessions", total_sessions)
        
        with col2:
            total_search = sum(len(db.get_search_results(s['id'])) for s in sessions)
            st.metric("Search Results", total_search)
        
        with col3:
            total_twitter = sum(len(db.get_twitter_results(s['id'])) for s in sessions)
            st.metric("Twitter Results", total_twitter)
        
        with col4:
            total_posts = sum(len(db.get_editor_outputs(s['id'])) for s in sessions)
            st.metric("Generated Posts", total_posts)
        
        # Recent sessions
        st.subheader("📅 Recent Sessions")
        recent_sessions = sessions[:5]  # Already sorted by created_at DESC
        
        for session in recent_sessions:
            with st.expander(f"📝 {session['session_name']} - {session['created_at']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Topic:** {session['topic'] or 'N/A'}")
                    st.write(f"**App:** {session['app_name'] or 'N/A'}")
                with col2:
                    summary = get_session_summary(session['id'])
                    st.write(f"**Data Points:** {sum(summary.values())}")
                    st.write(f"**Created:** {session['created_at']}")
    else:
        st.info("No sessions found. Create your first session by running the main content generation script.")

elif page == "📊 Sessions":
    st.title("📊 Session Management")
    
    sessions = db.get_sessions()
    
    if not sessions:
        st.warning("No sessions found.")
        st.stop()
    
    # Session selector
    session_options = {f"{s['session_name']} ({s['created_at']})": s['id'] for s in sessions}
    selected_session_name = st.selectbox("Select Session", list(session_options.keys()))
    selected_session_id = session_options[selected_session_name]
    
    # Session details
    session_info = next(s for s in sessions if s['id'] == selected_session_id)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Session Information")
        st.write(f"**Name:** {session_info['session_name']}")
        st.write(f"**Topic:** {session_info['topic'] or 'N/A'}")
        st.write(f"**App Name:** {session_info['app_name'] or 'N/A'}")
        st.write(f"**Created:** {session_info['created_at']}")
    
    with col2:
        st.subheader("Data Summary")
        summary = get_session_summary(selected_session_id)
        for key, value in summary.items():
            st.write(f"**{key.replace('_', ' ').title()}:** {value}")
    
    # Session actions
    st.subheader("Session Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Explore Data"):
            st.session_state['explorer_session_id'] = selected_session_id
            st.session_state['page'] = "🔍 Data Explorer"
            st.rerun()
    
    with col2:
        if st.button("📊 View Analytics"):
            st.session_state['analytics_session_id'] = selected_session_id
            st.session_state['page'] = "📈 Analytics"
            st.rerun()
    
    with col3:
        if st.button("📤 Export Session"):
            st.session_state['export_session_id'] = selected_session_id
            st.session_state['page'] = "📤 Export"
            st.rerun()

elif page == "🔍 Data Explorer":
    st.title("🔍 Data Explorer")
    
    sessions = db.get_sessions()
    if not sessions:
        st.warning("No sessions found.")
        st.stop()
    
    # Session selector
    session_options = {f"{s['session_name']} ({s['created_at']})": s['id'] for s in sessions}
    
    # Use session from state if available
    default_session = None
    if 'explorer_session_id' in st.session_state:
        for name, id in session_options.items():
            if id == st.session_state['explorer_session_id']:
                default_session = name
                break
    
    selected_session_name = st.selectbox("Select Session", list(session_options.keys()), 
                                        index=list(session_options.keys()).index(default_session) if default_session else 0)
    selected_session_id = session_options[selected_session_name]
    
    # Data type selector
    data_type = st.selectbox("Select Data Type", 
                           ["🔍 Search Results", "🐦 Twitter Results", "📝 Reviewer Output", "📄 Editor Outputs"])
    
    if data_type == "🔍 Search Results":
        st.subheader("🔍 Search Results")
        search_results = db.get_search_results(selected_session_id)
        
        if search_results:
            for i, result in enumerate(search_results):
                with st.expander(f"Result {i+1}: {result['url'][:50]}..."):
                    st.write(f"**URL:** {result['url']}")
                    st.write(f"**Snippet:** {result['snippet']}")
                    st.write(f"**Created:** {result['created_at']}")
                    
                    if result['raw_response']:
                        if st.button(f"Show Raw API Response", key=f"raw_search_{i}"):
                            st.code(result['raw_response'])
        else:
            st.info("No search results found for this session.")
    
    elif data_type == "🐦 Twitter Results":
        st.subheader("🐦 Twitter Results")
        twitter_results = db.get_twitter_results(selected_session_id)
        
        if twitter_results:
            for i, result in enumerate(twitter_results):
                with st.expander(f"Tweet {i+1}: @{result['screen_name']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**URL:** {result['url']}")
                        st.write(f"**User:** @{result['screen_name']}")
                        st.write(f"**Followers:** {result['followers_count']:,}")
                        st.write(f"**Created:** {result['created_at']}")
                    
                    with col2:
                        st.write(f"**❤️ Likes:** {result['favorite_count']:,}")
                        st.write(f"**🔄 Retweets:** {result['retweet_count']:,}")
                        st.write(f"**💬 Replies:** {result['reply_count']:,}")
                        st.write(f"**💭 Quotes:** {result['quote_count']:,}")
                    
                    st.write(f"**Content:** {result['snippet']}")
                    
                    if result['raw_response']:
                        if st.button(f"Show Raw API Response", key=f"raw_twitter_{i}"):
                            st.code(result['raw_response'])
        else:
            st.info("No Twitter results found for this session.")
    
    elif data_type == "📝 Reviewer Output":
        st.subheader("📝 Reviewer Output")
        reviewer_output = db.get_reviewer_output(selected_session_id)
        
        if reviewer_output['distilled_topics'] or reviewer_output['talking_points']:
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Distilled Topics:**")
                for topic in reviewer_output['distilled_topics']:
                    st.write(f"• {topic}")
            
            with col2:
                st.write("**Talking Points:**")
                for point in reviewer_output['talking_points']:
                    st.write(f"• {point}")
            
            if reviewer_output.get('raw_response'):
                if st.button("Show Raw API Response", key="raw_reviewer"):
                    st.code(reviewer_output['raw_response'])
        else:
            st.info("No reviewer output found for this session.")
    
    elif data_type == "📄 Editor Outputs":
        st.subheader("📄 Editor Outputs")
        editor_outputs = db.get_editor_outputs(selected_session_id)
        
        if editor_outputs:
            for i, output in enumerate(editor_outputs):
                with st.expander(f"Post {i+1}: {output['topic'][:50]}..."):
                    st.write(f"**Topic:** {output['topic']}")
                    st.write(f"**Created:** {output['created_at']}")
                    
                    st.write("**LinkedIn Post:**")
                    st.text_area("", output['linkedin_post'], height=200, key=f"post_{i}")
                    
                    if st.button(f"📋 Copy Post {i+1}", key=f"copy_{i}"):
                        st.success("Post copied to clipboard!")
                    
                    if output['raw_response']:
                        if st.button(f"Show Raw API Response", key=f"raw_editor_{i}"):
                            st.code(output['raw_response'])
        else:
            st.info("No editor outputs found for this session.")

elif page == "📈 Analytics":
    st.title("📈 Analytics Dashboard")
    
    sessions = db.get_sessions()
    if not sessions:
        st.warning("No sessions found.")
        st.stop()
    
    # Session selector for focused analytics
    session_options = {f"{s['session_name']} ({s['created_at']})": s['id'] for s in sessions}
    session_options["All Sessions"] = "all"
    
    selected_session_name = st.selectbox("Select Session for Analysis", list(session_options.keys()))
    selected_session_id = session_options[selected_session_name]
    
    if selected_session_id == "all":
        # Overall analytics
        st.subheader("📊 Overall Analytics")
        
        # Sessions over time
        sessions_df = pd.DataFrame(sessions)
        sessions_df['created_at'] = pd.to_datetime(sessions_df['created_at'])
        sessions_df['date'] = sessions_df['created_at'].dt.date
        
        daily_sessions = sessions_df.groupby('date').size().reset_index(name='count')
        
        fig = px.line(daily_sessions, x='date', y='count', title='Sessions Created Over Time')
        st.plotly_chart(fig, use_container_width=True)
        
        # Data distribution
        col1, col2 = st.columns(2)
        
        with col1:
            # Data points by session
            data_points = []
            for session in sessions:
                summary = get_session_summary(session['id'])
                data_points.append({
                    'session': session['session_name'][:20] + "...",
                    'search_results': summary['search_results'],
                    'twitter_results': summary['twitter_results'],
                    'editor_outputs': summary['editor_outputs'],
                    'reviewer_output': summary['reviewer_output']
                })
            
            dp_df = pd.DataFrame(data_points)
            dp_df_melted = dp_df.melt(id_vars=['session'], var_name='data_type', value_name='count')
            
            fig = px.bar(dp_df_melted, x='session', y='count', color='data_type', 
                        title='Data Points by Session')
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Total counts
            total_counts = {
                'Search Results': sum(summary['search_results'] for summary in [get_session_summary(s['id']) for s in sessions]),
                'Twitter Results': sum(summary['twitter_results'] for summary in [get_session_summary(s['id']) for s in sessions]),
                'Editor Outputs': sum(summary['editor_outputs'] for summary in [get_session_summary(s['id']) for s in sessions]),
                'Reviewer Outputs': sum(summary['reviewer_output'] for summary in [get_session_summary(s['id']) for s in sessions])
            }
            
            fig = px.pie(values=list(total_counts.values()), names=list(total_counts.keys()), 
                        title='Distribution of Data Types')
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        # Session-specific analytics
        session_info = next(s for s in sessions if s['id'] == selected_session_id)
        st.subheader(f"📊 Analytics for: {session_info['session_name'][:50]}...")
        
        # Twitter engagement analysis
        twitter_results = db.get_twitter_results(selected_session_id)
        if twitter_results:
            st.subheader("🐦 Twitter Engagement Analysis")
            
            twitter_df = pd.DataFrame(twitter_results)
            
            if len(twitter_df) > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Engagement metrics
                    total_engagement = twitter_df['favorite_count'] + twitter_df['retweet_count'] + twitter_df['reply_count']
                    
                    fig = px.scatter(twitter_df, x='followers_count', y=total_engagement,
                                   hover_data=['screen_name'], title='Engagement vs Followers')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Top engaged tweets
                    twitter_df['total_engagement'] = twitter_df['favorite_count'] + twitter_df['retweet_count'] + twitter_df['reply_count']
                    top_tweets = twitter_df.nlargest(min(5, len(twitter_df)), 'total_engagement')
                    
                    fig = px.bar(top_tweets, x='screen_name', y='total_engagement',
                               title='Top Engaged Tweets')
                    st.plotly_chart(fig, use_container_width=True)
        
        # Content analysis
        editor_outputs = db.get_editor_outputs(selected_session_id)
        if editor_outputs:
            st.subheader("📄 Content Analysis")
            
            # Post length analysis
            post_lengths = [len(output['linkedin_post']) for output in editor_outputs]
            
            fig = px.histogram(x=post_lengths, title='LinkedIn Post Length Distribution')
            fig.update_xaxes(title='Post Length (characters)')
            fig.update_yaxes(title='Count')
            st.plotly_chart(fig, use_container_width=True)

elif page == "🛠️ Database Tools":
    st.title("🛠️ Database Tools")
    
    st.warning("⚠️ Use these tools carefully. Some operations cannot be undone.")
    
    # Database info
    st.subheader("📊 Database Information")
    
    # Get database file info
    db_path = db.db_path
    if os.path.exists(db_path):
        file_size = os.path.getsize(db_path)
        file_size_mb = file_size / (1024 * 1024)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Database Size", f"{file_size_mb:.2f} MB")
        with col2:
            st.metric("Total Sessions", len(db.get_sessions()))
        with col3:
            st.metric("Database File", db_path)
    
    # Database maintenance
    st.subheader("🔧 Maintenance Operations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Vacuum Database**")
        st.write("Reclaim unused space and optimize database performance.")
        if st.button("🗜️ Vacuum Database"):
            with db.get_connection() as conn:
                conn.execute("VACUUM")
            st.success("Database vacuumed successfully!")
    
    with col2:
        st.write("**Analyze Database**")
        st.write("Update database statistics for better query performance.")
        if st.button("📊 Analyze Database"):
            with db.get_connection() as conn:
                conn.execute("ANALYZE")
            st.success("Database analyzed successfully!")
    
    # Danger zone
    st.subheader("⚠️ Danger Zone")
    
    with st.expander("🗑️ Delete Session"):
        st.warning("This will permanently delete a session and all its data!")
        
        sessions = db.get_sessions()
        if sessions:
            session_options = {f"{s['session_name']} ({s['created_at']})": s['id'] for s in sessions}
            selected_session = st.selectbox("Select Session to Delete", list(session_options.keys()))
            
            if st.button("🗑️ DELETE SESSION", type="primary"):
                session_id = session_options[selected_session]
                
                # Delete session data
                with db.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM search_results WHERE session_id = ?", (session_id,))
                    cursor.execute("DELETE FROM twitter_results WHERE session_id = ?", (session_id,))
                    cursor.execute("DELETE FROM reviewer_outputs WHERE session_id = ?", (session_id,))
                    cursor.execute("DELETE FROM editor_outputs WHERE session_id = ?", (session_id,))
                    cursor.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
                    conn.commit()
                
                st.success(f"Session '{selected_session}' deleted successfully!")
                st.rerun()

elif page == "📤 Export":
    st.title("📤 Export Data")
    
    sessions = db.get_sessions()
    if not sessions:
        st.warning("No sessions found.")
        st.stop()
    
    # Session selector
    session_options = {f"{s['session_name']} ({s['created_at']})": s['id'] for s in sessions}
    session_options["All Sessions"] = "all"
    
    selected_session_name = st.selectbox("Select Session to Export", list(session_options.keys()))
    selected_session_id = session_options[selected_session_name]
    
    # Export format
    export_format = st.selectbox("Export Format", ["JSON", "CSV"])
    
    if st.button("📤 Generate Export"):
        if selected_session_id == "all":
            # Export all sessions
            all_data = {}
            for session in sessions:
                session_data = export_session_data(session['id'], export_format.lower())
                all_data[f"session_{session['id']}"] = session_data
            
            if export_format == "JSON":
                json_str = json.dumps(all_data, indent=2, default=str)
                st.download_button(
                    label="📥 Download All Sessions (JSON)",
                    data=json_str,
                    file_name=f"all_sessions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
                with st.expander("Preview Export Data"):
                    st.code(json_str[:1000] + "..." if len(json_str) > 1000 else json_str)
        
        else:
            # Export single session
            session_data = export_session_data(selected_session_id, export_format.lower())
            session_info = next(s for s in sessions if s['id'] == selected_session_id)
            
            if export_format == "JSON":
                json_str = json.dumps(session_data, indent=2, default=str)
                st.download_button(
                    label="📥 Download Session (JSON)",
                    data=json_str,
                    file_name=f"session_{selected_session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
                with st.expander("Preview Export Data"):
                    st.code(json_str[:1000] + "..." if len(json_str) > 1000 else json_str)
            
            elif export_format == "CSV":
                # Create separate CSV files for each data type
                csv_files = export_session_data(selected_session_id, 'csv')
                
                for data_type, df in csv_files.items():
                    if not df.empty:
                        csv_data = df.to_csv(index=False)
                        st.download_button(
                            label=f"📥 Download {data_type.replace('_', ' ').title()} (CSV)",
                            data=csv_data,
                            file_name=f"{data_type}_session_{selected_session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                            mime="text/csv"
                        )

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Content Generation Dashboard**")
st.sidebar.markdown("Built with Streamlit") 