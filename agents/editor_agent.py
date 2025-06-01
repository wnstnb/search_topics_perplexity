import google.generativeai as genai
from config import GOOGLE_API_KEY
import re # Import re module

class EditorAgent:
    def __init__(self):
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not configured.")
        genai.configure(api_key=GOOGLE_API_KEY)
        # Initialize Gemini 2.5 Pro model
        print("EditorAgent initialized with Gemini 2.5 Pro")
        self.model = genai.GenerativeModel('gemini-2.5-pro-preview-05-06') # Using 1.5 pro as per PRD

    def craft_posts(self, distilled_content: dict, app_name: str, app_description: str) -> list:
        """
        Takes curated topics and pain points and crafts engaging social media posts.
        """
        print(f"Crafting posts for {app_name} based on distilled content.")
        social_media_posts = []

        topics = distilled_content.get("distilled_topics", [])
        # talking_points = distilled_content.get("talking_points", []) # Not directly used in this mock, but available

        if not topics:
            print("Warning: No distilled topics provided to Editor Agent.")
            return []

        for i, topic_text in enumerate(topics):
            # Constructing a prompt for Gemini Pro
            prompt_parts = [
                f"You are an expert social media copywriter for {app_name}, which is '{app_description}'.",
                f"Your task is to create engaging social media posts based on the following topic: '{topic_text}'.",
                "Generate three variations of a social media post for this topic: one for Twitter (max 280 chars), one for LinkedIn (more professional), and one for Facebook (more conversational).",
                "Ensure posts are engaging, concise, and include 2-3 relevant hashtags.",
                "Maintain a consistent tone of voice that is knowledgeable, helpful, and slightly enthusiastic about how the app solves user problems.",
                "Output the posts in a clear, structured format. For example:",
                "**Twitter Post:**\\n[Your Twitter post text here including #hashtags]\\n\\n**LinkedIn Post:**\\n[Your LinkedIn post text here including #hashtags]\\n\\n**Facebook Post:**\\n[Your Facebook post text here including #hashtags]"
            ]
            prompt = "\\n".join(prompt_parts)
            print(f"-- Editor Agent Prompt to Gemini (Topic {i+1}) --\\n{prompt[:500]}...\\n-- End of Prompt Snippet --")

            # Mock response - made slightly different for the second topic
            if i == 0:
                generated_post_text = f"""
                **Twitter Post:**
                Topic 1: Struggling with note chaos? {app_name} uses AI to auto-organize & find notes instantly! ✨ #NoteTaking #AI #Productivity

                **LinkedIn Post:**
                Topic 1: In today's fast-paced environment, effective note management is key. {app_name} leverages artificial intelligence to streamline your workflow. #DigitalTransformation #AIinBusiness

                **Facebook Post:**
                Topic 1: Tired of searching endlessly? 😫 {app_name}'s smart AI organizes your thoughts! #SmartNotes #GetOrganized
                """
            else:
                generated_post_text = f"""
                **Twitter Post:**
                Topic 2: Overwhelmed by info? {app_name} summarizes long texts with AI! 🤯 #ProductivityBoost #AI #Summary

                **LinkedIn Post:**
                Topic 2: Combat information overload with {app_name}. Our AI-powered summarization helps you grasp key insights faster. #FutureOfWork #AISolutions

                **Facebook Post:**
                Topic 2: Drowning in information? 🌊 Let {app_name} AI give you the highlights! #AISummarizer #TechForGood
                """
            print(f"-- Editor Agent Mock Response (Topic {i+1}) --\\n{generated_post_text}\\n-- End of Mock Response --")
            
            current_posts = {
                "topic": topic_text,
                "twitter": "",
                "linkedin": "",
                "facebook": ""
            }

            # More robust regex to capture content for each platform
            # Looks for a platform title and captures text until the *next* platform title or end of string
            # (?s) or re.DOTALL makes . match newlines.
            # The lookahead (?!\*\*\w+ Post:\*\*) ensures it stops before any other platform marker.
            
            twitter_match = re.search(r"\*\*Twitter Post:\*\*\s*(.*?)(?=\s*\*\*(?:LinkedIn|Facebook) Post:\*\*|$)", generated_post_text, re.DOTALL)
            linkedin_match = re.search(r"\*\*LinkedIn Post:\*\*\s*(.*?)(?=\s*\*\*(?:Twitter|Facebook) Post:\*\*|$)", generated_post_text, re.DOTALL)
            facebook_match = re.search(r"\*\*Facebook Post:\*\*\s*(.*?)(?=\s*\*\*(?:Twitter|LinkedIn) Post:\*\*|$)", generated_post_text, re.DOTALL)

            if twitter_match:
                current_posts["twitter"] = twitter_match.group(1).strip()
            if linkedin_match:
                current_posts["linkedin"] = linkedin_match.group(1).strip()
            if facebook_match:
                current_posts["facebook"] = facebook_match.group(1).strip()

            social_media_posts.append(current_posts)

        return social_media_posts 