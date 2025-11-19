# SerpAPI Setup & Integration Guide

This guide walks you through how to set up and use the **SerpAPI** integration in our AI project.  
You’ll register for an API key, store it securely, and test the API connection in your local environment.

---

## 1 Register for a SerpAPI Account & Get an API Key

1. Go to [https://serpapi.com/](https://serpapi.com/).
2. Click **Sign Up** (top right).
3. Create an account using your email or GitHub/Google account.
4. Once logged in, navigate to your [Dashboard → API Key](https://serpapi.com/manage-api-key).
5. Copy your **API key** — this is what authenticates you to use SerpAPI.

---

## 2 Store Your API Key Securely in a `.env` File

We use a `.env` file to store secrets such as your API key. This prevents it from being accidentally uploaded to GitHub.

1. In the **root** of the project (same level as `README.md`), create a file named:

.env

2. Add the following line inside:

SERPAPI_KEY=your_actual_api_key_here


3. Save and close the file.

4. **Important:** Verify that your `.env` file is *ignored by Git* so it never gets committed.

Check that `.gitignore` includes the following line (add it if missing):

.env


---

## 3 Activate the Virtual Environment

Before running the code, make sure you are inside the project’s Python virtual environment.

If you see a folder named `.venv` in the repo, activate it like this:

### macOS / Linux:

source .venv/bin/activate

### Windows (PowerShell):

.venv\Scripts\Activate

If you don’t have it yet, create one:

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

## 4 Run the SerpAPI Test Script

Now you’re ready to verify that everything works.

1. Inside your terminal, from the project root, run:

python -m backend.main

2. You’ll be prompted to enter a product name (e.g., coffee maker) and optionally a location (e.g., Fayetteville, Arkansas, United States).

3. You should see product titles, prices, and store names returned in the console.

## 5 Where the Code Lives

File -----> Purpose

backend/api/serpapi_client.py   ----->    Handles all API requests to SerpAPI
backend/config.py               ----->    Loads API keys from the .env file
backend/main.py                 ----->    Simple entry point for testing SerpAPI functionality
.env                            ----->    Stores your personal API key (not shared in GitHub)
.gitignore                      ----->    Ensures .env and other sensitive files are not committed