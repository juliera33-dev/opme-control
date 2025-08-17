from flask import Blueprint, request, jsonify
import os
from pathlib import Path
from src.parse_nfe_xml import parse_nfe_xml
from src.insert_nfe_data import insert_nfe_data
from src.opme_logic import get_opme_movements, calculate_balance

opme_bp = Blueprint('opme', __name__)

@opme_bp.route('/upload_xml', methods=['POST'])
def upload_xml():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo foi enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
        
        if file and file.filename.lower().endswith('.xml'):
            try:
                # Construir caminho do banco de dados
                current_dir = Path(__file__).resolve().parent
                db_path = current_dir.parent.parent / 'database' / 'app.db'
                
                # Processar XML diretamente da memória
                xml_content = file.read().decode('utf-8')
                insert_nfe_data(xml_content, str(db_path), is_file=False)
                
                return jsonify({'message': 'XML processado com sucesso'}), 200
                
            except Exception as processing_error:
                return jsonify({
                    'error': f'Erro no processamento: {str(processing_error)}'
                }), 500
        else:
            return jsonify({'error': 'Apenas arquivos XML são aceitos'}), 400
            
    except Exception as e:
        return jsonify({
            'error': f'Erro geral no upload: {str(e)}'
        }), 500

@opme_bp.route('/balance', methods=['GET'])
def get_balance():
    try:
        cnpj_cliente = request.args.get('cnpj_cliente')
        current_dir = Path(__file__).resolve().parent
        db_path = current_dir.parent.parent / 'database' / 'app.db'
        
        movements = get_opme_movements(str(db_path), cnpj_cliente)
        balance = calculate_balance(movements)
        
        balance_list = []
        for key, saldo in balance.items():
            cnpj_dest, xNome_dest, cProd, xProd, nLote = key
            balance_list.append({
                'cnpj_cliente': cnpj_dest,
                'nome_cliente': xNome_dest,
                'codigo_produto': cProd,
                'descricao_produto': xProd,
                'lote': nLote,
                'saldo': saldo
            })
        
        return jsonify(balance_list), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Erro ao calcular saldo: {str(e)}'
        }), 500

@opme_bp.route('/movements', methods=['GET'])
def get_movements():
    try:
        cnpj_cliente = request.args.get('cnpj_cliente')
        current_dir = Path(__file__).resolve().parent
        db_path = current_dir.parent.parent / 'database' / 'app.db'
        
        movements = get_opme_movements(str(db_path), cnpj_cliente)
        
        movements_list = []
        for movement in movements:
            nNF, dEmi, CNPJ_dest, xNome_dest, cProd, xProd, CFOP, qCom, nLote, qLote = movement
            movements_list.append({
                'numero_nf': nNF,
                'data_emissao': dEmi,
                'cnpj_cliente': CNPJ_dest,
                'nome_cliente': xNome_dest,
                'codigo_produto': cProd,
                'descricao_produto': xProd,
                'cfop': CFOP,
                'quantidade': qCom,
                'lote': nLote,
                'quantidade_lote': qLote
            })
        
        return jsonify(movements_list), 200
        
    except Exception as e:
        return jsonify({
            'error': f'Erro ao obter movimentações: {str(e)}'
        }), 500