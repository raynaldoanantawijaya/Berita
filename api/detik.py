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
