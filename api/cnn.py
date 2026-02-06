import sys
import os

try:
    # Add the local source directory to sys.path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(current_dir, 'cnn_src'))

    from cnn_src import cnn # Import module directly if needed or rely on main
    # Actually, main.py is not in cnn_src, it was in root of cnnindonesia-news-api.
    # I need to create a main.py shim or import cnn.py directly.
    # Let's assume I copied 'src' folder. The 'main.py' logic needs to be here.
    
    from flask import Flask, jsonify, request
    from flask_cors import CORS
    
    # Re-implement main.py logic here since it's short
    app = Flask(__name__)
    CORS(app)

    # --- Vercel Middleware: Strip Prefix ---
    # We now handle both /cnn-api (default) and /cnn-detail (direct access)
    class PrefixMiddleware(object):
        def __init__(self, app, prefix=''):
            self.app = app
            self.prefix = prefix
        def __call__(self, environ, start_response):
            path = environ['PATH_INFO']
            # If accessing via /cnn-detail, we don't strip passing to app, 
            # but we need to ensure app route matches.
            # actually app.route('/detail/<path:slug>') matches /detail/...
            # so if path is /cnn-detail/teknologi... we want it to become /detail/teknologi...
            
            if path.startswith('/cnn-api'):
                environ['PATH_INFO'] = path[len('/cnn-api'):]
                environ['SCRIPT_NAME'] = '/cnn-api'
            elif path.startswith('/cnn-detail'):
                # Map /cnn-detail/slug -> /detail/slug
                environ['PATH_INFO'] = path.replace('/cnn-detail', '/detail', 1)
                environ['SCRIPT_NAME'] = '/cnn-detail'
            
            return self.app(environ, start_response)

    app.wsgi_app = PrefixMiddleware(app.wsgi_app) # No fixed prefix, logic inside
    # ---------------------------------------

    # Import Controller logic from src
    from cnn_src import cnn as cnn_controller

    @app.route('/')
    def home():
        return cnn_controller.index()

    @app.route('/<path:path>', methods=['GET'])
    def proxy(path):
        # Allow dynamic calling of methods in cnn_controller if they match
        # But for robustness, let's map explicit routes as per original main.py?
        #Original main.py was a bit dynamic. Let's make it simpler.
        
        # If path is 'teknologi', call cnn.news('teknologi')?
        # Let's look at original main.py logic.
        pass
        
    # Re-implementing routes manually based on cnn_src structure
    @app.route('/nasional')
    def nasional(): return cnn_controller.news('nasional')
    @app.route('/internasional')
    def internasional(): return cnn_controller.news('internasional')
    @app.route('/ekonomi')
    def ekonomi(): return cnn_controller.news('ekonomi')
    @app.route('/olahraga')
    def olahraga(): return cnn_controller.news('olahraga')
    @app.route('/teknologi')
    def teknologi(): return cnn_controller.news('teknologi')
    @app.route('/hiburan')
    def hiburan(): return cnn_controller.news('hiburan')
    @app.route('/gaya-hidup')
    def gaya_hidup(): return cnn_controller.news('gaya-hidup')
    
    @app.route('/search/')
    def search():
        q = request.args.get('q')
        return cnn_controller.search(q)

    @app.route('/detail/<path:slug>')
    def detail(slug):
        # slug might include date/segments
        return cnn_controller.detail(f"https://www.cnnindonesia.com/{slug}")

    @app.route('/debug')
    def debug_view():
        return jsonify({
            "path": request.path,
            "url": request.url,
            "headers": dict(request.headers),
            "sys_path": sys.path
        })

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
            "cwd": os.getcwd(),
            "contents": os.listdir(os.getcwd())
        }), 500
