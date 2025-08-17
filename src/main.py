import os
from flask import Flask, send_from_directory
from src.models.user import db
from src.routes.user import user_bp
from src.routes.opme import opme_bp
from src.routes.maino import maino_bp

# Cria o caminho absoluto para o diretório atual
current_dir = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, 
            static_folder=os.path.join(current_dir, 'static'),
            static_url_path='/')

# Configurações
app.config.from_pyfile('../config.py')  # Vamos criar este arquivo
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
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)