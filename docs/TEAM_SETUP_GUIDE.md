# Team Setup Guide - AI-Powered Inventory Locator
**Getting Started with Docker (GUI-Friendly Version)**

## What You'll Need

### Before You Start
1. **Docker Desktop** - Download and install
2. **GitHub Desktop** (recommended) - Makes Git easier
3. **A text editor** - VS Code
4. **API Keys** - You'll need to create your own (see Step 3 below)

---

## Step 1: Get Latest Code Changes

Since you already have the repository, you need to pull the latest changes:

### Using GitHub Desktop

1. **Open GitHub Desktop**
2. **Make sure you're on the main branch**
   - Look at the top - should say "Current Branch: main"
   - If not, click the branch dropdown and select "main"
3. **Fetch the latest changes**
   - Click "Fetch origin" button in the top right
4. **Pull the changes**
   - If there are updates, you'll see "Pull origin" button
   - Click it to download the latest code
5. **Done!** You now have the latest Docker setup

### Using Command Line (Alternative)

1. **Open Terminal/Command Prompt in your project folder**
   - **Mac:** Right-click folder → "New Terminal at Folder"
   - **Windows:** In File Explorer → Click address bar → Type `cmd` → Enter

2. **Run these commands:**
   ```bash
   git checkout main
   git pull origin main
   ```

---

## Step 2: Install Docker Desktop 

**Skip this if you already have Docker Desktop installed**

### Download Docker Desktop
1. Go to: https://www.docker.com/products/docker-desktop
2. Click "Download for Mac" or "Download for Windows"
3. Install the downloaded file (just like any other app)
4. **Open Docker Desktop** - You should see a whale icon in your menu bar (Mac) or system tray (Windows)
5. Wait for Docker to say "Docker Desktop is running"

**Note:** Keep Docker Desktop running whenever you're working on the project!

---

## Step 3: Get Your API Keys

You need to create your own API keys for SerpAPI and Google Cloud Vision.

### Follow the API Key Setup Guide

**See the detailed guide:** [docs/API_KEY_SETUP.md](API_KEY_SETUP.md)

This guide walks you through:
1. Creating a SerpAPI account and getting your key
2. Setting up Google Cloud Vision API and getting your key
3. Adding both keys to your `.env.development` file

**Quick summary:**
1. **SerpAPI**: Sign up at https://serpapi.com/ (100 free searches/month)
2. **Google Cloud Vision**: Create project at https://console.cloud.google.com/ (1,000 free requests/month)
3. Add both keys to `.env.development` file in your project folder

**Important:** Keep your API keys private! Don't share them publicly or commit them to GitHub.

---

## Step 4: Start the Application

### Using Docker Desktop GUI

1. **Open Docker Desktop** (if not already running)

2. **Open a Terminal/Command Prompt in the project folder:**

   **On Mac:**
   - Open **Finder** → Navigate to the project folder
   - Right-click the folder → "New Terminal at Folder"
   - OR: Open Terminal → Type `cd ` (with a space) → Drag the project folder into Terminal → Press Enter

   **On Windows:**
   - Open **File Explorer** → Navigate to the project folder
   - Click in the address bar at the top
   - Type `cmd` and press Enter
   - OR: Right-click inside the folder → "Open in Terminal" (Windows 11)

3. **Start the application:**

   **Mac/Linux:**
   ```bash
   ./scripts/run_local.sh
   ```

   **Windows:**
   ```bash
   docker-compose up --build
   ```

4. **Wait for it to start** (2-3 minutes first time)
   - You'll see lots of text scrolling
   - Look for: `Running on http://0.0.0.0:5000`
   - Keep this window open!

5. **View in Docker Desktop:**
   - Click "Containers" on the left sidebar
   - You should see `ai-project-dev` with a green icon (running)

---

## Step 5: Test It Works

### Open the Application

1. **Open your web browser**
2. Go to: **http://localhost:5000**
3. You should see the AI-Powered Inventory Locator interface!

### Quick Test

1. **Click "Choose File"** and upload any product image
2. Click "Upload & Extract Text"
3. Wait a few seconds for the OCR to process
4. Click "Search for Products"
5. View the results!

**If you can upload an image and see search results, everything is working!**

---

## Daily Workflow

### Starting Your Work Session

1. **Make sure Docker Desktop is running** (check for whale icon)
2. **Open Terminal in the project folder**
3. **Start the container:**
   - Mac: `./scripts/run_local.sh`
   - Windows: `docker-compose up`
4. **Open browser to http://localhost:5000**

### Making Code Changes

1. **Edit files** in your normal editor (VS Code, etc.)
2. **Save the file** (Ctrl+S / Cmd+S)
3. **Check the Terminal** - You'll see "Restarting with stat"
4. **Refresh your browser** (F5 or Cmd+R)
5. **See your changes!**

**No rebuild needed!** Changes appear automatically.

### Stopping Your Work Session

