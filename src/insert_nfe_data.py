import sqlite3
from src.parse_nfe_xml import parse_nfe_xml

def insert_nfe_data(xml_content, db_name="opme_control.db", is_file=True):
    if is_file:
        nfe_data = parse_nfe_xml(xml_content)
    else:
        # Se não for um arquivo, assume que xml_content é o próprio conteúdo XML
        nfe_data = parse_nfe_xml(xml_content, is_file=False)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Inserir cabeçalho da NF-e
    cursor.execute("""
        INSERT INTO nfe_header (nNF, dEmi, CNPJ_emit, xNome_emit, CNPJ_dest, xNome_dest)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        nfe_data["nNF"],
        nfe_data["dEmi"],
        nfe_data["CNPJ_emit"],
        nfe_data["xNome_emit"],
        nfe_data["CNPJ_dest"],
        nfe_data["xNome_dest"]
    ))
    nfe_id = cursor.lastrowid

    # Inserir itens da NF-e e informações de lote
    for product in nfe_data["products"]:
        cursor.execute("""
            INSERT INTO nfe_item (nfe_id, cProd, xProd, CFOP, qCom, vUnCom, vProd)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            nfe_id,
            product["cProd"],
            product["xProd"],
            product["CFOP"],
            product["qCom"],
            product["vUnCom"],
            product["vProd"]
        ))
        nfe_item_id = cursor.lastrowid

        lote_info = product["lote_info"]
        if lote_info["nLote"]:
            cursor.execute("""
                INSERT INTO lote_info (nfe_item_id, nLote, qLote, dFab, dVal)
                VALUES (?, ?, ?, ?, ?)
            """, (
                nfe_item_id,
                lote_info["nLote"],
                lote_info["qLote"],
                lote_info["dFab"],
                lote_info["dVal"]
            ))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    # Exemplo de uso
    # insert_nfe_data("nfe_exemplo.xml")
    # print("Dados da NF-e inseridos no banco de dados com sucesso.")
    pass


