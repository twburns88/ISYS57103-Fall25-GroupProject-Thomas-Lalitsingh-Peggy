# Product Finder UI

Flask-based web application for AI-powered product search and inventory location.

## Quick Start

See the main [QUICKSTART.md](../QUICKSTART.md) for setup instructions.

For Docker-specific details, see [docs/DOCKER_SETUP.md](../docs/DOCKER_SETUP.md).

## Features

- **Image Upload:** Support for multiple formats (PNG, JPG, JPEG, GIF, BMP, WEBP)
- **OCR Processing:** Google Cloud Vision text extraction
- **Product Search:** Real-time Google Shopping search via SerpAPI
- **Location-Aware:** Nearby vs online-only availability
- **Price Comparison:** Compare across multiple retailers
- **Mobile-Friendly:** Responsive design

## Architecture

```
User uploads image
    ↓
Google Cloud Vision API (OCR)
    ↓
Extract product text
    ↓
SerpAPI Google Shopping Search
    ↓
User selects correct product
    ↓
SerpAPI Google Immersive Product API
    ↓
Display nearby stores + pricing
```

## API Endpoints

### `GET /`
Main page with upload interface

### `POST /upload`
Upload image and extract text via OCR
- **Body:** multipart/form-data with `image` field
- **Returns:** `{success: true, extracted_text: "..."}`

### `POST /search`
Search for products
- **Body:** `{query: "product name"}`
- **Returns:** `{success: true, products: [...]}`

### `GET /product/<page_token>`
Get detailed product info and store locations
- **Returns:** `{success: true, product: {...}, nearby_stores: [...], online_stores: [...]}`

### `GET /health`
Health check endpoint
- **Returns:** `{status: "healthy", google_vision_configured: true, serpapi_configured: true}`

## File Structure

```
ui/
├── app.py                  # Flask application
├── templates/
│   └── index.html          # Main UI template
├── static/
│   ├── css/               # Stylesheets
│   └── js/                # JavaScript
├── uploads/               # Uploaded images (auto-created)
└── README.md             # This file
```

## Configuration

Environment variables (set in `.env.development`):

- `SERPAPI_KEY` - SerpAPI key for product search
- `GOOGLE_CLOUD_API_KEY` - Google Cloud Vision API key for OCR
- `USER_LOCATION` - Default search location
- `FLASK_SECRET_KEY` - Session encryption key
- `FLASK_ENV` - Environment (development/production)

See [docs/API_KEY_SETUP.md](../docs/API_KEY_SETUP.md) for obtaining API keys.

## Development Notes

- Flask runs in debug mode by default (auto-reload enabled)
- Uploaded images stored temporarily in `ui/uploads/`
- Images cleaned up after OCR processing
- Session data tracks uploads

## Cost Considerations

- **Google Cloud Vision:** $1.50 per 1,000 images (after 1,000 free/month)
- **SerpAPI:** Free tier 100 searches/month, then $50/month for 5,000 searches
- Free tiers sufficient for academic projects

## Support

For setup issues or questions:
1. Check [QUICKSTART.md](../QUICKSTART.md) or [docs/TEAM_SETUP_GUIDE.md](../docs/TEAM_SETUP_GUIDE.md)
2. Review API documentation:
   - [Google Cloud Vision](https://cloud.google.com/vision/docs)
   - [SerpAPI](https://serpapi.com/search-api)
