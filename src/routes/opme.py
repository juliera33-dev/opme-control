from flask import Blueprint, request, jsonify
import os
from src.parse_nfe_xml import parse_nfe_xml
from ..insert_nfe_data import insert_nfe_data
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
                # Ler o conteúdo do arquivo diretamente na memória
                xml_content = file.read()
                
                # Fechar explicitamente o stream do arquivo
                if hasattr(file, 'close'):
                    file.close()
                
                # Decodificar para string se necessário
                if isinstance(xml_content, bytes):
                    xml_content = xml_content.decode('utf-8')
                
                # Processar o XML e inserir no banco de dados
                db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'app.db')
                insert_nfe_data(xml_content, db_path, is_file=False)
                
                return jsonify({'message': 'XML processado com sucesso'}), 200
                
            except Exception as processing_error:
                # Se houver erro no processamento, tentar limpar recursos
                try:
                    if hasattr(file, 'close'):
                        file.close()
                except:
                    pass
                raise processing_error
        else:
            return jsonify({'error': 'Apenas arquivos XML são aceitos'}), 400
            
    except Exception as e:
        error_msg = str(e)
        if "WinError 32" in error_msg or "arquivo já está sendo usado" in error_msg:
            return jsonify({
                'error': 'Erro de arquivo em uso no Windows. Tente novamente em alguns segundos ou reinicie a aplicação.',
                'details': error_msg
            }), 500
        else:
            return jsonify({'error': f'Erro ao processar XML: {error_msg}'}), 500

@opme_bp.route('/balance', methods=['GET'])
def get_balance():
    try:
        cnpj_cliente = request.args.get('cnpj_cliente')
        db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'app.db')
        
        movements = get_opme_movements(db_path, cnpj_cliente)
        balance = calculate_balance(movements)
        
        # Converter o resultado para um formato mais amigável
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
        return jsonify({'error': f'Erro ao calcular saldo: {str(e)}'}), 500

@opme_bp.route('/movements', methods=['GET'])
def get_movements():
    try:
        cnpj_cliente = request.args.get('cnpj_cliente')
        db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'app.db')
        
        movements = get_opme_movements(db_path, cnpj_cliente)
        
        # Converter o resultado para um formato mais amigável
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
        return jsonify({'error': f'Erro ao obter movimentações: {str(e)}'}), 500

