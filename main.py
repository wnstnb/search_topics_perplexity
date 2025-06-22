from agents.search_agent import SearchAgent
from agents.reviewer_agent import ReviewerAgent
from agents.editor_agent import EditorAgent
from agents.twitter_agent import TwitterAgent
from database import DatabaseHandler
import json
import os # Added for reading features file
from datetime import datetime

def main():
    print("Starting AI-Powered Social Media Content Generation...")

    # --- 1. Input ---    
    # As per PRD 5.1. User provides an initial topic or theme and app details.
    # For now, we'll use hardcoded values. In a real app, this would come from user input.
    initial_topic = "pain points in current note-taking apps in the AI era"
    app_name = "Tuon.io"
    app_description = "A note-taking app that integrates AI into the creative workflow, helping users capture, organize, and develop ideas effortlessly."
    
    print(f"\n--- Inputs --- ")
    print(f"Initial Topic: {initial_topic}")
    print(f"App Name: {app_name}")
    print(f"App Description: {app_description}")

    # --- Control Flags for Agent Execution ---
    RUN_SEARCH_AGENT = True  # Set to False to skip Perplexity search
    RUN_TWITTER_AGENT = True # Set to False to skip Twitter search
    
    # --- Debugging/Caching Control ---
    USE_EXISTING_SESSION = True  # Set to True to reuse latest session (for caching), False to create new session
    FORCE_NEW_SESSION = False    # Set to True to always create new session (overrides USE_EXISTING_SESSION)

    # Read Tuon.io features
    tuon_features_content = ""
    twitter_query = "AI in notes"
    try:
        with open("tuon_features.md", "r") as f:
            tuon_features_content = f.read()
        print("Successfully loaded Tuon.io features.")
    except FileNotFoundError:
        print("Warning: tuon_features.md not found. EditorAgent may not include specific features.")
    except Exception as e:
        print(f"Error reading tuon_features.md: {e}")

    try:
        # --- 2. Initialize Database and Session Management --- 
        print("\n--- Initializing Database and Session Management ---")
        db = DatabaseHandler()
        
        # Determine session strategy
        if FORCE_NEW_SESSION:
            # Always create new session
            session_name = f"Content Generation - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            session_id = db.create_session(
                session_name=session_name,
                topic=initial_topic,
                app_name=app_name,
                app_description=app_description
            )
            print(f"🆕 Created NEW session '{session_name}' with ID: {session_id}")
            
        elif USE_EXISTING_SESSION:
            # Try to reuse existing session, create new if none exists
            existing_session_id = db.get_latest_session_id()
            if existing_session_id:
                session_id = existing_session_id
                sessions = db.get_sessions()
                latest_session = sessions[0] if sessions else None
                if latest_session:
                    print(f"♻️  REUSING existing session '{latest_session['session_name']}' with ID: {session_id}")
                    print(f"   Original topic: {latest_session.get('topic', 'N/A')}")
                    print(f"   Created: {latest_session.get('created_at', 'N/A')}")
                    print(f"   📋 This enables CACHING - agents will use previously stored data if available")
                else:
                    session_id = existing_session_id
                    print(f"♻️  REUSING session ID: {session_id} (metadata not available)")
            else:
                # No existing sessions, create new one
                session_name = f"Content Generation - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                session_id = db.create_session(
                    session_name=session_name,
                    topic=initial_topic,
                    app_name=app_name,
                    app_description=app_description
                )
                print(f"🆕 No existing sessions found. Created NEW session '{session_name}' with ID: {session_id}")
        else:
            # Create new session (original behavior)
            session_name = f"Content Generation - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            session_id = db.create_session(
                session_name=session_name,
                topic=initial_topic,
                app_name=app_name,
                app_description=app_description
            )
            print(f"🆕 Created NEW session '{session_name}' with ID: {session_id}")
        
        # --- 3. Initialize Agents --- 
        print("\n--- Initializing Agents ---")
        search_agent = SearchAgent()
        reviewer_agent = ReviewerAgent()
        editor_agent = EditorAgent()
        twitter_agent = TwitterAgent()
        print("All agents initialized successfully.")

        # Initialize results lists to ensure they are always defined
        search_results = []
        tweet_results = []

        # --- 4. Search Agent Workflow --- 
        if RUN_SEARCH_AGENT:
            print("\n--- Stage 1a: Search Agent (Perplexity) --- ")
            _temp_search_results = search_agent.search(initial_topic, session_id)
            if _temp_search_results:
                search_results = _temp_search_results
                print(f"Search Agent found {len(search_results)} results:")
                for i, res in enumerate(search_results):
                    print(f"  {i+1}. URL: {res['url']}, Snippet: {res['snippet'][:60]}...")
            else:
                print("Search Agent (Perplexity) did not return any results.")
        else:
            print("\n--- Stage 1a: Search Agent (Perplexity) - SKIPPED ---")

        # --- 4b. Twitter Agent Workflow --- 
        if RUN_TWITTER_AGENT:
            print("\n--- Stage 1b: Twitter Agent --- ")
            _temp_tweet_results = twitter_agent.search_tweets(twitter_query, session_id=session_id)
            if _temp_tweet_results:
                tweet_results = _temp_tweet_results
                print(f"Twitter Agent found {len(tweet_results)} tweets for query '{twitter_query}':")
                for i, res in enumerate(tweet_results):
                    print(f"  {i+1}. URL: {res['url']}, Snippet: {res['snippet'][:60]}...")
            else:
                print(f"Twitter Agent did not return any results for query '{twitter_query}'.")
        else:
            print("\n--- Stage 1b: Twitter Agent - SKIPPED ---")
        
        # Combine results based on which agents were run
        if RUN_SEARCH_AGENT and RUN_TWITTER_AGENT:
            combined_search_results = search_results + tweet_results
            print(f"\nCombined {len(search_results)} Perplexity results and {len(tweet_results)} Twitter results.")
        elif RUN_SEARCH_AGENT:
            combined_search_results = search_results
            print(f"\nUsing {len(search_results)} Perplexity results only.")
        elif RUN_TWITTER_AGENT:
            combined_search_results = tweet_results
            print(f"\nUsing {len(tweet_results)} Twitter results only.")
        else:
            combined_search_results = []
            print("\nBoth Perplexity and Twitter searches were skipped.")

        if not combined_search_results:
            print("No search results gathered from any agent. Exiting.")
            return

        # --- 5. Reviewer Agent Workflow --- 
        print("\n--- Stage 2: Reviewer Agent --- ")
        # As per PRD 5.3. Reviewer Agent processes search results.
        distilled_content = reviewer_agent.review_and_distill(combined_search_results, app_name, app_description, tuon_features_content, session_id)
        if not distilled_content or not distilled_content.get("distilled_topics"):
            print("Reviewer Agent did not produce distilled content. Exiting.")
            return
        print(f"Reviewer Agent distilled content:")
        print(json.dumps(distilled_content, indent=2))

        # --- 6. Editor Agent Workflow --- 
        print("\n--- Stage 3: Editor Agent (LinkedIn Posts) --- ")
        # As per PRD 5.4. Editor Agent crafts posts.
        social_media_posts = editor_agent.craft_posts(distilled_content, app_name, app_description, tuon_features_content, session_id)
        if not social_media_posts:
            print("Editor Agent did not generate any LinkedIn posts. Exiting.")
            return
        
        # --- 6. Output --- 
        # As per PRD 5.5. Output a set of social media posts.
        print("\n--- Generated LinkedIn Posts --- ")
        for i, topic_post_data in enumerate(social_media_posts):
            print(f"\n--- LinkedIn Post for Topic {i+1}: \"{topic_post_data.get('topic', 'N/A')}\" ---")
            linkedin_post = topic_post_data.get('linkedin_post', '#Error: Post not found')
            if linkedin_post.startswith("#Error") or not linkedin_post.strip():
                print(f"    {linkedin_post}")
            else:
                print(f"    {linkedin_post.replace('\n', '\n    ')}")

        print("\nAI-Powered Social Media Content Generation complete.")

    except ValueError as e:
        print(f"Configuration Error: {e}")
        print("Please ensure PERPLEXITY_API_KEY and GOOGLE_API_KEY are set in your .env file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 