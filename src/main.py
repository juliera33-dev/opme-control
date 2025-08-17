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
    if os.environ.get('FLASK_ENV') == 'production':
        # FORCE uso de PostgreSQL em produção
        db_url = os.environ['DATABASE_URL']
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        return db_url
    else:
        # SQLite apenas para desenvolvimento
        db_dir = BASE_DIR / 'database'
        db_dir.mkdir(exist_ok=True)
        db_path = f"sqlite:///{db_dir / 'app.db'}"
        print(f"Usando banco SQLite: {db_path}")
        return db_path

app.config['SQLALCHEMY_DATABASE_URI'] = get_database_uri()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Importações DEPOIS da configuração do app
from models.user import db
from models.nfe import NFeHeader  # IMPORTAÇÃO CRÍTICA
# Importe todos os outros modelos aqui

from routes.user import user_bp
from routes.opme import opme_bp
from routes.maino import maino_bp

# Registra blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(opme_bp, url_prefix='/api')
app.register_blueprint(maino_bp, url_prefix='/api')

# Inicializa o banco de dados
db.init_app(app)

# Verificação e criação do banco
with app.app_context():
    try:
        db.create_all()
        print("Tabelas do banco de dados criadas com sucesso!")
        
        # Verificação explícita da tabela problemática
        if not db.engine.dialect.has_table(db.engine, 'nfe_header'):
            print("AVISO: Tabela nfe_header não existe! Recriando banco...")
            db.drop_all()
            db.create_all()
            print("Banco recriado forçadamente!")
    except Exception as e:
        print(f"ERRO FATAL na criação do banco: {str(e)}")
        # Tenta recriar como última instância
        try:
            db.drop_all()
            db.create_all()
            print("Banco recriado em modo de emergência!")
        except Exception as e2:
            print(f"FALHA CRÍTICA: {str(e2)}")
            raise RuntimeError("Não foi possível inicializar o banco de dados")

# Rotas para SPA corrigidas
@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route('/<path:path>')
def serve_spa(path):
    if not os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, 'index.html')
    return send_from_directory(app.static_folder, path)

# Verificação de permissões (Docker)
def check_permissions():
    if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].split('///')[1]
        if os.path.exists(db_path):
            try:
                os.chmod(db_path, 0o666)
                print(f"Permissões ajustadas para: {db_path}")
            except Exception as e:
                print(f"AVISO: Não pude ajustar permissões: {str(e)}")

if __name__ == '__main__':
    check_permissions()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'false').lower() == 'true'
    app.run(host='0.0.0.0', port=port, debug=debug)