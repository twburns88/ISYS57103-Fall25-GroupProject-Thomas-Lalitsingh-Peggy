from serpapi import GoogleSearch
from backend.config import SERPAPI_KEY

def get_product_locations(page_token: str) -> dict:
    """
    Query Google Immersive Product API via SerpAPI for location/availability data.
    Uses an immersive product page token to get detailed product info including stores.

    Note: Using Google Immersive Product API as Google Product API was discontinued.
    The page_token comes from the 'immersive_product_page_token' field in shopping results.

    Args:
        page_token (str): The immersive product page token from shopping results.
    Returns:
        dict: A dictionary containing product location/availability results.
    """

    # Define search parameters for Google Immersive Product API
    params = {
        "engine": "google_immersive_product",
        "page_token": page_token,
        "api_key": SERPAPI_KEY,
    }

    # Perform the search and get results
    search = GoogleSearch(params)
    data = search.get_dict()

    # Return relevant data
    if "error" in data:
        print("Error:", data["error"])
        return {"error": data["error"]}

    # Print available keys for debugging
    print("Available response keys:", list(data.keys()))

    # Return the full response for now to see what's available
    return data

def get_product_results(query: str, user_location: str = None) -> dict:
    """
    Query Google Shopping via SerpAPI for a given product name.
    Returns structured shopping results including title, price, and source.
    
    Args:
        query (str): The product name to search for.
        user_location (str, optional): The location to tailor search results. Defaults to None.
    Returns:
        dict: A dictionary containing shopping results.
    """

    # Define search parameters
    params = {
        "engine": "google_shopping",  # Using Google Shopping engine
        "q": query,
        "api_key": SERPAPI_KEY,
        "gl": "us",
        "hl": "en",
    }

    # Add user location if provided
    if user_location:
        params["location"] = user_location

    # Perform the search and get results
    search = GoogleSearch(params)
    data = search.get_dict()

    if "shopping_results" in data:
        return {"shopping_results": data["shopping_results"]}
    else:
        print("No shopping results found.")
        print("Full response keys:", list(data.keys()))
        if "error" in data:
            print("Error:", data["error"])
        return {}
