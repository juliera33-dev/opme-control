import requests
import json
from datetime import datetime
import tempfile
import zipfile
import os
from src.insert_nfe_data import insert_nfe_data

class MainoAPI:
    def __init__(self, api_key=None, bearer_token=None):
        self.base_url = "https://api.maino.com.br/api/v2"
        self.api_key = api_key
        self.bearer_token = bearer_token
        
    def _get_headers(self):
        """Retorna os headers para autenticação"""
        headers = {"Content-Type": "application/json"}
        
        if self.bearer_token:
            headers["Authorization"] = f"Bearer {self.bearer_token}"
        elif self.api_key:
            headers["X-Api-Key"] = self.api_key
        
        return headers
    
    def listar_notas_fiscais_emitidas(self, data_inicio, data_fim, numero_nfe=None, cnpj_destinatario=None, exibir_xmls=False):
        """
        Lista notas fiscais emitidas
        
        Args:
            data_inicio (str): Data de início no formato DD/MM/AAAA
            data_fim (str): Data de fim no formato DD/MM/AAAA
            numero_nfe (str, optional): Número da NF-e para filtrar
            cnpj_destinatario (str, optional): CNPJ do destinatário para filtrar
            exibir_xmls (bool): Se deve incluir XMLs na resposta
        
        Returns:
            dict: Resposta da API com as notas fiscais
        """
        endpoint = f"{self.base_url}/notas_fiscais_emitidas"
        
        params = {
            "data_inicio": data_inicio,
            "data_fim": data_fim,
            "exibir_xmls": str(exibir_xmls).lower()
        }
        
        if numero_nfe:
            params["numero_nfe"] = numero_nfe
        if cnpj_destinatario:
            params["cnpj_destinatario"] = cnpj_destinatario
        
        try:
            response = requests.get(endpoint, headers=self._get_headers(), params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao listar notas fiscais: {e}")
            return None
    
    def exportar_xmls_nfes_emitidas(self, data_inicio, data_fim):
        """
        Exporta XMLs das NF-es emitidas em um período
        
        Args:
            data_inicio (str): Data de início no formato DD/MM/AAAA
            data_fim (str): Data de fim no formato DD/MM/AAAA
        
        Returns:
            str: URL do arquivo ZIP com os XMLs ou None em caso de erro
        """
        endpoint = f"{self.base_url}/nfes_emitidas"
        
        params = {
            "data_inicio": data_inicio,
            "data_fim": data_fim
        }
        
        try:
            response = requests.get(endpoint, headers=self._get_headers(), params=params)
            response.raise_for_status()
            result = response.json()
            return result.get("zip_url")
        except requests.exceptions.RequestException as e:
            print(f"Erro ao exportar XMLs: {e}")
            return None
    
    def baixar_e_processar_xmls(self, data_inicio, data_fim, db_path="database/app.db"):
        """
        Baixa XMLs do Mainô e processa automaticamente
        
        Args:
            data_inicio (str): Data de início no formato DD/MM/AAAA
            data_fim (str): Data de fim no formato DD/MM/AAAA
            db_path (str): Caminho para o banco de dados
        
        Returns:
            dict: Resultado do processamento
        """
        # Exportar XMLs
        zip_url = self.exportar_xmls_nfes_emitidas(data_inicio, data_fim)
        
        if not zip_url:
            return {"success": False, "message": "Erro ao obter URL do ZIP"}
        
        try:
            # Baixar o arquivo ZIP
            zip_response = requests.get(zip_url)
            zip_response.raise_for_status()
            
            # Salvar temporariamente
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_zip:
                temp_zip.write(zip_response.content)
                temp_zip_path = temp_zip.name
            
            # Extrair e processar XMLs
            processed_count = 0
            errors = []
            
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                # Criar diretório temporário para extração
                with tempfile.TemporaryDirectory() as temp_dir:
                    zip_ref.extractall(temp_dir)
                    
                    # Processar cada arquivo XML
                    for filename in os.listdir(temp_dir):
                        if filename.lower().endswith('.xml'):
                            xml_path = os.path.join(temp_dir, filename)
                            try:
                                insert_nfe_data(xml_path, db_path)
                                processed_count += 1
                            except Exception as e:
                                errors.append(f"Erro ao processar {filename}: {str(e)}")
            
            # Limpar arquivo ZIP temporário
            os.unlink(temp_zip_path)
            
            return {
                "success": True,
                "processed_count": processed_count,
                "errors": errors,
                "message": f"Processados {processed_count} XMLs com sucesso"
            }
            
        except Exception as e:
            return {"success": False, "message": f"Erro ao processar XMLs: {str(e)}"}

# Exemplo de uso
def exemplo_uso():
    """Exemplo de como usar a integração com o Mainô"""
    
    # Inicializar com chave de API (método recomendado)
    api = MainoAPI(api_key="sua_chave_api_aqui")
    
    # Ou inicializar com Bearer Token
    # api = MainoAPI(bearer_token="seu_bearer_token_aqui")
    
    # Listar notas fiscais de um período
    data_inicio = "01/01/2025"
    data_fim = "31/01/2025"
    
    notas = api.listar_notas_fiscais_emitidas(data_inicio, data_fim)
    if notas:
        print(f"Encontradas {len(notas.get('notas_fiscais', []))} notas fiscais")
    
    # Baixar e processar XMLs automaticamente
    resultado = api.baixar_e_processar_xmls(data_inicio, data_fim)
    if resultado["success"]:
        print(resultado["message"])
    else:
        print(f"Erro: {resultado['message']}")

if __name__ == "__main__":
    exemplo_uso()

