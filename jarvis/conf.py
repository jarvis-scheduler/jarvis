import os

BASE_DIR = os.path.dirname(__file__)

TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates/')

STATIC_URL = '/static/'

STATIC_FILES_DIR = os.path.join(BASE_DIR, 'static/')

PORT = int(os.environ.get('JARVIS_PORT', 8080))

BUILD_PATH = os.path.join(STATIC_FILES_DIR, 'build/js/')

JSX_PATHS = [
    ('jsx/jarvis.jsx', 'build/js/jarvis.js'),
]

DEBUG = os.environ.get('APP_DEBUG', 'True') == 'True'
