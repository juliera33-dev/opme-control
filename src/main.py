import os
import sys
from pathlib import Path
from flask import Flask, send_from_directory, jsonify

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
            static_url_path='/')

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback_secret')

# Configuração do banco de dados
def get_database_uri():
    db_url = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')
    
    if db_url:
        if db_url.startswith("postgres://"):
            return db_url.replace("postgres://", "postgresql://", 1)
        return db_url
    else:
        db_dir = BASE_DIR / 'database'
        db_dir.mkdir(exist_ok=True)
        return f"sqlite:///{db_dir / 'app.db'}"

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

# Rota de teste
@app.route('/api/test')
def test():
    return jsonify({"message": "Teste bem sucedido!"}), 200

# Rotas para SPA com logs detalhados
@app.route('/')
def index():
    static_folder = app.static_folder
    index_path = os.path.join(static_folder, 'index.html')
    
    print(f"\n[ROTA RAIZ] Static folder: {static_folder}")
    print(f"[ROTA RAIZ] Caminho do index: {index_path}")
    print(f"[ROTA RAIZ] Arquivo existe? {os.path.exists(index_path)}")
    
    if os.path.exists(index_path):
        return send_from_directory(static_folder, 'index.html')
    
    return "Arquivo index.html não encontrado na pasta static!", 404

@app.route('/<path:path>')
def serve(path):
    static_folder = app.static_folder
    full_path = os.path.join(static_folder, path)
    
    print(f"\n[ROTA DINÂMICA] Path: {path}")
    print(f"[ROTA DINÂMICA] Full path: {full_path}")
    print(f"[ROTA DINÂMICA] Existe? {os.path.exists(full_path)}")
    
    if os.path.exists(full_path) and os.path.isfile(full_path):
        return send_from_directory(static_folder, path)
    
    return send_from_directory(static_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)