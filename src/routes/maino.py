from flask import Blueprint, request, jsonify
import os
from src.maino_integration import MainoAPI

maino_bp = Blueprint('maino', __name__)

@maino_bp.route('/sync_maino', methods=['POST'])
def sync_maino():
    """Sincronizar dados do Mainô"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        if not data or 'data_inicio' not in data or 'data_fim' not in data:
            return jsonify({'error': 'data_inicio e data_fim são obrigatórios'}), 400
        
        api_key = data.get('api_key')
        bearer_token = data.get('bearer_token')
        
        if not api_key and not bearer_token:
            return jsonify({'error': 'api_key ou bearer_token é obrigatório'}), 400
        
        # Inicializar API do Mainô
        if api_key:
            maino_api = MainoAPI(api_key=api_key)
        else:
            maino_api = MainoAPI(bearer_token=bearer_token)
        
        # Caminho do banco de dados
        db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'app.db')
        
        # Baixar e processar XMLs
        resultado = maino_api.baixar_e_processar_xmls(
            data['data_inicio'],
            data['data_fim'],
            db_path
        )
        
        if resultado['success']:
            return jsonify({
                'message': resultado['message'],
                'processed_count': resultado['processed_count'],
                'errors': resultado['errors']
            }), 200
        else:
            return jsonify({'error': resultado['message']}), 500
            
    except Exception as e:
        return jsonify({'error': f'Erro na sincronização: {str(e)}'}), 500

@maino_bp.route('/list_nfes_maino', methods=['POST'])
def list_nfes_maino():
    """Listar NF-es do Mainô sem processar"""
    try:
        data = request.get_json()
        
        # Validar dados obrigatórios
        if not data or 'data_inicio' not in data or 'data_fim' not in data:
            return jsonify({'error': 'data_inicio e data_fim são obrigatórios'}), 400
        
        api_key = data.get('api_key')
        bearer_token = data.get('bearer_token')
        
        if not api_key and not bearer_token:
            return jsonify({'error': 'api_key ou bearer_token é obrigatório'}), 400
        
        # Inicializar API do Mainô
        if api_key:
            maino_api = MainoAPI(api_key=api_key)
        else:
            maino_api = MainoAPI(bearer_token=bearer_token)
        
        # Listar notas fiscais
        notas = maino_api.listar_notas_fiscais_emitidas(
            data['data_inicio'],
            data['data_fim'],
            numero_nfe=data.get('numero_nfe'),
            cnpj_destinatario=data.get('cnpj_destinatario'),
            exibir_xmls=data.get('exibir_xmls', False)
        )
        
        if notas:
            return jsonify(notas), 200
        else:
            return jsonify({'error': 'Erro ao listar notas fiscais do Mainô'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Erro ao listar NF-es: {str(e)}'}), 500

