# IMPORTS MOVED INSIDE TRY BLOCK TO CATCH ERRORS
import sys
import os
import traceback

app = None
INIT_ERROR = None
DN_API = None
base_dir = os.path.dirname(os.path.abspath(__file__))

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS

    app = Flask(__name__)
    CORS(app)
DN_API = None
base_dir = os.path.dirname(os.path.abspath(__file__))

try:
    # 1. Setup Path to include 'detik_src'
    src_path = os.path.join(base_dir, 'detik_src')
    if src_path not in sys.path:
        sys.path.append(src_path)

    # 2. Try Import
    # Assuming 'detik_src' package has 'scraper.py' inside or __init__ exposes DetikScraper
    # Based on previous checks, it likely has scraper.py
    try:
        from detik_src.detik_scraper import DetikScraper
    except ImportError:
         try:
             # Fallback: maybe it's directly in detik_src namespace
             from detik_src import DetikScraper
         except ImportError:
             # Fallback: flat file import
             from detik_scraper import DetikScraper

    # 3. Instantiate
    DN_API = DetikScraper()

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
        # 2. Extract Slug from Query Param (Vercel rewrite) or Path
        # Vercel rewrite: /detik-detail/slug -> /api/detik?slug=slug
        slug = request.args.get('slug')
        
        if not slug:
            # Fallback for direct calls: try parsing path
            # If path is "/detail/..." or just "slug..."
            slug = path
            if slug.startswith('search'): # Handle search collision if any
                 query = request.args.get("q")
                 return jsonify(DN_API.search(query)) if query else jsonify([])

        if not slug:
             # Check if it is a search request hitting the wrong handler?
             if request.args.get("q"):
                  return jsonify(DN_API.search(request.args.get("q")))
                  
             return jsonify({
                 "error": "Missing Slug",
                 "debug": {
                     "path": path, 
                     "args": request.args,
                     "url": request.url
                 }
             }), 400

        # 3. Call Scraper (Detail)
        # Detik slug is usually a full URL part, e.g. "jabar/d-71234/judul"
        # We need to construct full URL.
        # Check if slug already has domain
        target_url = slug
        if not target_url.startswith('http'):
            # Basic reconstruction, might need adjustment for subdomains
            # But usually the scraper might handle relative paths OR we rely on Gateway sending full URL in slug?
            # Let's assume slug is the path part.
            target_url = f"https://news.detik.com/{slug}"
            # WARNING: Detik has many subdomains (finance, inet). 
            # If slug contains "finance/...", headers might redirect or 404 on news.detik.com
            # IMPROVEMENT: If slug starts with 'http', use it.
        
        # Handling the "https:/" issue from Vercel path splitting
        if target_url.startswith('https:/') and not target_url.startswith('https://'):
            target_url = target_url.replace('https:/', 'https://', 1)

        return jsonify(DN_API.get_article_content(target_url))

    except Exception as e:
        return jsonify({
            "error": "Runtime Error during Scraping",
            "message": str(e),
            "traceback": traceback.format_exc()
        }), 500

# Explicit Search Route (if Vercel routes specific /api/detik/search)
# But our current vercel.json rewrites /detik-detail to this file. 
# Search likely goes to /api/gateway -> /api/search?
