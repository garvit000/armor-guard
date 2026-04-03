# Vercel entry-point
# Vercel looks for a variable named `app` in this file.
# We simply re-export the Flask app from the root app.py.

import sys
import os

# Make sure the project root is on the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app  # noqa: F401  – Vercel picks up this `app` object
