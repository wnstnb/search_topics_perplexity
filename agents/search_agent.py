from config import PERPLEXITY_API_KEY
from openai import OpenAI # Import OpenAI
import json # For parsing if sources are in a JSON string

class SearchAgent:
    def __init__(self):
        if not PERPLEXITY_API_KEY:
            raise ValueError("PERPLEXITY_API_KEY not configured.")
        self.api_key = PERPLEXITY_API_KEY
        try:
            self.client = OpenAI(api_key=self.api_key, base_url="https://api.perplexity.ai")
            print("SearchAgent initialized with Perplexity API client.")
        except Exception as e:
            print(f"Error initializing Perplexity API client: {e}")
            raise

    def search(self, topic: str) -> list:
        """Queries Perplexity API to find relevant content based on the topic."""
        print(f"Searching for topic: '{topic}' using Perplexity API (model: sonar-pro)")
        
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an AI assistant that researches topics and provides concise, factual information, including sources when available."
                    "Focus on finding recent and relevant articles, blog posts, forum discussions, and social media threads related to the user's query."
                ),
            },
            {
                "role": "user",
                "content": topic,
            },
        ]

        try:
            response = self.client.chat.completions.create(
                model="sonar-pro", # As requested by user
                messages=messages,
                # Perplexity might have specific parameters for temperature, max_tokens for online models
                # For now, using defaults. Refer to Perplexity docs for specifics.
            )
            
            print(f"-- Perplexity API Raw Response Snippet --")
            # Convert response to dict for easier inspection if it's not already one
            try:
                response_dict = response.model_dump() if hasattr(response, 'model_dump') else vars(response)
                print(json.dumps(response_dict, indent=2)[:1000] + "...")
            except Exception as e:
                print(f"Could not serialize full response for printing: {e}")
                print(str(response)[:1000] + "...")
            print("-- End of Raw Response Snippet --")

            search_results = []
            if response.choices and response.choices[0].message and response.choices[0].message.content:
                main_content = response.choices[0].message.content.strip()
                
                # Placeholder for actual URL/source extraction
                # The Perplexity API (especially online models) might provide citations or sources.
                # How these are provided via the OpenAI-compatible SDK needs to be determined by inspecting a real response.
                # For now, we create one result with the main content as snippet and a placeholder URL.
                
                # Attempt to find sources if they are structured in the response
                # This is speculative and depends on Perplexity's actual response format via OpenAI SDK
                urls_found = []
                if hasattr(response, 'sources') and response.sources: # Example: if sources are a direct attribute
                    for source in response.sources:
                        if isinstance(source, dict) and 'url' in source:
                            urls_found.append(source['url'])
                # Another speculative check: sometimes metadata or context might contain source URLs
                elif response.choices[0].message.context and isinstance(response.choices[0].message.context, dict) and 'sources' in response.choices[0].message.context:
                    for source_info in response.choices[0].message.context['sources']:
                        if isinstance(source_info, dict) and 'url' in source_info:
                            urls_found.append(source_info['url'])
                
                if urls_found:
                    for url in urls_found:
                        # If we have multiple URLs, we might create multiple search_results items
                        # or associate all URLs with the single snippet. For now, let's create one entry per URL with the same snippet.
                        search_results.append({"url": url, "snippet": main_content[:500]}) # Truncate snippet if too long
                else:
                    # If no specific URLs found, use main content as snippet with a placeholder URL
                    search_results.append({"url": "https://perplexity.ai/search", "snippet": main_content})
            else:
                print("Perplexity API did not return the expected content structure.")
                return [] # Return empty list if no valid content

            if not search_results:
                 print("Warning: No content processed into search_results, though API call may have succeeded.")
                 # Fallback to a generic entry if nothing specific was parsed but we got some content
                 if main_content:
                    search_results.append({"url": "https://perplexity.ai/search/unknown_source", "snippet": main_content})

            return search_results

        except Exception as e:
            print(f"Error calling Perplexity API: {e}")
            # In case of an API error, return an empty list or re-raise depending on desired handling
            return [] 