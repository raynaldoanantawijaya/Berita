from flask import Flask, jsonify, request
import os

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def echo(path):
    return jsonify({
        "status": "alive",
        "message": "Echo Server Online",
        "path": path,
        "files_in_api": os.listdir(os.path.dirname(os.path.abspath(__file__))),
        "cwd": os.getcwd()
    })
