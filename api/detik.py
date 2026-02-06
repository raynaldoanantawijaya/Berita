import sys
import os

try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(current_dir, 'detik_src'))

    from flask import Flask, request, jsonify
    from flask_cors import CORS
    from detik_src import DetikScraper # Assuming __init__.py allows this or direct file import

    # Initialize App
    app = Flask(__name__)
    CORS(app)
    DN_API = DetikScraper()

    # --- Vercel Middleware: Strip Prefix ---
    class PrefixMiddleware(object):
        def __init__(self, app, prefix=''):
            self.app = app
            self.prefix = prefix
        def __call__(self, environ, start_response):
            if environ['PATH_INFO'].startswith(self.prefix):
                environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
                environ['SCRIPT_NAME'] = self.prefix
                return self.app(environ, start_response)
            else:
                return self.app(environ, start_response)

    app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix='/detik')
    # ---------------------------------------

    # Direct Detail Route (Bypassing Gateway)
    # Rewrite: /detik-detail/path/to/news -> /api/detik.py -> /detail/path/to/news
    # We need to reconstruct the full URL from the slug
    @app.route("/detail/<path:slug>", methods=["GET"])
    def detail_direct(slug):
        # Detik slug is usually part of the URL.
        # e.g. /jabar/d-71234/judul-berita
        # Full URL: https://news.detik.com/jabar/d-71234/judul-berita
        # BUT Detik has many subdomains (finance, inet, etc). 
        # The slug passed by client might be: "jabar/d-71234/judul"
        # The gateway search results usually have `link`.
        # If client passes the FULL URL in slug (url encoded?), we can use it.
        # But Vercel rewrites usually match path.
        # Re-reading gateway logic: req.url = `/detail${req.url}`. 
        # So client calls /cnn-detail/teknologi/... -> cnn.py receives /detail/teknologi...
        
        # For Detik, we need the full URL to scrape.
        # Let's try to deduce it or assume the input is sufficient?
        # DetikScraper.get_article_content(url) needs a full URL?
        # Let's check `code.py` in detik_src if possible, but let's just Try.
        
        # HACK: If slug doesn't start with http, assume it's a path on news.detik.com?
        # Or better, accept 'url' param if possible?
        # But this is a Rewrite rule /detik-detail/:path*
        
        # Ideally client sends: /detik-detail/https://news.detik.com/...
        # Then slug is "https://news.detik.com/..."
        # If slug starts with 'https:/', fix it (flask might merge slashes)
        
        target_url = slug
        if not target_url.startswith('http'):
             # Try to fix "https:/www..." issues common in path params
             if target_url.startswith('https:/'):
                 target_url = target_url.replace('https:/', 'https://', 1)
             else:
                 # Default to generic detik id?
                 pass 
        
        return jsonify(DN_API.get_article_content(target_url))

    @app.route("/search", methods=["GET"])
    def search():
        query = request.args.get("q")
        if not query:
            return jsonify({"status": 400, "message": "Query parameter 'q' is required"}), 400
        return jsonify(DN_API.search(query))

    @app.route("/detail", methods=["GET"])
    def detail():
        url = request.args.get("url")
        if not url:
            return jsonify({"status": 400, "message": "Query parameter 'url' is required"}), 400
        return jsonify(DN_API.get_article_content(url))

except Exception as e:
    from flask import Flask, jsonify
    import traceback
    app = Flask(__name__)
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return jsonify({
            "error_type": "Startup Error",
            "message": str(e),
            "traceback": traceback.format_exc(),
            "cwd": os.getcwd()
        }), 500
