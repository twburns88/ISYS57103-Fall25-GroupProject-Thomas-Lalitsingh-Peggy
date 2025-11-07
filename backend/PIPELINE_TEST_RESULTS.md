# Two-Step Product Lookup Pipeline - Test Results

**Date:** November 4, 2025
**Status:** ✅ **PIPELINE WORKS!**

---

## Summary

The two-step product lookup pipeline has been successfully implemented and tested. The pipeline allows users to:
1. Search for products using generic text (from OCR or manual input)
2. Select the correct product from results
3. Get detailed store location and availability data

---

## API Architecture

### Step 1: Generic Product Search
- **API:** Google Shopping via SerpAPI
- **Engine:** `google_shopping`
- **Input:** Product name/description (e.g., "Tylenol Extra Strength")
- **Output:** List of products with:
  - Product ID
  - Title, price, source
  - **`immersive_product_page_token`** ← Key for Step 2
  - Thumbnail image
  - Rating and reviews

### Step 2: Product Location Lookup
- **API:** Google Immersive Product via SerpAPI
- **Engine:** `google_immersive_product`
- **Input:** `page_token` from Step 1 results
- **Output:** Detailed product data including:
  - Store names (Walgreens, Target, CVS, Walmart, etc.)
  - Online availability
  - **Local availability ("In stock online and nearby")**
  - Pricing per store
  - Delivery options
  - Store ratings and reviews

---

## Key Findings

### ✅ What Works

1. **Product IDs are available** - Every search result includes a `product_id` and `immersive_product_page_token`
2. **Page token approach works** - The `immersive_product_page_token` successfully retrieves location data
3. **Store data is comprehensive** - Includes:
   - Store name (Walgreens, Target, CVS, etc.)
   - Store-specific pricing
   - Availability status ("In stock online and nearby", "In stock online")
   - Delivery options
   - Payment methods accepted
   - Store ratings and reviews
   - Links to product pages

4. **Location awareness** - Results show "nearby" availability when queried with location parameter

### ⚠️ Important Notes

1. **Google Product API is deprecated** - Had to use Google Immersive Product API instead
2. **Page tokens, not product IDs** - Must use `immersive_product_page_token` field, not `product_id`
3. **API call cost** - Each user flow requires 2 SerpAPI calls (acceptable for academic project)

---

## Data Structure Example

### Step 1 Response (Shopping Search):
```json
{
  "shopping_results": [
    {
      "position": 1,
      "title": "Tylenol Extra Strength Rapid Release Gels",
      "product_id": "5979770365228373519",
      "immersive_product_page_token": "eyJlaSI6IlpvVUthYnlF...",
      "price": "$13.99",
      "source": "Walgreens.com",
      "rating": 4.7,
      "reviews": 8300,
      "extensions": ["Also nearby", "LOW PRICE"]
    }
  ]
}
```

### Step 2 Response (Immersive Product):
```json
{
  "product_results": {
    "title": "Tylenol Extra Strength Rapid Release Gels",
    "brand": "TYLENOL®",
    "price_range": "$4.97-$25.99",
    "stores": [
      {
        "name": "Target",
        "price": "$4.99",
        "rating": 4.7,
        "reviews": 5849,
        "tag": "Best price",
        "details_and_offers": [
          "In stock online and nearby",
          "Same-day delivery on orders $35+",
          "Free 90-day returns"
        ],
        "link": "https://www.target.com/p/tylenol..."
      },
      {
        "name": "CVS Pharmacy",
        "price": "$8.29",
        "rating": 4.7,
        "reviews": 1340,
        "details_and_offers": [
          "In stock online and nearby",
          "Free delivery between Thu - Mon on orders $35+",
          "60-day returns"
        ]
      },
      {
        "name": "Walgreens.com",
        "price": "$13.99",
        "original_price": "$23",
        "rating": 4.5,
        "reviews": 1368,
        "tag": "Most popular",
        "details_and_offers": [
          "In stock online",
          "Delivery $5.99",
          "30-day returns"
        ]
      }
    ]
  }
}
```

---

## Implementation Details

### Function Signatures

**`get_product_results(query: str, user_location: str = None) -> dict`**
- Searches Google Shopping for products
- Returns shopping_results array with product details and page tokens

**`get_product_locations(page_token: str) -> dict`**
- Queries Google Immersive Product API
- Returns detailed product info including store locations and availability

### File Locations
- **API Client:** `backend/api/serpapi_client.py`
- **Test Script:** `backend/test_product_pipeline.py`
- **Config:** `backend/config.py`

---

## Test Results

### Test Query: "Tylenol Extra Strength"
**Location:** Fayetteville, Arkansas, United States

#### Step 1 Results:
- **40 products found**
- **Top 3 sources:** Walgreens, Walmart, Target
- **Price range:** $4.99 - $19.97
- **All products included page tokens:** ✅

#### Step 2 Results:
- **Stores with listings:** Walgreens, Target, CVS, Walmart, Amazon, Sam's Club
- **Availability indicators:** "In stock online and nearby", "In stock online"
- **Price comparison:** $4.99 (Target) to $13.99 (Walgreens)
- **Additional data:** Delivery options, return policies, payment methods

---

## Next Steps for Development

1. **UI Implementation**
   - Camera/upload interface for product images
   - Display Step 1 results as selectable grid (images + titles)
   - Show Step 2 results as sorted list by distance/price

2. **Query Builder**
   - Convert OCR text to optimized search queries
   - Handle brand names, product variants, dosages

3. **Ranking/Sorting**
   - Parse "nearby" vs "online only" availability
   - Sort by price, distance, availability
   - Highlight best options

4. **Error Handling**
   - Handle missing page_tokens
   - Fallback for products without location data
   - User-friendly error messages

5. **Caching** (Optional)
   - Cache Step 1 results to avoid repeated searches
   - Time-limited caching for Step 2 (inventory changes)

---

## Conclusion

**The pipeline is viable and ready for integration.**

The two-step approach successfully:
- ✅ Works around SerpAPI's product ID limitation
- ✅ Provides location-aware availability data
- ✅ Returns store-specific pricing and details
- ✅ Gives users confirmation step (reduces OCR errors)
- ✅ Achieves project goal: "Find where products are available nearby"

**Recommendation:** Proceed with frontend development and integration.
