from flask import Flask, jsonify, request
import sys
import os
import traceback

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
# Attempt to add api/cnn_src to path so we can import code
sys.path.append(os.path.join(current_dir, 'cnn_src'))

try:
    # Try importing from cnn_src package style if possible, or direct module if path appended
    try:
        from cnn_src.cnn_scraper import CNN
    except ImportError:
        # Fallback if sys.path allows direct import
        from cnn_scraper import CNN

    app = Flask(__name__)
    cnn_controller = CNN()

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        # The Vercel Rewrite sends /cnn-detail/slug -> /api/detail.py
        # But Flask sees the PATH_INFO.
        # If we access /cnn-detail/teknologi/... 
        # Vercel might pass that full path or strip it?
        # Usually standard Vercel python behavior: request.path matches the rewrite source if not stripped?
        # Let's handle it dynamically.
        
        # Target: Recieve slug from Query Param (preferred) or Path
        clean_path = request.args.get('slug')
        
        # Fallback to path if query param missing
        if not clean_path:
            clean_path = path
            if clean_path.startswith('cnn-detail/'):
                clean_path = clean_path.replace('cnn-detail/', '', 1)
        
        # Reconstruct full URL
        target_url = f"https://www.cnnindonesia.com/{clean_path}"
        
        try:
            return jsonify(cnn_controller.detail(target_url))
        except Exception as e:
             return jsonify({
                "error": "Error scraping detail",
                "details": str(e),
                "target_url": target_url
            }), 500

except Exception as e:
    app = Flask(__name__)
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def error_handler(path):
        return jsonify({
            "error": "Startup Error in detail.py",
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500
