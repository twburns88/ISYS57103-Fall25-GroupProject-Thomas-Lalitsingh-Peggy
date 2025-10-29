import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
SERPAPI_KEY = os.getenv("SERPAPI_KEY")

BASE_URL = "https://serpapi.com/search.json"
