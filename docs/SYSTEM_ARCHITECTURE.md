# AI-Powered Inventory Locator - System Architecture & Flow Documentation

## Table of Contents
1. [High-Level System Architecture](#1-high-level-system-architecture)
2. [Complete User Journey Flowchart](#2-complete-user-journey-flowchart)
3. [Data Flow Diagram](#3-data-flow-diagram)
4. [API Integration Points](#4-api-integration-points)
5. [File Structure & Responsibilities](#5-file-structure--responsibilities)
6. [Key Decision Logic](#6-key-decision-logic)
7. [Environment Configuration](#7-environment-configuration)

---

## 1. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
│                    (Flask Web Application)                      │
│                      localhost:5001                             │
└────────────┬────────────────────────────────────┬───────────────┘
             │                                    │
             ▼                                    ▼
┌────────────────────────┐          ┌────────────────────────────┐
│  PRODUCT IDENTIFICATION │          │   RETAILER DATA AGENT      │
│        AGENT            │          │                            │
│  Google Cloud Vision    │          │       SerpAPI              │
│     OCR API             │          │  - Google Shopping         │
│                         │          │  - Immersive Product API   │
└────────────────────────┘          └────────────────────────────┘
             │                                    │
             └──────────────┬─────────────────────┘
                            ▼
                ┌───────────────────────┐
                │   RANKING AGENT       │
                │                       │
                │  Flask Backend        │
                │  - Categorization     │
                │  - Nearby vs Online   │
                │  - Store Sorting      │
                └───────────────────────┘
```

### Multi-Agent System Components

The system implements a three-agent architecture:

1. **Product Identification Agent** ([models/ocr_processor.py](../models/ocr_processor.py))
   - Extracts text from product images using Google Cloud Vision API
   - Converts images to Base64 for API transmission
   - Returns structured response with extracted text

2. **Retailer Data Agent** ([backend/api/api_retrieval.py](../backend/api/api_retrieval.py))
   - Two-step product lookup pipeline via SerpAPI
   - Step 1: Generic product search via Google Shopping
   - Step 2: Detailed location lookup via Google Immersive Product API

3. **Ranking Agent** ([ui/app.py](../ui/app.py))
   - Orchestrates the complete workflow
   - Categorizes stores as "nearby" vs "online-only"
   - Sorts and ranks results by availability

---

## 2. Complete User Journey Flowchart

```
                          ┌──────────────┐
                          │  User Opens  │
                          │   App @:5001 │
                          └──────┬───────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  Upload Product Image  │
                    │  (Drag & Drop / Click) │
                    └────────┬───────────────┘
                             │
                             ▼
┌────────────────────────────────────────────────────────────────┐
│                    IMAGE UPLOAD PROCESSING                     │
│                       (POST /upload)                           │
├────────────────────────────────────────────────────────────────┤
│  1. Validate file type (png, jpg, jpeg, gif, bmp, webp)       │
│  2. Generate unique filename (UUID)                            │
│  3. Save to ui/uploads/                                        │
│  4. Call OCR Processor                                         │
└────────────┬───────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│              OCR PROCESSING (Google Vision API)                │
│              models/ocr_processor.py                           │
├────────────────────────────────────────────────────────────────┤
│  1. Read image file                                            │
│  2. Convert to Base64 encoding                                 │
│  3. Send to: vision.googleapis.com/v1/images:annotate          │
│  4. Extract text from response['textAnnotations'][0]           │
│  5. Return: {success: bool, text: str, error: str}            │
└────────────┬───────────────────────────────────────────────────┘
             │
             ▼
        ┌──────────┐      NO    ┌─────────────────┐
        │Text Found?├────────────►│ Show Error      │
        └────┬─────┘             │ Clean up file   │
             │ YES               └─────────────────┘
             ▼
┌────────────────────────────┐
│  Display Extracted Text    │
│  "Review and Search"       │
│                            │
│  User clicks:              │
│  "Search for Products"     │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────────┐
│              PRODUCT SEARCH (POST /search)                     │
│              backend/api/api_retrieval.py                      │
├────────────────────────────────────────────────────────────────┤
│  Function: get_product_results(query, user_location)          │
│                                                                │
│  1. Build SerpAPI request:                                     │
│     - engine: "google_shopping"                                │
│     - q: extracted_text                                        │
│     - location: "Fayetteville, Arkansas, United States"        │
│     - gl: "us", hl: "en"                                       │
│                                                                │
│  2. GoogleSearch(params).get_dict()                            │
│                                                                │
│  3. Extract shopping_results (top 5 products)                  │
│     For each product:                                          │
│     - title, price, source, thumbnail                          │
│     - rating, reviews                                          │
│     - immersive_product_page_token (KEY for next step!)        │
└────────────┬───────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────┐
│  Display Products Grid     │
│  (5 product cards)         │
│                            │
│  User clicks a product     │
└────────┬───────────────────┘
         │
         ▼
┌────────────────────────────────────────────────────────────────┐
│         STORE LOCATION LOOKUP (GET /product/<token>)           │
│         backend/api/api_retrieval.py                           │
├────────────────────────────────────────────────────────────────┤
│  Function: get_product_locations(page_token)                   │
│                                                                │
│  1. Build SerpAPI request:                                     │
│     - engine: "google_immersive_product"                       │
│     - page_token: immersive_product_page_token                 │
│                                                                │
│  2. GoogleSearch(params).get_dict()                            │
│                                                                │
│  3. Extract product_results.stores[] array                     │
│     For each store:                                            │
│     - name, price, link, logo                                  │
│     - details_and_offers[] (contains "nearby" indicator)       │
│     - tag (can be "nearby")                                    │
│     - rating, reviews, shipping, total                         │
└────────────┬───────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│              RANKING & CATEGORIZATION (Flask)                  │
│              ui/app.py (lines 208-218)                         │
├────────────────────────────────────────────────────────────────┤
│  For each store in results:                                    │
│                                                                │
│    1. Check if "nearby" in details_and_offers[] (lowercase)    │
│    2. Check if tag == "nearby"                                 │
│                                                                │
│    IF nearby:                                                  │
│      ├─► Add to nearby_stores[]                                │
│    ELSE:                                                       │
│      └─► Add to online_stores[]                                │
│                                                                │
│  Return categorized lists to frontend                          │
└────────────┬───────────────────────────────────────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────┐
│                  DISPLAY STORE RESULTS                         │
│                  ui/templates/index.html                       │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  🎯 AVAILABLE NEARBY                                           │
│  ┌────────────────────────────────────┐                       │
│  │ Walmart          [NEARBY]          │                       │
│  │ $12.99                             │                       │
│  │ ★ 4.5 (1,234 reviews)             │                       │
│  │ In stock • Pick up today           │                       │
│  │ [View at Store →]                  │                       │
│  └────────────────────────────────────┘                       │
│                                                                │
│  📦 ONLINE OPTIONS                                             │
│  ┌────────────────────────────────────┐                       │
│  │ Amazon           [ONLINE]          │                       │
│  │ $11.49                             │                       │
│  │ Free shipping • Arrives in 2 days  │                       │
│  │ [View at Store →]                  │                       │
│  └────────────────────────────────────┘                       │
│                                                                │
│  User clicks link → Opens retailer website                     │
└────────────────────────────────────────────────────────────────┘
```

---

## 3. Data Flow Diagram

```
INPUT: Product Image
    │
    ├──► [1] Base64 Encoding
    │         │
    │         ▼
    │    Google Vision API
    │         │
    │         ▼
    └──► Extracted Text: "Tylenol Extra Strength 500mg"
              │
              │
    ├─────────┴─────────┐
    │                   │
    ▼                   ▼
Google Shopping    User Location
"Tylenol..."       "Fayetteville, AR"
    │
    ▼
SerpAPI Response:
{
  shopping_results: [
    {
      title: "Tylenol Extra Strength...",
      price: "$12.99",
      source: "Walmart",
      immersive_product_page_token: "abc123..."  ◄─── CRITICAL
    },
    {...}
  ]
}
    │
    ▼
User Selects Product
    │
    ▼
GET /product/abc123...
    │
    ▼
Google Immersive Product API
    │
    ▼
{
  product_results: {
    title: "Tylenol Extra Strength 500mg",
    stores: [
      {
        name: "Walmart",
        price: "$12.99",
        details_and_offers: ["In stock nearby", "Pick up today"],
        tag: "nearby"  ◄─── Categorization key
      },
      {
        name: "Amazon",
        price: "$11.49",
        details_and_offers: ["Free shipping"],
        tag: ""  ◄─── Online-only
      }
    ]
  }
}
    │
    ▼
CATEGORIZATION:
    │
    ├─► nearby_stores[] = [Walmart]
    │
    └─► online_stores[] = [Amazon]
         │
         ▼
    Display to User
```

### Key Data Transformation Points

1. **Image → Text**: Binary image data converted to Base64, sent to Google Vision, returns plain text
2. **Text → Products**: Search query sent to Google Shopping, returns product list with tokens
3. **Token → Stores**: Immersive product token retrieves detailed store availability data
4. **Stores → Categories**: Algorithm separates nearby vs online stores based on availability indicators

---

## 4. API Integration Points

### External API Calls

#### 1. Google Cloud Vision API

**Endpoint**: `vision.googleapis.com/v1/images:annotate`

**Method**: POST

**Authentication**: API Key (GOOGLE_CLOUD_API_KEY)

**Request Structure**:
```json
{
  "requests": [{
    "image": {
      "content": "base64_image_data"
    },
    "features": [{
      "type": "TEXT_DETECTION",
      "maxResults": 1
    }]
  }]
}
```

**Response Structure**:
```json
{
  "responses": [{
    "textAnnotations": [
      {
        "description": "Full extracted text from image..."
      }
    ]
  }]
}
```

**Code Location**: [models/ocr_processor.py:28](../models/ocr_processor.py#L28)

**Cost**: $1.50 per 1,000 requests after 1,000 free requests/month

---

#### 2. SerpAPI - Google Shopping Search

**Engine**: `google_shopping`

**Authentication**: API Key (SERPAPI_KEY)

**Parameters**:
- `q`: Search query (e.g., "Tylenol Extra Strength")
- `location`: "Fayetteville, Arkansas, United States"
- `gl`: "us" (Google country)
- `hl`: "en" (Language)

**Key Response Fields**:
```json
{
  "shopping_results": [
    {
      "title": "Product name",
      "price": "$12.99",
      "source": "Walmart",
      "thumbnail": "image_url",
      "rating": 4.5,
      "reviews": 1234,
      "immersive_product_page_token": "token_for_next_api_call"
    }
  ]
}
```

**Code Location**: [backend/api/api_retrieval.py:40-77](../backend/api/api_retrieval.py#L40-L77)

**Critical Field**: `immersive_product_page_token` - Required for Step 3

---

#### 3. SerpAPI - Google Immersive Product API

**Engine**: `google_immersive_product`

**Authentication**: API Key (SERPAPI_KEY)

**Parameters**:
- `page_token`: The `immersive_product_page_token` from Google Shopping results

**Key Response Fields**:
```json
{
  "product_results": {
    "title": "Product name",
    "brand": "Brand name",
    "rating": 4.5,
    "reviews": 5000,
    "price_range": "$10 - $15",
    "stores": [
      {
        "name": "Walmart",
        "price": "$12.99",
        "link": "store_url",
        "logo": "logo_url",
        "details_and_offers": [
          "In stock nearby",
          "Pick up today"
        ],
        "tag": "nearby",
        "shipping": "Free pickup",
        "total": "$12.99"
      }
    ]
  }
}
```

**Code Location**: [backend/api/api_retrieval.py:4-38](../backend/api/api_retrieval.py#L4-L38)

**Cost**: $50/month for 5,000 searches (100 free searches/month)

---

## 5. File Structure & Responsibilities

### Backend Components

#### Flask Application: `ui/app.py`

**Line 58-118**: `POST /upload` endpoint
- Validates file upload
- Saves image with unique UUID filename
- Calls OCR processor
- Returns extracted text to frontend

**Line 120-165**: `POST /search` endpoint
- Receives search query (from OCR or manual input)
- Calls `get_product_results()` from api_retrieval
- Returns top 5 product matches

**Line 168-239**: `GET /product/<page_token>` endpoint
- Receives immersive product page token
- Calls `get_product_locations()` from api_retrieval
- **Lines 208-218**: Categorization logic (nearby vs online)
- Returns categorized store lists

**Line 242-249**: `GET /health` endpoint
- System health check
- Verifies API key configuration

---

#### OCR Processor: `models/ocr_processor.py`

**Line 9-98**: `extract_text_from_image(image_path, api_key)`
- Reads image file from disk
- Encodes to Base64 (line 25)
- Sends POST request to Google Vision API (line 43)
- Parses response and extracts text (line 66-68)
- Returns structured dict: `{success: bool, text: str, error: str}`

**Error Handling**:
- File not found (line 87-92)
- API errors (line 58-63)
- No text detected (line 74-79)

---

#### API Retrieval: `backend/api/api_retrieval.py`

**Line 40-77**: `get_product_results(query, user_location)`
- Configures Google Shopping search parameters
- Executes SerpAPI request
- Returns shopping_results array
- Critical output: `immersive_product_page_token` for each product

**Line 4-38**: `get_product_locations(page_token)`
- Configures Google Immersive Product parameters
- Executes SerpAPI request
- Returns full product_results with stores array
- Includes debugging output (line 35)

---

### Frontend Components

#### HTML/JavaScript: `ui/templates/index.html`

**Line 444-474**: `uploadImage(file)` function
- Creates FormData with image
- POSTs to `/upload` endpoint
- Displays extracted text
- Shows success/error messages

**Line 476-509**: `searchProducts()` function
- Sends extracted text as search query
- POSTs to `/search` endpoint
- Calls `displayProducts()` with results
- Transitions from upload view to results view

**Line 532-560**: `selectProduct(product, index)` function
- Triggered when user clicks a product card
- Fetches detailed store data via GET `/product/<token>`
- Shows loading spinner
- Calls `displayProductDetails()` with response

**Line 562-606**: `displayProductDetails(data)` function
- Renders product information
- Separates nearby_stores and online_stores
- Creates store cards with `createStoreCard()`
- Displays badges (NEARBY vs ONLINE)

**Line 608-624**: `createStoreCard(store, isNearby)` function
- Generates HTML for individual store
- Adds appropriate badge
- Includes pricing, ratings, shipping info
- Creates "View at Store" link

---

## 6. Key Decision Logic

### Nearby vs Online Categorization Algorithm

**Location**: [ui/app.py:208-218](../ui/app.py#L208-L218)

```python
# For each store in stores_data:
is_nearby = False

# Check method 1: details_and_offers array
for detail in store.get('details_and_offers', []):
    if 'nearby' in detail.lower():
        is_nearby = True
        break

# Check method 2: tag field
if store.get('tag', '').lower() == 'nearby':
    is_nearby = True

# Categorize
if is_nearby:
    nearby_stores.append(store_info)
else:
    online_stores.append(store_info)
```

### Pseudocode

```
FUNCTION categorize_stores(stores_data):
    nearby_stores = []
    online_stores = []

    FOR each store IN stores_data:
        is_nearby = FALSE

        // Method 1: Check offer text
        FOR each detail IN store.details_and_offers:
            IF "nearby" appears in detail (case-insensitive):
                is_nearby = TRUE
                EXIT FOR loop

        // Method 2: Check tag
        IF store.tag equals "nearby" (case-insensitive):
            is_nearby = TRUE

        // Categorize
        IF is_nearby:
            ADD store TO nearby_stores
        ELSE:
            ADD store TO online_stores

    RETURN nearby_stores, online_stores
```

### Matching Criteria

A store is classified as "NEARBY" if **either** condition is true:

1. **Details Check**: The string "nearby" (case-insensitive) appears in any element of the `details_and_offers[]` array
2. **Tag Check**: The `tag` field exactly equals "nearby" (case-insensitive)

Common nearby indicators in Google data:
- "In stock nearby"
- "Available nearby"
- "Pick up today"
- "Store pickup available"

---

## 7. Environment Configuration

### Required Environment Variables

Location: `.env.development` (for Docker) or `.env` (for local development)

```bash
# Google Cloud Vision API Key
GOOGLE_CLOUD_API_KEY=your_google_vision_api_key_here
# Used by: models/ocr_processor.py:28
# Get from: https://console.cloud.google.com/apis/credentials

# SerpAPI Key
SERPAPI_KEY=your_serpapi_key_here
# Used by: backend/api/api_retrieval.py:2
# Get from: https://serpapi.com/manage-api-key

# Default User Location
USER_LOCATION=Fayetteville, Arkansas, United States
# Used by: ui/app.py:44 → api_retrieval.py:63
# Format: "City, State, Country"
```

### Optional Configuration

```bash
# Flask Security
FLASK_SECRET_KEY=your_random_secret_key_here
# Required for production, auto-generated for development
# Generate with: python -c "import secrets; print(secrets.token_hex(32))"

# Upload Settings
UPLOAD_FOLDER=ui/uploads
# Directory for temporary image storage

MAX_UPLOAD_SIZE=10485760
# Maximum file size in bytes (default: 10MB)

# Flask Environment
FLASK_ENV=development
# Options: development, production

FLASK_DEBUG=False
# Enable Flask debug mode (only for development)
```

### API Key Setup

See [API_KEY_SETUP.md](API_KEY_SETUP.md) for detailed instructions on obtaining and configuring API keys.

---

## System Flow Summary

The AI-Powered Inventory Locator implements a sophisticated three-agent pipeline:

1. **Upload Phase**: User uploads product image → Flask validates and saves → Calls OCR Agent
2. **OCR Phase**: Image converted to Base64 → Google Vision API extracts text → Returns to user for confirmation
3. **Search Phase**: Confirmed text sent to Retailer Data Agent → Google Shopping returns 5 products with tokens
4. **Selection Phase**: User selects product → Token sent to Immersive Product API → Returns store availability data
5. **Ranking Phase**: Ranking Agent categorizes stores → Separates nearby vs online → Returns categorized results
6. **Display Phase**: Frontend renders nearby stores first, online stores second → User clicks to visit retailer

**Key Innovation**: The two-step SerpAPI integration using `immersive_product_page_token` bridges generic product search to detailed local availability, solving the core problem of finding products in stock nearby.

---

**Documentation Version**: 1.0
**Last Updated**: 2025-11-20
**Project**: ISYS57103-Fall25-GroupProject
**Team**: Thomas, Lalitsingh, Peggy
