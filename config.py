import os
from dotenv import load_dotenv

load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not PERPLEXITY_API_KEY:
    print("Warning: PERPLEXITY_API_KEY not found in .env file.")

if not GOOGLE_API_KEY:
    print("Warning: GOOGLE_API_KEY not found in .env file.") 