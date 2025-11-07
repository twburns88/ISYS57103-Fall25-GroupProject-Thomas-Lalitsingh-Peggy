# Product Finder UI - Setup and Usage Guide

## Overview

This is a Flask-based web application that allows users to:
1. Upload a product image from their phone or computer
2. Extract text using Google Cloud Vision OCR
3. Search for products using the extracted text
4. Find nearby store availability and pricing

## Prerequisites

- Python 3.9+
- Google Cloud Vision API key
- SerpAPI key
- Active internet connection

## Setup Instructions

### 1. Install Dependencies

From the project root directory:

```bash
# Activate virtual environment
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Make sure your `.env` file in the project root contains:

```
SERPAPI_KEY=your_serpapi_key_here
GOOGLE_CLOUD_API_KEY=your_google_vision_api_key_here
USER_LOCATION=Fayetteville, Arkansas, United States
FLASK_SECRET_KEY=any_random_string_here
```

**To get API keys:**

- **Google Cloud Vision API:**
  1. Go to https://console.cloud.google.com
  2. Create a new project or select existing
  3. Enable "Cloud Vision API"
  4. Go to Credentials → Create API Key

- **SerpAPI:**
  1. Sign up at https://serpapi.com
  2. Get your API key from the dashboard
  3. Free tier includes 100 searches/month

### 3. Run the Application

```bash
# From the project root
cd ui
python app.py
```

The server will start at `http://localhost:5000`

## Usage

### Step 1: Upload Product Image

1. Open http://localhost:5000 in your browser
2. Click the upload zone or drag and drop a product image
3. Wait for OCR processing (typically 2-3 seconds)
4. Review the extracted text

### Step 2: Search for Products

1. Click "Search for Products" button
2. View the top 5 matching products
3. Click on the correct product that matches your image

### Step 3: View Store Availability

1. See nearby stores with "Available Nearby" badge
2. See online-only options
3. Compare prices across stores
4. Click "View at Store" to visit the retailer's website

## Features

- **Image Upload:** Support for multiple image formats (PNG, JPG, JPEG, GIF, BMP, WEBP)
- **OCR Processing:** Automatic text extraction from product images
- **Product Search:** Real-time product search via Google Shopping
- **Location-Aware:** Shows nearby vs online-only availability
- **Price Comparison:** Compare prices across multiple retailers
- **Mobile-Friendly:** Responsive design works on phones and tablets

## Troubleshooting

### "Google Vision API key not configured"
- Make sure `GOOGLE_CLOUD_API_KEY` is set in your `.env` file
- Verify the API key is valid and has Cloud Vision API enabled

### "No text detected in image"
- Try a clearer image with better lighting
- Ensure the product label/text is visible and in focus
- Avoid images with heavy glare or shadows

### "No products found"
- The extracted text might not match product names
- Try uploading a different angle of the product
- Manually edit the search query if needed

### "Failed to get product details"
- Some products may not have detailed availability data
- Try a different product from the search results
- Check your SerpAPI quota (100 free searches/month)

### Port Already in Use
If port 5000 is busy, you can change it in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Changed to 8080
```

## File Structure

```
ui/
├── app.py                  # Flask application
├── templates/
│   └── index.html          # Main UI template
├── uploads/                # Uploaded images (auto-created)
└── README.md              # This file
```

## API Endpoints

### `GET /`
- Main page with upload interface

### `POST /upload`
- Upload image and extract text via OCR
- **Body:** multipart/form-data with 'image' field
- **Returns:** `{success: true, extracted_text: "..."}`

### `POST /search`
- Search for products
- **Body:** `{query: "product name"}`
- **Returns:** `{success: true, products: [...]}`

### `GET /product/<page_token>`
- Get detailed product info and store locations
- **Returns:** `{success: true, product: {...}, nearby_stores: [...], online_stores: [...]}`

### `GET /health`
- Health check endpoint
- **Returns:** `{status: "healthy", google_vision_configured: true, serpapi_configured: true}`

## Development Notes

- The app runs in debug mode by default (don't use in production)
- Uploaded images are stored in `ui/uploads/` directory
- Images are cleaned up after OCR processing
- Session data is used to track uploads

## Production Deployment (Future)

For production deployment:
1. Set `debug=False` in `app.py`
2. Use a production WSGI server (gunicorn, uWSGI)
3. Set up proper SSL/HTTPS
4. Configure proper file upload limits
5. Add authentication if needed
6. Set up proper logging

## Cost Considerations

- **Google Cloud Vision:** $1.50 per 1000 images after free tier
- **SerpAPI:** Free tier (100 searches/month), then $50/month for 5000 searches
- For academic projects, free tiers should be sufficient

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review API documentation:
   - [Google Cloud Vision](https://cloud.google.com/vision/docs)
   - [SerpAPI](https://serpapi.com/search-api)
3. Check the project repository issues

---

**Built for:** Demystifying AI Course - Fall 2025
**Project:** AI-Powered Inventory Locator System
