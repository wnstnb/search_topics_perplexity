import google.generativeai as genai
from config import GOOGLE_API_KEY

class ReviewerAgent:
    def __init__(self):
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not configured.")
        genai.configure(api_key=GOOGLE_API_KEY)
        # Initialize Gemini 2.5 Flash model
        # For now, we'll just print, model initialization will be more specific
        print("ReviewerAgent initialized with Gemini 2.5 Flash (placeholder)")
        self.model = genai.GenerativeModel('gemini-1.5-flash-latest') # Using 1.5 flash as per PRD

    def review_and_distill(self, search_results: list, app_name: str, app_description: str) -> dict:
        """
        Processes search results, identifies key pain points, and extracts topics
        relevant to the application being marketed.
        """
        print(f"Reviewing search results for {app_name}: {app_description}")
        
        # Constructing a prompt for Gemini
        prompt_parts = [
            "You are an expert content reviewer. Your task is to analyze the following search results:"
        ]
        for i, result in enumerate(search_results):
            prompt_parts.append(f"Result {i+1}: URL: {result['url']}, Snippet: {result['snippet']}")
        
        prompt_parts.extend([
            f"Based on these results, identify key themes, pain points, and interesting angles relevant to an application called '{app_name}'.",
            f"'{app_name}' is described as: '{app_description}'.",
            "Focus on extracting information that can be framed to highlight the benefits of this application.",
            "Output a structured list of distilled topics and talking points. For example:",
            "{\"distilled_topics\": [\"Topic 1: Pain point X and how app_name solves it...\", \"Topic 2: Interesting angle Y related to app_name...\"], \"talking_points\": [\"Point A about app_name...\", \"Point B about app_name...\"]}"
        ])
        
        prompt = "\n".join(prompt_parts)
        print(f"-- Reviewer Agent Prompt to Gemini --\n{prompt[:500]}...\n-- End of Prompt Snippet --")

        # Actual call to Gemini API will go here
        # response = self.model.generate_content(prompt)
        # mock_response_text = response.text

        # Mock response for now
        mock_response_text = '''
        {
            "distilled_topics": [
                "Topic 1: Users struggle with organizing notes effectively. Tuon.io's AI features help categorize and find notes effortlessly.",
                "Topic 2: Information overload is a common pain point. Tuon.io can summarize long texts, making information digestible."
            ],
            "talking_points": [
                "Highlight Tuon.io's intelligent search.",
                "Showcase automated summarization for productivity."
            ]
        }
        '''
        print(f"-- Reviewer Agent Mock Response --\n{mock_response_text}\n-- End of Mock Response --")
        
        try:
            # A more robust parsing and validation should be here
            import json
            return json.loads(mock_response_text)
        except json.JSONDecodeError:
            print("Error: Failed to parse mock response from Reviewer Agent.")
            return {"distilled_topics": [], "talking_points": []} 