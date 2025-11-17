"""
pytest configuration file for QFS V13 test suite.
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'libs'))

# pytest fixtures can be defined here