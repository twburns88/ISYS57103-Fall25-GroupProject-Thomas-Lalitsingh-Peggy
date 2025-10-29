from .api.serpapi_client import get_product_results

if __name__ == "__main__":
    query = "coffee maker"
    user_location = "Fayetteville, Arkansas, United States"  # Optional: specify user location
    results = get_product_results(query=query)

    if not results.get("shopping_results"):
        print("No results found for your location, showing general results...")
        results = get_product_results(query=query)

    for product in results.get("shopping_results", []):
        title = product.get("title")
        price = product.get("price")
        store = product.get("source")
        location = product.get("location", "N/A")

        print(f"Title: {title}")
        print(f"Price: {price}")
        print(f"Store: {store}")
        print(f"Location: {location}")
        print("-" * 40)
