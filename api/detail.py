from flask import Flask, jsonify, request
import os
import sys
import traceback

# INITIALIZATION WRAPPER
# We wrap everything in a try-catch to ensure the function ALWAYS starts,
# returning the error as JSON instead of crashing (which causes Vercel 404/500Opaque).

app = Flask(__name__)

INIT_ERROR = None
cnn_controller = None
base_dir = os.path.dirname(os.path.abspath(__file__))

try:
    # 1. Setup Path to include 'cnn_src'
    src_path = os.path.join(base_dir, 'cnn_src')
    if src_path not in sys.path:
        sys.path.append(src_path)

    # 2. Try Import
    # Note: 'cnn_scraper' is the renamed file (was code.py)
    try:
        from cnn_src.cnn_scraper import CNN
    except ImportError:
        # Fallback if path appending made it a top-level module
        from cnn_scraper import CNN

    # 3. Instantiate
    cnn_controller = CNN()

except Exception as e:
    # Capture ANY startup error
    INIT_ERROR = {
        "status": "Startup Failed",
        "error_type": type(e).__name__,
        "message": str(e),
        "traceback": traceback.format_exc(),
        "debug_info": {
            "cwd": os.getcwd(),
            "base_dir": base_dir,
            "src_path": src_path,
            "src_exists": os.path.exists(src_path),
            "src_files": os.listdir(src_path) if os.path.exists(src_path) else [],
            "sys_path": sys.path
        }
    }

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def detail_handler(path):
    # 1. Return Startup Error if exists
    if INIT_ERROR:
        return jsonify(INIT_ERROR), 500

    try:
        # 2. Extract Slug
        # Vercel rewrite: /cnn-detail/slug -> /api/detail?slug=slug
        slug = request.args.get('slug')
        
        if not slug:
            # Fallback: try to parsing path if query param missing
            slug = path
            if slug.startswith('cnn-detail/'):
                slug = slug.replace('cnn-detail/', '', 1)

        if not slug:
             return jsonify({
                 "error": "Missing Slug",
                 "debug": {
                     "path": path, 
                     "args": request.args,
                     "url": request.url
                 }
             }), 400

        # 3. Call Scraper
        # Reconstruct full URL if needed, depending on what user passed
        # The slug from gateway usually includes the full path: "teknologi/..."
        target_url = f"https://www.cnnindonesia.com/{slug}"
        
        result = cnn_controller.detail(target_url)
        return jsonify(result)

    except Exception as e:
        return jsonify({
            "error": "Runtime Error during Scraping",
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500
