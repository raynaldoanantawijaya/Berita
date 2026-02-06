import sys
import os

try:
    # Add the subdirectory to sys.path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    sys.path.append(os.path.join(parent_dir, 'detiknews_api'))

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
            "sys_path": sys.path
        }), 500
