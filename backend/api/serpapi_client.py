from serpapi import GoogleSearch
from backend.config import SERPAPI_KEY

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
