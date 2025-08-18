from ..opme_logic import get_opme_movements, calculate_balance

class EstoqueService:
    """
    Implementação mínima para permitir que a aplicação suba sem erro.
    Substitua/expanda esses métodos para usar SQLAlchemy e persistência real.
    """
    def process_nfe(self, nfe_data):
        # Placeholder: aqui você implementaria a lógica de persistência
        # usando seus models/SQLAlchemy.
        return True

    def get_estoque_resumo(self):
        # Retorna um resumo (balance) como serializável JSON
        movements = get_opme_movements()
        balance = calculate_balance(movements)
        readable = []
        for k, v in balance.items():
            cnpj, nome, cprod, xprod, lote = k
            readable.append({
                "cnpj": cnpj,
                "nome": nome,
                "codigo_produto": cprod,
                "descricao_produto": xprod,
                "lote": lote,
                "saldo": v
            })
        return readable

    def get_estoque_por_produto(self, codigo_produto):
        movements = get_opme_movements()
        resultados = []
        for m in movements:
            _, dEmi, CNPJ_dest, xNome_dest, cProd, xProd, CFOP, qCom, nLote, qLote = m
            if str(cProd) == str(codigo_produto):
                resultados.append({
                    "data_emissao": dEmi,
                    "cnpj_cliente": CNPJ_dest,
                    "nome_cliente": xNome_dest,
                    "codigo_produto": cProd,
                    "descricao_produto": xProd,
                    "cfop": CFOP,
                    "quantidade": qLote if qLote else qCom,
                    "lote": nLote or ""
                })
        return resultados

    def get_estoque_por_cliente(self, cnpj_cliente):
        movements = get_opme_movements(cnpj_cliente=cnpj_cliente)
        resultados = []
        for m in movements:
            _, dEmi, CNPJ_dest, xNome_dest, cProd, xProd, CFOP, qCom, nLote, qLote = m
            resultados.append({
                "data_emissao": dEmi,
                "cnpj_cliente": CNPJ_dest,
                "nome_cliente": xNome_dest,
                "codigo_produto": cProd,
                "descricao_produto": xProd,
                "cfop": CFOP,
                "quantidade": qLote if qLote else qCom,
                "lote": nLote or ""
            })
        return resultados