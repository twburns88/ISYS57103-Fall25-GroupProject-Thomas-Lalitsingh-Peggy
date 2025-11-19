"""
Flask web application for AI-Powered Inventory Locator System
Allows users to upload product images, search for products, and find nearby availability
"""

from flask import Flask, render_template, request, jsonify, session
import os
import sys
from pathlib import Path
from werkzeug.utils import secure_filename
import uuid
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.ocr_processor import extract_text_from_image
from backend.api.serpapi_client import get_product_results, get_product_locations
from backend.config import SERPAPI_KEY

app = Flask(__name__)

# Configuration from environment variables
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# File upload configuration
UPLOAD_FOLDER = Path(os.getenv('UPLOAD_FOLDER', 'ui/uploads'))
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_FILE_SIZE = int(os.getenv('MAX_UPLOAD_SIZE', 10 * 1024 * 1024))  # Default 10MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload folder if it doesn't exist
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)

# Get API keys from environment
GOOGLE_VISION_API_KEY = os.getenv('GOOGLE_CLOUD_API_KEY')
USER_LOCATION = os.getenv('USER_LOCATION', 'Fayetteville, Arkansas, United States')


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """Home page with image upload form"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_image():
    """
    Handle image upload and OCR processing
    Returns extracted text and initiates product search
    """

    # Check if file is present
    if 'image' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['image']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'}), 400

    try:
        # Save uploaded file with unique name
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = app.config['UPLOAD_FOLDER'] / unique_filename
        file.save(filepath)

        # Check if Google Vision API key is available
        if not GOOGLE_VISION_API_KEY:
            return jsonify({
                'error': 'Google Vision API key not configured. Please set GOOGLE_CLOUD_API_KEY environment variable.'
            }), 500

        # Extract text from image using OCR
        ocr_result = extract_text_from_image(str(filepath), GOOGLE_VISION_API_KEY)

        if not ocr_result['success']:
            # Clean up uploaded file
            filepath.unlink(missing_ok=True)
            return jsonify({'error': f"OCR failed: {ocr_result['error']}"}), 500

        extracted_text = ocr_result['text'].strip()

        if not extracted_text:
            filepath.unlink(missing_ok=True)
            return jsonify({'error': 'No text detected in image. Please try a clearer image.'}), 400

        # Store filepath in session for later cleanup
        session['last_upload'] = str(filepath)

        return jsonify({
            'success': True,
            'extracted_text': extracted_text,
            'message': 'Text extracted successfully'
        })

    except Exception as e:
        # Clean up on error
        if 'filepath' in locals() and filepath.exists():
            filepath.unlink(missing_ok=True)
        return jsonify({'error': f'Error processing image: {str(e)}'}), 500


@app.route('/search', methods=['POST'])
def search_products():
    """
    Search for products based on extracted text or manual query
    Returns list of product options for user confirmation
    """

    data = request.get_json()
    query = data.get('query', '').strip()

    if not query:
        return jsonify({'error': 'Search query is required'}), 400

    try:
        # Search for products using SerpAPI
        results = get_product_results(query=query, user_location=USER_LOCATION)

        if not results or 'shopping_results' not in results:
            return jsonify({
                'error': 'No products found. Please try a different search term.'
            }), 404

        shopping_results = results['shopping_results']

        # Format results for frontend (return top 5)
        products = []
        for product in shopping_results[:5]:
            products.append({
                'title': product.get('title', 'Unknown Product'),
                'price': product.get('price', 'N/A'),
                'source': product.get('source', 'Unknown'),
                'thumbnail': product.get('thumbnail', ''),
                'rating': product.get('rating'),
                'reviews': product.get('reviews'),
                'page_token': product.get('immersive_product_page_token', ''),
                'product_id': product.get('product_id', ''),
            })

        return jsonify({
            'success': True,
            'products': products,
            'count': len(products)
        })

    except Exception as e:
        return jsonify({'error': f'Search failed: {str(e)}'}), 500


@app.route('/product/<path:page_token>', methods=['GET'])
def get_product_details(page_token):
    """
    Get detailed product information including store locations
    Uses the immersive product page token from search results
    """

    try:
        # Get detailed product data
        location_data = get_product_locations(page_token)

        if 'error' in location_data:
            return jsonify({'error': location_data['error']}), 500

        # Parse product results
        if 'product_results' not in location_data:
            return jsonify({'error': 'No product data found'}), 404

        product_results = location_data['product_results']

        # Extract store information
        stores_data = product_results.get('stores', [])
        nearby_stores = []
        online_stores = []

        for store in stores_data:
            store_info = {
                'name': store.get('name', 'Unknown Store'),
                'price': store.get('price', 'N/A'),
                'extracted_price': store.get('extracted_price'),
                'link': store.get('link', ''),
                'rating': store.get('rating'),
                'reviews': store.get('reviews'),
                'logo': store.get('logo', ''),
                'details': store.get('details_and_offers', []),
                'tag': store.get('tag', ''),
                'shipping': store.get('shipping', ''),
                'total': store.get('total', store.get('price', 'N/A'))
            }

            # Check if available nearby
            is_nearby = False
            for detail in store.get('details_and_offers', []):
                if 'nearby' in detail.lower():
                    is_nearby = True
                    break

            if is_nearby or store.get('tag', '').lower() == 'nearby':
                nearby_stores.append(store_info)
            else:
                online_stores.append(store_info)

        # Product information
        product_info = {
            'title': product_results.get('title', 'Unknown Product'),
            'brand': product_results.get('brand', ''),
            'rating': product_results.get('rating'),
            'reviews': product_results.get('reviews'),
            'price_range': product_results.get('price_range', ''),
            'thumbnails': product_results.get('thumbnails', [])[:5],  # Limit to 5 images
        }

        return jsonify({
            'success': True,
            'product': product_info,
            'nearby_stores': nearby_stores,
            'online_stores': online_stores,
            'total_stores': len(stores_data)
        })

    except Exception as e:
        return jsonify({'error': f'Failed to get product details: {str(e)}'}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'google_vision_configured': GOOGLE_VISION_API_KEY is not None,
        'serpapi_configured': SERPAPI_KEY is not None
    })


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({'error': 'File too large. Maximum size is 10MB.'}), 413


if __name__ == '__main__':
    # Validate configuration
    if not GOOGLE_VISION_API_KEY:
        print("WARNING: GOOGLE_CLOUD_API_KEY environment variable not set")
    if not SERPAPI_KEY:
        print("WARNING: SERPAPI_KEY environment variable not set")

    # Production safety check
    if FLASK_ENV == 'production' and app.secret_key == 'dev-secret-key-change-in-production':
        raise ValueError(
            "CRITICAL: Cannot run in production with default secret key! "
            "Please set FLASK_SECRET_KEY environment variable to a secure random string."
        )

    print(f"Environment: {FLASK_ENV}")
    print(f"Debug mode: {FLASK_DEBUG}")
    print(f"User location: {USER_LOCATION}")
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print("Starting Flask server...")

    app.run(debug=FLASK_DEBUG, host='0.0.0.0', port=5000)
