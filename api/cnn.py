import sys
import os

try:
    # Add the subdirectory to sys.path so we can import from it
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(os.path.join(parent_dir, 'cnnindonesia-news-api'))

    from main import app as application
    app = application
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
            "sys_path": sys.path,
            "contents_of_cwd": os.listdir(os.getcwd()) if os.path.exists(os.getcwd()) else "cwd not found"
        }), 500
