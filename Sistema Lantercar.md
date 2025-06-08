# Sistema Lantercar

Sistema de gestão para oficina mecânica desenvolvido em Flask com PostgreSQL.

## Funcionalidades

- **Gestão de Clientes**: Cadastro completo de clientes com CPF/CNPJ
- **Almoxarifado**: Controle de materiais e estoque
- **Orçamentos**: Criação e gestão de orçamentos com aprovação
- **Ordens de Serviço**: Geração automática após aprovação do orçamento
- **Contratos**: Geração automática de contratos
- **Notas Fiscais**: Emissão automática após conclusão do serviço
- **Relatórios**: Relatórios detalhados com exportação para Excel e PDF
- **Dashboard**: Painel executivo com indicadores
- **Autenticação**: Sistema de login com diferentes perfis de usuário

## Tecnologias

- **Backend**: Flask (Python)
- **Banco de Dados**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript, Bootstrap 5
- **Geração de PDF**: ReportLab
- **Exportação Excel**: OpenPyXL
- **Deploy**: Render.com com Gunicorn

## Instalação Local

### Pré-requisitos

- Python 3.11+
- PostgreSQL
- Git

### Passos

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd lantercar
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure as variáveis de ambiente:
```bash
cp .env.example .env
# Edite o arquivo .env com suas configurações
```

5. Configure o banco de dados PostgreSQL:
```sql
CREATE DATABASE lantercar;
CREATE USER lantercar_user WITH PASSWORD 'sua_senha';
GRANT ALL PRIVILEGES ON DATABASE lantercar TO lantercar_user;
```

6. Execute as migrações:
```bash
cd src
python main.py
```

7. Acesse o sistema:
```
http://localhost:5000
```

### Usuário Padrão

- **Usuário**: rodrigo
- **Senha**: 1234

## Deploy no Render

### Preparação

1. Faça push do código para o GitHub
2. Conecte sua conta do Render ao GitHub
3. Crie um novo Web Service no Render

### Configuração

1. **Repository**: Selecione o repositório do projeto
2. **Branch**: main (ou sua branch principal)
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `gunicorn --bind 0.0.0.0:$PORT wsgi:app`

### Variáveis de Ambiente

Configure as seguintes variáveis no Render:

- `FLASK_ENV`: production
- `SECRET_KEY`: (gere uma chave secreta)
- `DATABASE_URL`: (será fornecida automaticamente pelo banco PostgreSQL do Render)

### Banco de Dados

1. Crie um PostgreSQL database no Render
2. O `DATABASE_URL` será configurado automaticamente
3. O sistema criará as tabelas automaticamente na primeira execução

## Estrutura do Projeto

```
lantercar/
├── src/
│   ├── main.py              # Aplicação principal
│   ├── config.py            # Configurações
│   ├── models/              # Modelos do banco de dados
│   ├── routes/              # Rotas da aplicação
│   ├── templates/           # Templates HTML
│   ├── static/              # Arquivos estáticos
│   └── utils/               # Utilitários (geração de PDF, etc.)
├── requirements.txt         # Dependências Python
├── wsgi.py                 # Arquivo WSGI para deploy
├── render.yaml             # Configuração do Render
└── README.md               # Este arquivo
```

## Uso do Sistema

### Fluxo Principal

1. **Cadastrar Cliente**: Registre os dados do cliente
2. **Criar Orçamento**: Elabore o orçamento com materiais e mão de obra
3. **Aprovar Orçamento**: Cliente aprova o orçamento
4. **Ordem de Serviço**: Sistema gera automaticamente a ordem
5. **Contrato**: Sistema gera automaticamente o contrato
6. **Executar Serviço**: Marque a ordem como concluída
7. **Nota Fiscal**: Sistema gera automaticamente a nota fiscal

### Relatórios

- Acesse **Relatórios > Relatório de Serviços** para visualizar todos os serviços
- Use filtros por período, cliente e status
- Exporte para Excel ou PDF conforme necessário
- Acesse **Relatórios > Dashboard** para visão executiva

## Suporte

Para suporte técnico ou dúvidas sobre o sistema, entre em contato com a equipe de desenvolvimento.

## Licença

Este sistema foi desenvolvido especificamente para a Lantercar Oficina Mecânica.

