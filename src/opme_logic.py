import sqlite3

def get_opme_movements(db_name="opme_control.db", cnpj_cliente=None):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    query = """
        SELECT
            nh.nNF,
            nh.dEmi,
            nh.CNPJ_dest,
            nh.xNome_dest,
            ni.cProd,
            ni.xProd,
            ni.CFOP,
            ni.qCom,
            li.nLote,
            li.qLote
        FROM
            nfe_header nh
        JOIN
            nfe_item ni ON nh.id = ni.nfe_id
        LEFT JOIN
            lote_info li ON ni.id = li.nfe_item_id
    """
    params = []

    if cnpj_cliente:
        query += " WHERE nh.CNPJ_dest = ?"
        params.append(cnpj_cliente)

    cursor.execute(query, params)
    movements = cursor.fetchall()
    conn.close()
    return movements

def calculate_balance(movements):
    balance = {}
    # CFOPs de saída para consignação
    cfop_saida_consignacao = ["5917", "6917"]
    # CFOPs de retorno de consignação
    cfop_retorno_consignacao = ["1918", "2918"]
    # CFOPs de retorno simbólico (utilizado)
    cfop_retorno_simbolico = ["1919", "2919"]
    # CFOPs de faturamento (venda)
    cfop_faturamento = ["5114", "6114"]

    for movement in movements:
        nNF, dEmi, CNPJ_dest, xNome_dest, cProd, xProd, CFOP, qCom, nLote, qLote_lote_info = movement

        # Usar qCom do item da NF, se qLote da lote_info não estiver disponível ou for 0
        quantity = qLote_lote_info if qLote_lote_info else qCom

        key = (CNPJ_dest, xNome_dest, cProd, xProd, nLote if nLote else "SEM_LOTE")

        if key not in balance:
            balance[key] = 0.0

        if CFOP in cfop_saida_consignacao:
            balance[key] -= quantity
        elif CFOP in cfop_retorno_consignacao or CFOP in cfop_retorno_simbolico:
            balance[key] += quantity
        # CFOPs de faturamento (5114, 6114) não afetam o saldo de consignação diretamente
        # pois representam a venda do material que já estava em consignação.
        # O controle de saldo aqui é sobre o que está em posse do cliente.

    return balance

if __name__ == '__main__':
    # Exemplo de uso
    # from insert_nfe_data import insert_nfe_data
    # insert_nfe_data("nfe_exemplo.xml") # Certifique-se de que o XML de exemplo foi inserido

    all_movements = get_opme_movements()
    print("Todos os movimentos:", all_movements)

    saldo_geral = calculate_balance(all_movements)
    print("Saldo Geral:", saldo_geral)

    # Exemplo com CNPJ específico (substitua pelo CNPJ do destinatário do seu XML de exemplo)
    # movements_cliente = get_opme_movements(cnpj_cliente="00000000000191")
    # print("Movimentos para cliente específico:", movements_cliente)
    # saldo_cliente = calculate_balance(movements_cliente)
    # print("Saldo para cliente específico:", saldo_cliente)


