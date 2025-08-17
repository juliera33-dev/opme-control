import xml.etree.ElementTree as ET

def parse_nfe_xml(xml_source, is_file=True):
    if is_file:
        tree = ET.parse(xml_source)
        root = tree.getroot()
    else:
        root = ET.fromstring(xml_source)

    # Namespace para a NF-e
    ns = {"nfe": "http://www.portalfiscal.inf.br/nfe"}

    # Extrair informações da NF-e
    ide = root.find(".//nfe:ide", ns)
    dEmi = ide.find("nfe:dEmi", ns).text if ide is not None and ide.find("nfe:dEmi", ns) is not None else ""
    nNF = ide.find("nfe:nNF", ns).text if ide is not None and ide.find("nfe:nNF", ns) is not None else ""

    emit = root.find(".//nfe:emit", ns)
    CNPJ_emit = emit.find("nfe:CNPJ", ns).text if emit is not None and emit.find("nfe:CNPJ", ns) is not None else ""
    xNome_emit = emit.find("nfe:xNome", ns).text if emit is not None and emit.find("nfe:xNome", ns) is not None else ""

    dest = root.find(".//nfe:dest", ns)
    CNPJ_dest = dest.find("nfe:CNPJ", ns).text if dest is not None and dest.find("nfe:CNPJ", ns) is not None else ""
    xNome_dest = dest.find("nfe:xNome", ns).text if dest is not None and dest.find("nfe:xNome", ns) is not None else ""

    products = []
    for det in root.findall(".//nfe:det", ns):
        prod = det.find("nfe:prod", ns)
        cProd = prod.find("nfe:cProd", ns).text if prod is not None and prod.find("nfe:cProd", ns) is not None else ""
        xProd = prod.find("nfe:xProd", ns).text if prod is not None and prod.find("nfe:xProd", ns) is not None else ""
        CFOP = prod.find("nfe:CFOP", ns).text if prod is not None and prod.find("nfe:CFOP", ns) is not None else ""
        qCom = prod.find("nfe:qCom", ns).text if prod is not None and prod.find("nfe:qCom", ns) is not None else "0.0"
        vUnCom = prod.find("nfe:vUnCom", ns).text if prod is not None and prod.find("nfe:vUnCom", ns) is not None else "0.0"
        vProd = prod.find("nfe:vProd", ns).text if prod is not None and prod.find("nfe:vProd", ns) is not None else "0.0"

        lote_info = {
            "nLote": "",
            "qLote": "",
            "dFab": "",
            "dVal": ""
        }
        rastro = prod.find("nfe:rastro", ns)
        if rastro is not None:
            lote_info["nLote"] = rastro.find("nfe:nLote", ns).text if rastro.find("nfe:nLote", ns) is not None else ""
            lote_info["qLote"] = rastro.find("nfe:qLote", ns).text if rastro.find("nfe:qLote", ns) is not None else ""
            lote_info["dFab"] = rastro.find("nfe:dFab", ns).text if rastro.find("nfe:dFab", ns) is not None else ""
            lote_info["dVal"] = rastro.find("nfe:dVal", ns).text if rastro.find("nfe:dVal", ns) is not None else ""

        products.append({
            "cProd": cProd,
            "xProd": xProd,
            "CFOP": CFOP,
            "qCom": float(qCom),
            "vUnCom": float(vUnCom),
            "vProd": float(vProd),
            "lote_info": lote_info
        })

    return {
        "dEmi": dEmi,
        "nNF": nNF,
        "CNPJ_emit": CNPJ_emit,
        "xNome_emit": xNome_emit,
        "CNPJ_dest": CNPJ_dest,
        "xNome_dest": xNome_dest,
        "products": products
    }

if __name__ == "__main__":
    # Exemplo de uso (substitua "caminho/para/sua/nfe.xml" pelo caminho real do arquivo)
    # Para testar, você pode usar o conteúdo do XML que obtivemos anteriormente e salvar em um arquivo.
    # Por exemplo, salve o conteúdo em "nfe_exemplo.xml"
    # xml_data = parse_nfe_xml("nfe_exemplo.xml")
    # print(xml_data)
    pass


