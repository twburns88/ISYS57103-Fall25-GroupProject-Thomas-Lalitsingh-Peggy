"""
Test script for two-step product lookup pipeline:
Step 1: Generic product search (get product IDs)
Step 2: Product-specific location lookup (using product ID)

This validates that SerpAPI returns product IDs and that those IDs
can be used to query the Google Product API for location data.
"""

import sys
import os
# Add parent directory to path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.api.api_retrieval import get_product_results, get_product_locations
import json

def test_pipeline():
    """Test the full two-step product lookup pipeline"""

    print("="*60)
    print("STEP 1: Generic Product Search")
    print("="*60)

    # Step 1: Search for a common product
    query = "Tylenol Extra Strength"
    user_location = "Fayetteville, Arkansas, United States"

    print(f"\nSearching for: '{query}'")
    print(f"Location: {user_location}\n")

    results = get_product_results(query=query, user_location=user_location)

    if not results or "shopping_results" not in results:
        print("ERROR: No shopping results returned!")
        return

    shopping_results = results["shopping_results"]
    print(f"Found {len(shopping_results)} products\n")

    # Display first 3 results with product IDs
    print("Top 3 results:")
    print("-"*60)

    for i, product in enumerate(shopping_results[:3], 1):
        title = product.get("title", "N/A")
        price = product.get("price", "N/A")
        source = product.get("source", "N/A")
        product_id = product.get("product_id", None)
        product_link = product.get("product_link", None)
        link = product.get("link", None)

        print(f"\n{i}. {title}")
        print(f"   Price: {price}")
        print(f"   Source: {source}")
        print(f"   Product ID: {product_id}")
        print(f"   Product Link: {product_link}")
        print(f"   Link: {link}")

        # Check if product_id exists
        if not product_id:
            print("   ⚠️  WARNING: No product_id found!")

    # Debug: Show full structure of first product
    print("\n" + "="*60)
    print("DEBUG: Full First Product Data Structure")
    print("="*60)
    first_product = shopping_results[0]
    print(json.dumps(first_product, indent=2))

    print("\n" + "="*60)
    print("STEP 2: Product Location Lookup")
    print("="*60)

    # Step 2: Try to get location data for the first product
    page_token = first_product.get("immersive_product_page_token")

    if not page_token:
        print("\n❌ PIPELINE BLOCKED: First product has no immersive_product_page_token!")
        return

    print(f"\nQuerying Google Immersive Product API")
    print(f"Product: {first_product.get('title')}")
    print(f"Using page_token: {page_token[:50]}...\n")

    location_data = get_product_locations(page_token=page_token)

    if "error" in location_data:
        print(f"❌ ERROR: {location_data['error']}")
        return

    print("\n✅ SUCCESS: Product location data retrieved!")
    print("\nFull response structure:")
    print(json.dumps(location_data, indent=2, default=str))

    # Check for specific location-related fields
    print("\n" + "="*60)
    print("ANALYZING LOCATION DATA")
    print("="*60)

    # Check if stores data exists
    if "product_results" in location_data and "stores" in location_data["product_results"]:
        stores = location_data["product_results"]["stores"]
        print(f"\n✅ Found {len(stores)} stores with availability data!\n")

        # Analyze each store for location indicators
        nearby_stores = []
        online_only_stores = []

        for store in stores:
            store_name = store.get("name", "Unknown")
            details = store.get("details_and_offers", [])
            tag = store.get("tag", "")
            price = store.get("price", "N/A")

            # Check for nearby availability
            is_nearby = False
            for detail in details:
                if "nearby" in detail.lower():
                    is_nearby = True
                    nearby_stores.append({
                        "name": store_name,
                        "price": price,
                        "tag": tag,
                        "availability": detail
                    })
                    break

            if not is_nearby:
                online_only_stores.append({
                    "name": store_name,
                    "price": price,
                    "availability": details[0] if details else "Unknown"
                })

        # Display results
        if nearby_stores:
            print("🎯 NEARBY AVAILABILITY:")
            print("-" * 60)
            for store in nearby_stores:
                print(f"  {store['name']}")
                print(f"    Price: {store['price']}")
                print(f"    Status: {store['availability']}")
                if store['tag']:
                    print(f"    Tag: {store['tag']}")
                print()

        if online_only_stores:
            print("\n📦 ONLINE ONLY:")
            print("-" * 60)
            for store in online_only_stores:
                print(f"  {store['name']}")
                print(f"    Price: {store['price']}")
                print(f"    Status: {store['availability']}")
                print()

    else:
        print("❌ No store location data found in response")

    print("\n" + "="*60)
    print("PIPELINE TEST COMPLETE")
    print("="*60)


if __name__ == "__main__":
    test_pipeline()
