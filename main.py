from agents.search_agent import SearchAgent
from agents.reviewer_agent import ReviewerAgent
from agents.editor_agent import EditorAgent
import json
import os # Added for reading features file

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

    # Read Tuon.io features
    tuon_features_content = ""
    try:
        with open("tuon_features.md", "r") as f:
            tuon_features_content = f.read()
        print("Successfully loaded Tuon.io features.")
    except FileNotFoundError:
        print("Warning: tuon_features.md not found. EditorAgent may not include specific features.")
    except Exception as e:
        print(f"Error reading tuon_features.md: {e}")

    try:
        # --- 2. Initialize Agents --- 
        print("\n--- Initializing Agents ---")
        search_agent = SearchAgent()
        reviewer_agent = ReviewerAgent()
        editor_agent = EditorAgent()
        print("All agents initialized successfully.")

        # --- 3. Search Agent Workflow --- 
        print("\n--- Stage 1: Search Agent --- ")
        # As per PRD 5.2. Search Agent queries Perplexity.
        search_results = search_agent.search(initial_topic)
        if not search_results:
            print("Search Agent did not return any results. Exiting.")
            return
        print(f"Search Agent found {len(search_results)} results (mocked):")
        for i, res in enumerate(search_results):
            print(f"  {i+1}. URL: {res['url']}, Snippet: {res['snippet'][:60]}...")

        # --- 4. Reviewer Agent Workflow --- 
        print("\n--- Stage 2: Reviewer Agent --- ")
        # As per PRD 5.3. Reviewer Agent processes search results.
        distilled_content = reviewer_agent.review_and_distill(search_results, app_name, app_description, tuon_features_content)
        if not distilled_content or not distilled_content.get("distilled_topics"):
            print("Reviewer Agent did not produce distilled content. Exiting.")
            return
        print(f"Reviewer Agent distilled content (mocked):")
        print(json.dumps(distilled_content, indent=2))

        # --- 5. Editor Agent Workflow --- 
        print("\n--- Stage 3: Editor Agent (LinkedIn Posts) --- ")
        # As per PRD 5.4. Editor Agent crafts posts.
        social_media_posts = editor_agent.craft_posts(distilled_content, app_name, app_description, tuon_features_content)
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