import os
import sys
from pathlib import Path
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

# Configura caminhos absolutos
BASE_DIR = Path(__file__).resolve().parent.parent
SRC_DIR = Path(__file__).resolve().parent

# Adiciona diretórios ao PATH
sys.path.insert(0, str(SRC_DIR))
sys.path.insert(0, str(BASE_DIR))

# Correção para Windows
if sys.platform.startswith('win'):
    static_path = BASE_DIR / 'static'
    if not static_path.exists():
        static_path.mkdir(exist_ok=True)
        print(f"Criada pasta static em: {static_path}")

app = Flask(__name__, 
            static_folder=str(BASE_DIR / 'static'),
            static_url_path='')

# Habilita CORS para todas as rotas
CORS(app)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback_secret')
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB

# Configuração do banco de dados
def get_database_uri():
    db_url = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')
    
    if db_url:
        print(f"Usando banco PostgreSQL: {db_url[:50]}...")  # Log parcial
        if db_url.startswith("postgres://"):
            return db_url.replace("postgres://", "postgresql://", 1)
        return db_url
    else:
        db_dir = BASE_DIR / 'database'
        db_dir.mkdir(exist_ok=True)
        db_path = f"sqlite:///{db_dir / 'app.db'}"
        print(f"Usando banco SQLite: {db_path}")
        return db_path

app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Importações DEPOIS da configuração do app
from models.user import db
from routes.user import user_bp
from routes.opme import opme_bp
from routes.maino import maino_bp

# Registra blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(opme_bp, url_prefix='/api')
app.register_blueprint(maino_bp, url_prefix='/api')

# Inicializa o banco de dados
db.init_app(app)
with app.app_context():
    db.create_all()
    print("Tabelas do banco de dados criadas com sucesso!")

# Rotas para SPA
@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/<path:path>')
def serve(path):
    return send_from_directory(app.static_folder, path)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)