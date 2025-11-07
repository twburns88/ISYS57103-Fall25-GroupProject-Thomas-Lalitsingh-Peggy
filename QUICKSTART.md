# Quick Start Guide - Product Finder App

## What You Built

A complete image-to-product-finder web application with:
- Image upload with OCR text extraction
- Product search via Google Shopping
- Nearby vs online store availability
- Price comparison across retailers

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

## Prerequisites Checklist

- [ ] Python 3.9+ installed
- [ ] Virtual environment activated
- [ ] Google Cloud Vision API key obtained
- [ ] SerpAPI key obtained
- [ ] `.env` file configured

## Step-by-Step Launch

### 1. Activate Virtual Environment

```bash
cd "/Users/path-to-repo"
source .venv/bin/activate
```

### 2. Verify Dependencies

```bash
pip install -r requirements.txt
```

### 3. Check Your `.env` File

Make sure it contains:

```
SERPAPI_KEY=your_actual_serpapi_key
GOOGLE_CLOUD_API_KEY=your_actual_google_vision_key
USER_LOCATION=Fayetteville, Arkansas, United States
```

### 4. Start the Server

```bash
cd ui
python app.py
```

You should see:
```
User location set to: Fayetteville, Arkansas, United States
Starting Flask server...
 * Running on http://0.0.0.0:5000
```

### 5. Test the Application

1. Open browser to: `http://localhost:5000`
2. Upload a product image (take a photo or use one from your computer)
3. Wait for OCR processing
4. Click "Search for Products"
5. Select the correct product
6. View nearby stores and pricing

## Common Issues

### Issue: "GOOGLE_CLOUD_API_KEY not set"
**Solution:** Add your Google Vision API key to `.env` file

### Issue: "Module 'flask' not found"
**Solution:**
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Issue: Port 5000 already in use
**Solution:**
- Stop other processes using port 5000, OR


### Issue: "No text detected in image"
**Solution:**
- Use a clearer image with visible product text
- Ensure good lighting
- Try different angle showing product label


## API Usage Tracking

Monitor your API usage to stay within free tiers:

- **SerpAPI:** https://serpapi.com/dashboard (100 free searches/month)
- **Google Cloud Vision:** https://console.cloud.google.com (1000 free requests/month)

## Shutting Down

To stop the server:
- Press `Ctrl+C` in the terminal

To deactivate virtual environment:
```bash
deactivate
```
