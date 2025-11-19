# Quick Start Guide - AI-Powered Inventory Locator

## What This Application Does

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

## Quick Start (Docker - Recommended)

Docker provides the fastest and most consistent setup experience.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed
- API keys from:
  - [SerpAPI](https://serpapi.com/) - 100 free searches/month
  - [Google Cloud Vision](https://console.cloud.google.com/) - 1000 free requests/month

### Setup Steps

1. **Clone and navigate to the repository**
   ```bash
   cd AI-Project
   ```

2. **Configure environment variables**
   ```bash
   # Copy the template
   cp .env.development .env.development

   # Edit and add your API keys
   # SERPAPI_KEY=your_key_here
   # GOOGLE_CLOUD_API_KEY=your_key_here
   ```

3. **Start the application**
   ```bash
   ./scripts/run_local.sh
   ```

   Or manually:
   ```bash
   docker-compose up --build
   ```

4. **Access the application**

   Open your browser to: **http://localhost:5000**

5. **Test it out**
   - Upload a product image
   - Wait for OCR processing
   - Search for products
   - View nearby store availability

That's it! The application is now running in an isolated Docker container with all dependencies installed.

For detailed Docker documentation, see [docs/DOCKER_SETUP.md](docs/DOCKER_SETUP.md)

---

## Alternative: Traditional Python Setup

If you prefer to run without Docker:

### Prerequisites Checklist

- [ ] Python 3.9+ installed
- [ ] Virtual environment activated
- [ ] Google Cloud Vision API key obtained
- [ ] SerpAPI key obtained
- [ ] `.env` file configured

### Step-by-Step Launch

### 1. Activate Virtual Environment

```bash
cd "/Users/thomasburns/Documents/MISGrad/Fall 2025/Demystifying AI/AI-Project"
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

## For Your Report/Presentation

Key metrics to highlight:

- **Two-step pipeline:** Generic search → User confirmation → Location lookup
- **APIs integrated:** Google Cloud Vision, SerpAPI (Google Shopping + Immersive Product)
- **User flow:** Image upload → OCR → Search → Select → Results (4 steps)
- **Technology stack:** Python, Flask, HTML/CSS/JavaScript
- **Scope:** Proof of concept for academic project

## Shutting Down

To stop the server:
- Press `Ctrl+C` in the terminal

To deactivate virtual environment:
```bash
deactivate
```

---

**Success Criteria:**
- [ ] Server starts without errors
- [ ] Health check returns "healthy"
- [ ] Can upload image successfully
- [ ] OCR extracts text from image
- [ ] Product search returns results
- [ ] Product details show store locations
- [ ] Nearby vs online stores are differentiated

**Next:** Test with a real product image and document results for your project report!
