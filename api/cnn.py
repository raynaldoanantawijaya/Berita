import sys
import os

# Add the subdirectory to sys.path so we can import from it
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(os.path.join(parent_dir, 'cnnindonesia-news-api'))

from main import app as application

# Vercel expects 'app' but we can just expose the handler
app = application
