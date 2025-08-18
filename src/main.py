import os
import sys
from datetime import datetime, timedelta

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# importa a instância única do SQLAlchemy (extensions.py)
from .extensions import db

# Configuração do Flask
app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'

# Habilita CORS para todas as rotas
CORS(app)

# Configuração do banco de dados
# Usa DATABASE_URL se disponível (por ex. Postgres em produção). Caso contrário, usa SQLite em /app/database/app.db
db_uri = os.environ.get("DATABASE_URL") or "sqlite:///database/app.db"
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Se for sqlite com arquivo, garante que o diretório exista antes de conectar/criar tabelas
if db_uri.startswith("sqlite"):
    import re
    m = re.match(r"sqlite:/*(.+)", db_uri)
    if m:
        # normaliza para caminho absoluto dentro do container
        db_file = "/" + m.group(1).lstrip("/")
        db_dir = os.path.dirname(db_file)
        try:
            os.makedirs(db_dir, exist_ok=True)
        except Exception:
            app.logger.exception("Não foi possível criar diretório do banco de dados: %s", db_dir)

# Inicializa o SQLAlchemy com a aplicação Flask
db.init_app(app)

# Cria as tabelas do banco de dados se não existirem (faz isso dentro do app_context)
with app.app_context():
    db.create_all()

# Agora que o DB está inicializado, importe serviços e models
from .services.xml_processor import XMLProcessor
from .services.estoque_service import EstoqueService
from .services.maino_api import MainoAPI
from .models.nfe import NFeHeader, NFeItem, EstoqueConsignacao

# Inicializa serviços
xml_processor = XMLProcessor()
estoque_service = EstoqueService()
maino_api = MainoAPI()

# Rotas da API
@app.route('/api/processar-xml', methods=['POST'])
def processar_xml():
    xml_content = request.json.get('xml_content')
    if not xml_content:
        return jsonify({'error': 'XML content is required'}), 400

    try:
        nfe_data = xml_processor.parse_nfe_xml(xml_content)
        estoque_service.process_nfe(nfe_data)
        return jsonify({'message': 'XML processed successfully', 'nfe_data': nfe_data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/estoque/resumo', methods=['GET'])
def get_estoque_resumo():
    resumo = estoque_service.get_estoque_resumo()
    return jsonify(resumo)

@app.route('/api/estoque/por-produto/<string:codigo_produto>', methods=['GET'])
def get_estoque_por_produto(codigo_produto):
    estoque = estoque_service.get_estoque_por_produto(codigo_produto)
    return jsonify(estoque)

@app.route('/api/estoque/por-cliente/<string:cnpj_cliente>', methods=['GET'])
def get_estoque_por_cliente(cnpj_cliente):
    estoque = estoque_service.get_estoque_por_cliente(cnpj_cliente)
    return jsonify(estoque)

@app.route('/api/sincronizar-maino', methods=['POST'])
def sincronizar_maino():
    data = request.get_json()
    dias_atras = data.get("dias_atras", 7)
    
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=dias_atras)
        resultado_nfes = maino_api.get_nfes_emitidas(start_date, end_date)

        if not resultado_nfes["sucesso"]:
            return jsonify(resultado_nfes), 400
        
        nfes_para_processar = resultado_nfes["nfes"]
        
        xmls_processados = 0
        nfes_saida = 0
        nfes_entrada = 0
        erros = []
        
        for nfe_item in nfes_para_processar:
            chave_acesso = nfe_item.get("chaveAcesso")
            if not chave_acesso:
                erros.append(f"NF-e sem chave de acesso: {nfe_item.get('numero')}")
                continue

            resultado_xml_completo = maino_api.get_nfe_xml_by_chave(chave_acesso)
            if not resultado_xml_completo["sucesso"]:
                erros.append(f"Erro ao buscar XML da NF-e {chave_acesso}: {resultado_xml_completo['erro']}")
                continue
            xml_content = resultado_xml_completo["xml_content"]

            try:
                nfe_data = xml_processor.parse_nfe_xml(xml_content)
                estoque_service.process_nfe(nfe_data)
                xmls_processados += 1
                if nfe_data['cfop'][0] == '5' or nfe_data['cfop'][0] == '6':
                    nfes_saida += 1
                else:
                    nfes_entrada += 1
            except Exception as e:
                erros.append(f"Erro ao processar NF-e {chave_acesso}: {str(e)}")
        
        return jsonify({
            "sucesso": True,
            "nfes_encontradas": len(nfes_para_processar),
            "nfes_processadas": xmls_processados,
            "nfes_saida": nfes_saida,
            "nfes_entrada": nfes_entrada,
            "erros": erros
        })
        
    except Exception as e:
        return jsonify({"sucesso": False, "erro": f"Erro na sincronização: {e}"}), 500

# Rota para servir arquivos estáticos (frontend)
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join('static', path)):
        return send_from_directory('static', path)
    else:
        return send_from_directory('static', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


@app.route("/test")
def test_route():
    return "Hello from Flask!"
