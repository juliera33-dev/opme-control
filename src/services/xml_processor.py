from ..parse_nfe_xml import parse_nfe_xml

class XMLProcessor:
    """
    Wrapper simples que expõe a interface esperada pelo main.py.
    Usa a função parse_nfe_xml existente em src/parse_nfe_xml.py.
    """
    def parse_nfe_xml(self, xml_content):
        # A função parse_nfe_xml no projeto aceita (xml_source, is_file=True/False)
        # Aqui estamos recebendo o conteúdo do XML, então passamos is_file=False.
        return parse_nfe_xml(xml_content, is_file=False)