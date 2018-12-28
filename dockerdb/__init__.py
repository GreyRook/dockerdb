__version__ = '0.3.0'
import os

from .service import Service, HTTPServer


inside_docker = os.path.exists('/.dockerenv')