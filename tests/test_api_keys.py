#!/usr/bin/env python3
"""
Diagnostic script to test Google Cloud Vision API and SerpAPI keys
"""

import base64
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.development')

GOOGLE_API_KEY = os.getenv('GOOGLE_CLOUD_API_KEY')
SERPAPI_KEY = os.getenv('SERPAPI_KEY')

print("=" * 80)
print("API KEY DIAGNOSTIC TEST")
print("=" * 80)
print()

# Test 1: Check if keys are loaded
print("TEST 1: Environment Variables")
print("-" * 80)
print(f"Google Cloud API Key: {'✓ Found' if GOOGLE_API_KEY else '✗ NOT FOUND'}")
if GOOGLE_API_KEY:
    print(f"  Key: {GOOGLE_API_KEY[:20]}...{GOOGLE_API_KEY[-10:]}")
print(f"SerpAPI Key: {'✓ Found' if SERPAPI_KEY else '✗ NOT FOUND'}")
if SERPAPI_KEY:
    print(f"  Key: {SERPAPI_KEY[:20]}...{SERPAPI_KEY[-10:]}")
print()

# Test 2: Google Cloud Vision API
print("TEST 2: Google Cloud Vision API")
print("-" * 80)

if not GOOGLE_API_KEY:
    print("✗ SKIPPED - No API key found")
else:
    try:
        # Create a simple test image (1x1 pixel PNG)
        # This is a base64 encoded 1x1 white PNG
        test_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="

        url = f'https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_API_KEY}'

        payload = {
            'requests': [{
                'image': {
                    'content': test_image
                },
                'features': [{
                    'type': 'TEXT_DETECTION',
                    'maxResults': 1
                }]
            }]
        }

        print(f"Sending request to: {url[:60]}...")
        response = requests.post(url, json=payload)
        result = response.json()

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✓ SUCCESS - API key is valid and working!")
            if 'responses' in result:
                print(f"  Response structure: Valid")
                if result['responses'] and 'textAnnotations' in result['responses'][0]:
                    print(f"  Text detection: Working")
                else:
                    print(f"  Text detection: No text found (expected for test image)")
        else:
            print("✗ FAILED - API request failed")
            if 'error' in result:
                error = result['error']
                print(f"  Error Code: {error.get('code', 'Unknown')}")
                print(f"  Error Message: {error.get('message', 'Unknown')}")
                print(f"  Error Status: {error.get('status', 'Unknown')}")

                # Provide specific guidance
                if 'API key expired' in error.get('message', ''):
                    print("\n  → SOLUTION: Your API key has expired. Create a new one:")
                    print("     https://console.cloud.google.com/apis/credentials")
                elif 'API key not valid' in error.get('message', ''):
                    print("\n  → SOLUTION: API key is invalid. Double-check the key:")
                    print("     https://console.cloud.google.com/apis/credentials")
                elif 'has not been used' in error.get('message', '') or 'disabled' in error.get('message', ''):
                    print("\n  → SOLUTION: Enable Cloud Vision API:")
                    print("     https://console.cloud.google.com/apis/library/vision.googleapis.com")
                elif 'billing' in error.get('message', '').lower():
                    print("\n  → SOLUTION: Enable billing for your project:")
                    print("     https://console.cloud.google.com/billing")

                print(f"\n  Full response:")
                print(f"  {result}")
            else:
                print(f"  Raw response: {result}")

    except Exception as e:
        print(f"✗ ERROR - Exception occurred: {e}")

print()

# Test 3: SerpAPI
print("TEST 3: SerpAPI")
print("-" * 80)

if not SERPAPI_KEY:
    print("✗ SKIPPED - No API key found")
else:
    try:
        url = "https://serpapi.com/account.json"
        params = {'api_key': SERPAPI_KEY}

        print(f"Checking account status...")
        response = requests.get(url, params=params)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✓ SUCCESS - API key is valid!")
            print(f"  Account Email: {data.get('account_email', 'N/A')}")
            print(f"  Plan: {data.get('plan_name', 'N/A')}")
            print(f"  Searches This Month: {data.get('this_month_usage', 0)}")
            print(f"  Total Searches: {data.get('total_searches_left', 'N/A')}")
        else:
            print("✗ FAILED - API key issue")
            try:
                error_data = response.json()
                print(f"  Error: {error_data}")
            except:
                print(f"  Response: {response.text}")

    except Exception as e:
        print(f"✗ ERROR - Exception occurred: {e}")

print()

# Test 4: Test with actual image if available
print("TEST 4: Real Image Test (if available)")
print("-" * 80)

test_images = list(Path('tests').glob('*.jpg')) + list(Path('tests').glob('*.png'))
if test_images and GOOGLE_API_KEY:
    test_image_path = test_images[0]
    print(f"Testing with: {test_image_path}")

    try:
        with open(test_image_path, 'rb') as image_file:
            image_content = image_file.read()

        base64_image = base64.b64encode(image_content).decode('utf-8')

        url = f'https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_API_KEY}'

        payload = {
            'requests': [{
                'image': {
                    'content': base64_image
                },
                'features': [{
                    'type': 'TEXT_DETECTION',
                    'maxResults': 1
                }]
            }]
        }

        response = requests.post(url, json=payload)
        result = response.json()

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            print("✓ SUCCESS - Real image processed!")
            if 'responses' in result and result['responses']:
                response_data = result['responses'][0]
                if 'textAnnotations' in response_data:
                    text = response_data['textAnnotations'][0]['description']
                    print(f"  Extracted text preview: {text[:100]}...")
                else:
                    print(f"  No text found in image")
        else:
            print("✗ FAILED")
            if 'error' in result:
                print(f"  Error: {result['error'].get('message', 'Unknown')}")

    except Exception as e:
        print(f"✗ ERROR: {e}")
else:
    if not test_images:
        print("No test images found in 'tests' directory")
    if not GOOGLE_API_KEY:
        print("No Google API key available")

print()
print("=" * 80)
print("DIAGNOSTIC COMPLETE")
print("=" * 80)
