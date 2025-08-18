from flask import Blueprint, request, jsonify
import logging
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from src.models import db, NFeHeader, NFeItem
from src.utils.parse_nfe_xml import parse_nfe_xml

opme_bp = Blueprint('opme', __name__)

def parse_and_save_nfe(xml_content):
    try:
        # Parseia o XML
        parsed_data = parse_nfe_xml(xml_content)
        
        # Verifica se a NF já existe
        existing_nf = NFeHeader.query.filter_by(nNF=parsed_data['nNF']).first()
        if existing_nf:
            logging.warning(f"NF-e {parsed_data['nNF']} já existe no banco")
            return False

        # Cria cabeçalho
        header = NFeHeader(
            nNF=parsed_data['nNF'],
            dEmi=datetime.strptime(parsed_data['dEmi'], '%Y-%m-%d').date(),
            CNPJ_emit=parsed_data['CNPJ_emit'],
            xNome_emit=parsed_data['xNome_emit'],
            CNPJ_dest=parsed_data['CNPJ_dest'],
            xNome_dest=parsed_data['xNome_dest']
        )
        db.session.add(header)
        db.session.flush()  # Obtém ID para os itens

        # Adiciona itens
        for item in parsed_data['items']:
            nfe_item = NFeItem(
                nfe_header_id=header.id,
                cProd=item['cProd'],
                xProd=item['xProd'],
                CFOP=item['CFOP'],
                uCom=item['uCom'],
                qCom=float(item['qCom']),
                vUnCom=float(item['vUnCom']),
                nLote=item.get('nLote', ''),
                qLote=float(item.get('qLote', 0))
            )
            db.session.add(nfe_item)
        
        db.session.commit()
        return True
        
    except Exception as e:
        db.session.rollback()
        logging.exception(f"Erro ao processar NF-e: {str(e)}")
        return False

@opme_bp.route('/upload_xml', methods=['POST'])
def upload_xml():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Nome de arquivo vazio'}), 400
        
        if file.filename.lower().endswith('.xml'):
            try:
                xml_content = file.read().decode('utf-8')
                
                if parse_and_save_nfe(xml_content):
                    return jsonify({'message': 'XML processado com sucesso'}), 200
                else:
                    return jsonify({'error': 'Falha ao processar XML'}), 400
                    
            except Exception as e:
                logging.exception("Erro no processamento")
                return jsonify({'error': f'Erro no processamento: {str(e)}'}), 500
        else:
            return jsonify({'error': 'Apenas XML são aceitos'}), 400
            
    except Exception as e:
        logging.exception("Erro geral no upload")
        return jsonify({'error': f'Erro geral: {str(e)}'}), 500

@opme_bp.route('/balance', methods=['GET'])
def get_balance():
    try:
        cnpj_cliente = request.args.get('cnpj_cliente')
        
        # Consulta usando ORM
        movements = db.session.query(
            NFeHeader.nNF,
            NFeHeader.dEmi,
            NFeHeader.CNPJ_dest,
            NFeHeader.xNome_dest,
            NFeItem.cProd,
            NFeItem.xProd,
            NFeItem.CFOP,
            NFeItem.qCom,
            NFeItem.nLote,
            NFeItem.qLote
        ).join(NFeItem).filter(
            NFeHeader.CNPJ_dest == cnpj_cliente
        ).all()
        
        # Cálculo do saldo
        balance = {}
        for mov in movements:
            key = (mov.CNPJ_dest, mov.xNome_dest, mov.cProd, mov.xProd, mov.nLote)
            
            if mov.CFOP in ['5102', '6102']:  # Entradas
                balance.setdefault(key, 0)
                balance[key] += mov.qCom
            elif mov.CFOP in ['5405', '6405']:  # Saídas
                balance.setdefault(key, 0)
                balance[key] -= mov.qCom
        
        # Formata resposta
        balance_list = [{
            'cnpj_cliente': key[0],
            'nome_cliente': key[1],
            'codigo_produto': key[2],
            'descricao_produto': key[3],
            'lote': key[4],
            'saldo': saldo
        } for key, saldo in balance.items()]
        
        return jsonify(balance_list), 200
        
    except Exception as e:
        logging.exception("Erro ao calcular saldo")
        return jsonify({'error': f'Erro ao calcular saldo: {str(e)}'}), 500

@opme_bp.route('/movements', methods=['GET'])
def get_movements():
    try:
        cnpj_cliente = request.args.get('cnpj_cliente')
        
        movements = db.session.query(
            NFeHeader.nNF,
            NFeHeader.dEmi,
            NFeHeader.CNPJ_dest,
            NFeHeader.xNome_dest,
            NFeItem.cProd,
            NFeItem.xProd,
            NFeItem.CFOP,
            NFeItem.qCom,
            NFeItem.nLote,
            NFeItem.qLote
        ).join(NFeItem).filter(
            NFeHeader.CNPJ_dest == cnpj_cliente
        ).all()
        
        movements_list = []
        for mov in movements:
            movements_list.append({
                'numero_nf': mov.nNF,
                'data_emissao': mov.dEmi.strftime('%Y-%m-%d'),
                'cnpj_cliente': mov.CNPJ_dest,
                'nome_cliente': mov.xNome_dest,
                'codigo_produto': mov.cProd,
                'descricao_produto': mov.xProd,
                'cfop': mov.CFOP,
                'quantidade': mov.qCom,
                'lote': mov.nLote,
                'quantidade_lote': mov.qLote
            })
        
        return jsonify(movements_list), 200
        
    except Exception as e:
        logging.exception("Erro ao obter movimentações")
        return jsonify({'error': f'Erro ao obter movimentações: {str(e)}'}), 500