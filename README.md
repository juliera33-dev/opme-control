# Sistema de Controle de OPME - Akos Med

## Descrição

Sistema desenvolvido para controlar a movimentação de OPME (Órteses, Próteses e Materiais Especiais) em consignação, permitindo rastreabilidade completa por cliente, NF e lote através da importação de XMLs de Notas Fiscais eletrônicas.

## Funcionalidades

### ✅ Implementadas

1. **Importação de XML por arquivo individual**
   - Upload de arquivos XML de NF-e
   - Parsing automático dos dados relevantes
   - Extração de informações de lote (rastreabilidade)

2. **Controle de Saldo por CFOP**
   - CFOP 5917/6917: Saída para consignação
   - CFOP 1918/2918: Retorno de consignação
   - CFOP 1919/2919: Retorno simbólico (material utilizado)
   - CFOP 5114/6114: Faturamento (venda)

3. **Consultas e Relatórios**
   - Consulta de saldo por cliente (CNPJ ou nome)
   - Visualização de movimentações históricas
   - Filtros por cliente específico

4. **Interface Web Responsiva**
   - Design moderno e intuitivo
   - Tabelas organizadas com cores para saldos
   - Feedback visual para operações

### 🔄 Preparadas para Futuro

5. **Integração com API do Mainô**
   - Módulo completo de integração desenvolvido
   - Sincronização automática de XMLs
   - Aguardando correção do endpoint pela equipe de desenvolvimento

## Estrutura do Projeto

```
opme_control_app/
├── src/
│   ├── main.py                 # Aplicação Flask principal
│   ├── parse_nfe_xml.py        # Parser de XML de NF-e
│   ├── insert_nfe_data.py      # Inserção de dados no banco
│   ├── opme_logic.py           # Lógica de negócio OPME
│   ├── database_setup.py       # Configuração do banco de dados
│   ├── maino_integration.py    # Integração com API do Mainô
│   ├── routes/
│   │   ├── opme.py            # Rotas da aplicação OPME
│   │   ├── maino.py           # Rotas de integração Mainô
│   │   └── user.py            # Rotas de usuário (template)
│   ├── static/
│   │   └── index.html         # Interface web
│   └── database/
│       └── app.db             # Banco de dados SQLite
├── venv/                      # Ambiente virtual Python
├── requirements.txt           # Dependências
└── README.md                  # Esta documentação
```

## Instalação e Execução

### Pré-requisitos
- Python 3.11+
- pip

### Passos

1. **Navegar para o diretório do projeto**
   ```bash
   cd opme_control_app
   ```

2. **Ativar o ambiente virtual**
   ```bash
   source venv/bin/activate
   ```

3. **Instalar dependências** (se necessário)
   ```bash
   pip install -r requirements.txt
   ```

4. **Executar a aplicação**
   ```bash
   python src/main.py
   ```

5. **Acessar no navegador**
   ```
   http://localhost:5000
   ```

## Como Usar

### 1. Importar XML de NF-e

1. Clique em "Choose File" na seção "Importar XML de NF-e"
2. Selecione um arquivo XML de NF-e
3. Clique em "Importar XML"
4. Aguarde a confirmação de processamento

### 2. Consultar Saldo

1. Na seção "Consultar Saldo por Cliente":
   - Deixe o campo CNPJ vazio para ver todos os clientes
   - Ou digite o CNPJ específico do cliente
2. Clique em "Consultar Saldo"
3. Visualize os resultados na tabela:
   - **Verde**: Saldo positivo (material devolvido)
   - **Vermelho**: Saldo negativo (material em consignação)

### 3. Ver Movimentações

1. Clique em "Ver Movimentações"
2. Visualize o histórico completo de todas as NFs processadas
3. Analise os CFOPs para entender o tipo de movimentação

## Estrutura do Banco de Dados

### Tabela: nfe_header
- `id`: ID único da NF-e
- `nNF`: Número da NF-e
- `dEmi`: Data de emissão
- `CNPJ_emit`: CNPJ do emitente
- `xNome_emit`: Nome do emitente
- `CNPJ_dest`: CNPJ do destinatário
- `xNome_dest`: Nome do destinatário

### Tabela: nfe_item
- `id`: ID único do item
- `nfe_id`: Referência à NF-e
- `cProd`: Código do produto
- `xProd`: Descrição do produto
- `CFOP`: Código CFOP
- `qCom`: Quantidade comercial
- `vUnCom`: Valor unitário comercial
- `vProd`: Valor total do produto

### Tabela: lote_info
- `id`: ID único do lote
- `nfe_item_id`: Referência ao item da NF-e
- `nLote`: Número do lote
- `qLote`: Quantidade do lote
- `dFab`: Data de fabricação
- `dVal`: Data de validade

## Lógica de Negócio - CFOPs

### Saída (Diminui Saldo)
- **5917/6917**: Saída para consignação
  - Material enviado ao cliente
  - Saldo fica negativo (em consignação)

### Entrada (Aumenta Saldo)
- **1918/2918**: Retorno de consignação
  - Material devolvido pelo cliente
  - Saldo volta ao positivo

- **1919/2919**: Retorno simbólico
  - Material foi utilizado (implantado)
  - Confirma utilização do material

### Faturamento
- **5114/6114**: Venda do material
  - Representa a cobrança do material utilizado
  - Não afeta o saldo de consignação diretamente

## API Endpoints

### OPME
- `POST /api/upload_xml`: Upload de arquivo XML
- `GET /api/balance`: Consultar saldo (parâmetro: cnpj_cliente)
- `GET /api/movements`: Listar movimentações (parâmetro: cnpj_cliente)

### Mainô (Futuro)
- `POST /api/sync_maino`: Sincronizar dados do Mainô
- `POST /api/list_nfes_maino`: Listar NF-es do Mainô

## Integração com Mainô

### Configuração Futura

Quando o endpoint da API do Mainô for corrigido, você poderá usar:

```python
from src.maino_integration import MainoAPI

# Inicializar com chave de API
api = MainoAPI(api_key="sua_chave_api")

# Baixar e processar XMLs automaticamente
resultado = api.baixar_e_processar_xmls("01/01/2025", "31/01/2025")
```

### Endpoints do Mainô
- **GET /api/v2/notas_fiscais_emitidas**: Listar NF-es
- **GET /api/v2/nfes_emitidas**: Exportar XMLs em ZIP

## Troubleshooting

### Erro "no such table"
- Certifique-se de que o banco de dados foi criado
- Execute `python src/database_setup.py` se necessário

### Erro de importação de módulos
- Verifique se o ambiente virtual está ativado
- Instale as dependências: `pip install -r requirements.txt`

### Problemas com XML
- Verifique se o arquivo é um XML válido de NF-e
- Confirme se contém as tags necessárias (ide, emit, dest, det)

## Suporte

Para dúvidas ou problemas:
1. Verifique os logs da aplicação Flask
2. Consulte esta documentação
3. Entre em contato com a equipe de desenvolvimento

## Versão

**v1.0** - Sistema completo de controle de OPME com importação por arquivo XML individual e preparação para integração com API do Mainô.

