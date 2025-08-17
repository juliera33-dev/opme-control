import os

# Configurações básicas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Configurações específicas para produção
if os.environ.get('FLASK_ENV') == 'production':
    PREFERRED_URL_SCHEME = 'https'