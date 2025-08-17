import os
import sys
from pathlib import Path

# [CORREÇÃO] - MOVER ESTA PARTE PARA O TOPO ABSOLUTO!
# --------------------------------------------------
# Adiciona o diretório src ao PATH (deve ser a PRIMEIRA coisa após os imports básicos)
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
# --------------------------------------------------

# [ATENÇÃO] - Agora os imports do Flask devem vir DEPOIS da configuração do path
from flask import Flask, send_from_directory
from models.user import db  # Removido "src." pois agora o diretório está no path
from routes.user import user_bp
from routes.opme import opme_bp
from routes.maino import maino_bp

# Cria o caminho absoluto para o diretório atual
current_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, 
            static_folder=os.path.join(current_dir, 'static'),
            static_url_path='/')

# [SUGESTÃO] Remover esta linha se não tiver config.py
# app.config.from_pyfile('../config.py')

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback_secret')

# Registra blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(opme_bp, url_prefix='/api')
app.register_blueprint(maino_bp, url_prefix='/api')

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f"sqlite:///{os.path.join(current_dir, 'app.db')}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Cria o banco se não existir
with app.app_context():
    db.create_all()

# Rotas para SPA (Single Page Application)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder = app.static_folder
    if path and os.path.exists(os.path.join(static_folder, path)):
        return send_from_directory(static_folder, path)
    return send_from_directory(static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)