**Option 1: Using Terminal**
- Go to the Terminal window where the app is running
- Press **Ctrl+C** (Windows/Mac/Linux)

**Option 2: Using Docker Desktop GUI**
- Open Docker Desktop
- Click "Containers" on the left
- Find `ai-project-dev`
- Click the **Stop** button (square icon)

---

## Troubleshooting

### Docker Desktop Not Running
**Problem:** "Cannot connect to Docker daemon"

**Solution:**
1. Open Docker Desktop application
2. Wait for it to say "Docker Desktop is running"
3. Try starting the container again

---

### Port Already in Use
**Problem:** "Port 5000 is already allocated"

**Solution:**
1. Open Docker Desktop
2. Click "Containers" → Stop all running containers
3. Try again

**OR on Mac/Linux:**
```bash
# Find what's using port 5000
lsof -i :5000

# Kill it (replace <PID> with the number shown)
kill -9 <PID>
```

---

### Can't See Hidden Files (.env.development)
**Windows:**
1. Open File Explorer
2. Click "View" at the top
3. Check "Hidden items"

**Mac:**
1. In Finder, press **Cmd + Shift + .** (period)
2. Hidden files now appear grayed out

---

### API Keys Not Working
**Problem:** Seeing "API key not configured" warnings

**Solution:**
1. Open `.env.development` file
2. Make sure the keys are there (no spaces around the `=` sign)
3. Save the file
4. Stop and restart the Docker container

**Format should look exactly like:**
```
SERPAPI_KEY=dd8ea6c63be1360a9345adc8f09804cbe94af17abc6ed1a876eb973ae57f5477
GOOGLE_CLOUD_API_KEY=AIzaSyA4lD7GUk2rzgFwS3sDI_1liYdirkJntAI
```

---

### Changes Not Showing Up
**Solution:**
1. Check Terminal - did Flask restart? (look for "Restarting with stat")
2. Hard refresh browser: **Ctrl+Shift+R** (Windows) or **Cmd+Shift+R** (Mac)
3. If still not working, stop and restart the container

---

### Container Won't Start
**Solution 1:** View logs in Docker Desktop
1. Open Docker Desktop
2. Click "Containers"
3. Click on `ai-project-dev`
4. Look at the logs - what's the error?

**Solution 2:** Start fresh
1. Open Docker Desktop
2. Go to "Containers"
3. Delete `ai-project-dev` if it exists
4. Try starting again with `docker-compose up --build`

---

## Understanding the Project Structure

You don't need to understand all this, but it helps to know what's what:

```
AI-Project/
├── ui/                     # Web interface (HTML, CSS, JavaScript)
│   ├── app.py             # Main Flask application
│   ├── templates/         # HTML pages
│   └── static/            # CSS, JavaScript, images
├── backend/               # Server-side logic
│   ├── api/              # SerpAPI integration
│   └── config.py         # Configuration
├── models/                # AI/ML code
│   └── ocr_processor.py  # Google Cloud Vision integration
├── tests/                 # Test files and test images
├── .env.development       # Your API keys (keep private!)
├── docker-compose.yml     # Docker configuration
├── Dockerfile             # Docker build instructions
└── requirements.txt       # Python dependencies
```

**Files you'll edit most often:**
- `ui/app.py` - Main application logic
- `ui/templates/*.html` - Web pages
- `ui/static/css/*.css` - Styling
- `models/ocr_processor.py` - OCR/image processing

---

## Quick Reference Card

### Starting the App
```
Mac:     ./scripts/run_local.sh
Windows: docker-compose up
```

### Stopping the App
- Press **Ctrl+C** in Terminal
- OR use Docker Desktop GUI

### Viewing the App
- Open browser: **http://localhost:5000**

### Checking if Docker is Running
- Look for whale icon in menu bar/system tray
- Should say "Docker Desktop is running"

### Getting Updates from Team
1. Open GitHub Desktop
2. Click "Fetch origin"
3. Click "Pull origin"
4. Restart Docker container

---


1. **Keep Docker Desktop open** while working - it needs to be running for containers to work
2. **Don't delete the container** in Docker Desktop - just stop/start it
3. **First build can take 2-3 minutes** - subsequent builds are much faster
4. **Use Docker Desktop Dashboard** - Great way to see what's running and view logs visually
5. **Hard refresh often** - Browser caching can hide your changes (Ctrl+Shift+R / Cmd+Shift+R)

---

## Working with the Team

### Sharing Your Changes
1. **Make your changes** and test them
2. **Open GitHub Desktop**
3. Write a summary of what you changed
4. Click "Commit to main"
5. Click "Push origin"

### Getting Team Changes
1. **Open GitHub Desktop**
2. Click "Fetch origin" (top right)
3. If there are changes, click "Pull origin"
4. Restart your Docker container to see the changes

### Important Rules
- Always test before pushing - Make sure it works!
- Pull before you start working - Get latest changes
- Never commit `.env.development` - Contains your API keys!
- Don't commit random files - Only commit code you changed

---
