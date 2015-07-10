import os

BASE_DIR = os.path.dirname(__file__)

TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates/')

STATIC_URL = '/static/'

STATIC_FILES_DIR = os.path.join(BASE_DIR, 'static/')

PORT = os.environ.get('JARVIS_PORT', 8080)

JSX_PATHS = [
    ('jsx/jarvis.jsx', 'build/js/jarvis.js'),
]
