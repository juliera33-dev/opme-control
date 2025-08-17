import sqlite3

def setup_database(db_name="opme_control.db"):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Tabela para cabeçalho da NF-e
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nfe_header (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nNF TEXT NOT NULL,
            dEmi TEXT NOT NULL,
            CNPJ_emit TEXT NOT NULL,
            xNome_emit TEXT NOT NULL,
            CNPJ_dest TEXT NOT NULL,
            xNome_dest TEXT NOT NULL
        )
    ''')

    # Tabela para itens da NF-e (produtos)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nfe_item (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nfe_id INTEGER NOT NULL,
            cProd TEXT NOT NULL,
            xProd TEXT NOT NULL,
            CFOP TEXT NOT NULL,
            qCom REAL NOT NULL,
            vUnCom REAL NOT NULL,
            vProd REAL NOT NULL,
            FOREIGN KEY (nfe_id) REFERENCES nfe_header(id)
        )
    ''')

    # Tabela para informações de lote (rastreabilidade)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lote_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nfe_item_id INTEGER NOT NULL,
            nLote TEXT,
            qLote REAL,
            dFab TEXT,
            dVal TEXT,
            FOREIGN KEY (nfe_item_id) REFERENCES nfe_item(id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    setup_database()
    print("Banco de dados 'opme_control.db' configurado com sucesso.")


