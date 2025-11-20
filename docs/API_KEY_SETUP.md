# Getting Your Own API Keys
**Step-by-step guide for SerpAPI and Google Cloud Vision**

---

## Part 1: SerpAPI Key

SerpAPI provides access to Google Shopping search results.

### Step 1: Create Account
1. Go to: **https://serpapi.com/**
2. Click **"Sign Up"** in the top right
3. Sign up with:
   - Email (school or personal)
   - OR Sign up with Google

### Step 2: Verify Email
1. Check your email inbox
2. Click the verification link
3. You'll be redirected to the SerpAPI dashboard

### Step 3: Get Your API Key
1. After logging in, you'll see your dashboard
2. Look for **"Your Private API Key"** section
3. You'll see something like: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6...`
4. Click the **Copy** button
5. **Save this somewhere safe**

### Free Tier Includes:
- 100 searches per month
- No credit card required
- Resets every month

---

## Part 2: Google Cloud Vision API Key

Google Cloud Vision handles OCR (text extraction from images).

### Step 1: Create Google Cloud Account
1. Go to: **https://console.cloud.google.com/**
2. Sign in with your Google account
3. If first time:
   - Click **"Try for free"** or **"Get started for free"**
   - Accept the terms of service
   - Enter payment info (required but you won't be charged)
   - You get $300 free credit

### Step 2: Create a New Project
1. Click the project dropdown at the top (says "Select a project")
2. Click **"New Project"**
3. Name it: `AI-Inventory-Project` (or your preference)
4. Click **"Create"**
5. Wait for creation to complete
6. Make sure your new project is selected (check the top dropdown)

### Step 3: Enable Cloud Vision API
1. In the search bar at the top, type: **"Cloud Vision API"**
2. Click on **"Cloud Vision API"** in the results
3. Click the blue **"Enable"** button
4. Wait for it to enable

### Step 4: Create API Key
1. Click hamburger menu (three lines) in the top left
2. Go to: **"APIs & Services"** → **"Credentials"**
3. Click **"+ CREATE CREDENTIALS"** at the top
4. Select **"API key"**
5. A popup shows your API key (looks like: `AIzaSyA...`)
6. Click **"Copy"**
7. **Save this somewhere safe**

### Step 5: Restrict Your API Key (Recommended)
Prevents unauthorized use if your key is exposed:

1. On the credentials page, find your API key
2. Click the pencil icon (Edit)
3. Under **"API restrictions"**:
   - Select **"Restrict key"**
   - Check only: **"Cloud Vision API"**
4. Click **"Save"**

### Free Tier Includes:
- 1,000 OCR requests per month
- $300 free credit (first year)
- After free tier: $1.50 per 1,000 requests

---

## Part 3: Add Keys to Your Project

### Step 1: Locate the Configuration File
1. Navigate to your AI-Project folder
2. Find the file: `.env.development`
   - **Windows**: Enable hidden files (File Explorer → View → Hidden items)
   - **Mac**: Press `Cmd + Shift + .` in Finder

### Step 2: Edit the File
1. Right-click `.env.development` → Open With → Text editor
2. Find these lines:
   ```
   SERPAPI_KEY=your_dev_serpapi_key_here
   GOOGLE_CLOUD_API_KEY=your_dev_google_api_key_here
   ```

3. Replace with your keys:
   ```
   SERPAPI_KEY=your_actual_key_here
   GOOGLE_CLOUD_API_KEY=your_actual_key_here
   ```

4. **Save the file** (Ctrl+S or Cmd+S)

### Step 3: Test Configuration
1. Start your Docker container: `docker-compose up`
2. Open browser: http://localhost:5000
3. Upload a product image
4. If it processes successfully, your keys are working

---

## Security Best Practices

**DO:**
- Keep keys in `.env.development` (already gitignored)
- Restrict keys in API consoles
- Regenerate keys if exposed

**DON'T:**
- Commit keys to GitHub
- Share keys publicly
- Post keys in chat/email
- Include keys in screenshots

**If a key is exposed:**
1. Go to the API console
2. Delete the compromised key
3. Create a new one
4. Update `.env.development`

---

## Monitoring Usage

### SerpAPI
- Dashboard: https://serpapi.com/dashboard
- Shows search count
- Resets monthly on the 1st

### Google Cloud
- Console: https://console.cloud.google.com/
- Navigate to "APIs & Services" → "Dashboard"
- View Cloud Vision API usage

---

## Troubleshooting

### "Invalid API key" Error
**Solution:**
1. Verify you copied the complete key
2. Check for extra spaces before/after the key
3. Ensure format: `KEY=value` (no spaces around `=`)
4. Try regenerating the key

### SerpAPI Rate Limit
**Solution:**
- Wait until next month (auto-resets)
- Avoid repeated searches for the same query

### Google Cloud Billing Concerns
**Solution:**
- Set up billing alerts:
  1. Go to "Billing" → "Budgets & alerts"
  2. Set alert at $1
  3. Receive email notifications

### Can't Find .env.development
**Windows:**
- File Explorer → View → Check "Hidden items"

**Mac:**
- Finder → Press `Cmd + Shift + .`

---

## Additional Resources

- **SerpAPI Docs**: https://serpapi.com/docs
- **Google Vision Docs**: https://cloud.google.com/vision/docs
