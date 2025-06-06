from config import PERPLEXITY_API_KEY
from openai import OpenAI # Import OpenAI
import json # For parsing if sources are in a JSON string
import os

CACHE_FILE = "_cache_search_results.json"
RAW_CACHE_FILE = "_cache_search_agent_raw_api_response.json"

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
        
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, 'r') as f:
                    cached_results = json.load(f)
                print(f"Loaded {len(cached_results)} search results from cache: {CACHE_FILE}")
                return cached_results
            except Exception as e:
                print(f"Error loading search results from cache {CACHE_FILE}: {e}. Proceeding with API call.")

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an AI assistant that researches topics and provides concise, factual information, including sources and search results. "
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
                model="sonar-pro",
                messages=messages,
            )
            
            # Get the full dictionary representation of the response for raw caching
            full_response_dict = {}
            if hasattr(response, 'model_dump'):
                full_response_dict = response.model_dump()
            else:
                try:
                    full_response_dict = json.loads(response.json()) # For some SDK versions
                except AttributeError: # If .json() doesn't exist
                    try:
                        full_response_dict = vars(response) # General fallback
                    except TypeError: # If vars() is not applicable (e.g. for pydantic models directly)
                        # This might be a scenario where response itself is already dict-like or needs specific handling
                        # For now, we'll try to force it to a string and log a warning if it's not a dict
                        print(f"Warning: Could not easily convert response to dict. Saving string representation for raw cache.")
                        full_response_dict = {"raw_string_representation": str(response)}
                except json.JSONDecodeError:
                    print(f"Warning: response.json() did not return valid JSON. Trying vars() for raw cache.")
                    full_response_dict = vars(response)
            
            # Save the raw API response
            try:
                with open(RAW_CACHE_FILE, 'w') as f:
                    json.dump(full_response_dict, f, indent=2)
                print(f"Saved raw API response for SearchAgent to: {RAW_CACHE_FILE}")
            except Exception as e:
                print(f"Error saving raw API response for SearchAgent to {RAW_CACHE_FILE}: {e}")

            search_results_data = []
            
            # Prioritize the structured "search_results" field if available
            if "search_results" in full_response_dict and isinstance(full_response_dict.get("search_results"), list):
                for item in full_response_dict["search_results"]:
                    url = item.get("url")
                    title = item.get("title", "No title provided")
                    # Using title as snippet for now, as per PRD requirement for URL and snippet
                    # Could also use a portion of message.content if more detail per source is needed
                    # and can be mapped, but title is directly associated with the URL here.
                    if url:
                        search_results_data.append({"url": url, "snippet": title})
                if search_results_data:
                    print(f"Processed {len(search_results_data)} items from API's 'search_results' field.")

            # Fallback or augmentation: if no structured search_results, or if we also want the main content
            # For now, the PRD implies distinct URL/snippet pairs, so structured search_results are preferred.
            # If search_results_data is still empty, but we have main content, use that.
            # Adjusting to use full_response_dict for consistency in accessing choices
            choices = full_response_dict.get('choices', [])
            if not search_results_data and choices and isinstance(choices, list) and len(choices) > 0 \
               and isinstance(choices[0], dict) and choices[0].get('message') \
               and isinstance(choices[0]['message'], dict) and choices[0]['message'].get('content'):
                main_content = choices[0]['message']['content'].strip()
                print("Warning: No structured 'search_results' found in API response or it was empty. Using main message content as a single snippet.")
                search_results_data.append({
                    "url": "https://perplexity.ai/summarized_result", # Placeholder for summarized content
                    "snippet": main_content
                })
            elif not choices or not isinstance(choices, list) or len(choices) == 0 \
                 or not isinstance(choices[0], dict) or not choices[0].get('message') \
                 or not isinstance(choices[0]['message'], dict) or not choices[0]['message'].get('content'):
                 print("Perplexity API did not return the expected content structure in choices.")
                 return []

            if not search_results_data:
                print("Warning: Perplexity API call succeeded but no content was processed into search_results_data.")

            if search_results_data: # Save to cache only if we have data
                try:
                    with open(CACHE_FILE, 'w') as f:
                        json.dump(search_results_data, f, indent=2)
                    print(f"Saved {len(search_results_data)} search results to cache: {CACHE_FILE}")
                except Exception as e:
                    print(f"Error saving search results to cache {CACHE_FILE}: {e}")

            return search_results_data

        except Exception as e:
            print(f"Error calling Perplexity API or processing its response: {e}")
            # Ensure traceback is printed for better debugging of other potential errors
            import traceback
            traceback.print_exc()
            return [] 