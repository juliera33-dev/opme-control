def parse_nfe_xml(xml_content):
    # Implementação fictícia - substitua pela sua lógica real
    return {
        'nNF': '12345',
        'dEmi': '2023-01-01',
        'CNPJ_emit': '12345678000199',
        'xNome_emit': 'Fornecedor Exemplo',
        'CNPJ_dest': '98765432000100',
        'xNome_dest': 'Cliente Exemplo',
        'items': [
            {
                'cProd': '001',
                'xProd': 'Produto A',
                'CFOP': '5102',
                'uCom': 'UN',
                'qCom': '10',
                'vUnCom': '5.99',
                'nLote': 'LOTE001',
                'qLote': '10'
            },
            {
                'cProd': '002',
                'xProd': 'Produto B',
                'CFOP': '5405',
                'uCom': 'UN',
                'qCom': '5',
                'vUnCom': '12.50',
                'nLote': 'LOTE002',
                'qLote': '5'
            }
        ]
    }