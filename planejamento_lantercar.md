# Sistema de Gestão Lantercar - Planejamento Detalhado

## Visão Geral
Sistema completo de gestão para oficina mecânica "Lantercar" com funcionalidades de:
- Almoxarifado (cadastro de materiais)
- Orçamentos
- Contratos automáticos
- Notas fiscais
- Relatórios exportáveis
- Gestão de usuários e clientes

## Tecnologias
- **Backend**: Flask (Python)
- **Banco de dados**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript (Bootstrap)
- **Deploy**: Render com Gunicorn
- **Geração de PDF**: ReportLab/WeasyPrint

## Modelos de Dados

### Usuario
- id (PK)
- nome
- email (unique)
- senha (hash)
- ativo
- data_criacao

### Cliente
- id (PK)
- nome
- cpf_cnpj
- telefone
- email
- endereco
- cidade
- estado
- cep
- data_cadastro

### Material
- id (PK)
- nome
- descricao
- codigo
- preco_unitario
- quantidade_estoque
- unidade_medida
- data_cadastro

### Orcamento
- id (PK)
- cliente_id (FK)
- usuario_id (FK)
- numero_orcamento
- data_orcamento
- validade
- descricao_servico
- valor_mao_obra
- valor_total
- status (pendente, aceito, rejeitado)
- observacoes

### OrcamentoItem
- id (PK)
- orcamento_id (FK)
- material_id (FK)
- quantidade
- preco_unitario
- subtotal

### OrdemServico
- id (PK)
- orcamento_id (FK)
- numero_ordem
- data_inicio
- data_conclusao
- status (em_andamento, concluido, cancelado)
- observacoes

### NotaFiscal
- id (PK)
- ordem_servico_id (FK)
- numero_nf
- data_emissao
- valor_total
- status (emitida, cancelada)

### Contrato
- id (PK)
- ordem_servico_id (FK)
- numero_contrato
- data_contrato
- termos_condicoes
- status (ativo, concluido, cancelado)

## Fluxo do Sistema

1. **Cadastro de Cliente** → Cliente é cadastrado no sistema
2. **Criação de Orçamento** → Orçamento é criado para o cliente com materiais e mão de obra
3. **Aceite do Orçamento** → Cliente aceita o orçamento
4. **Geração Automática** → Sistema gera automaticamente:
   - Ordem de Serviço
   - Contrato
   - Nota Fiscal (quando serviço for concluído)

## Funcionalidades por Módulo

### Autenticação
- Login/Logout
- Cadastro de usuários (apenas admin)
- Controle de sessão

### Almoxarifado
- Cadastrar materiais
- Editar materiais
- Listar materiais
- Controle de estoque

### Clientes
- Cadastrar clientes
- Editar clientes
- Listar clientes
- Buscar clientes

### Orçamentos
- Criar orçamento
- Adicionar materiais ao orçamento
- Calcular totais automaticamente
- Gerar PDF do orçamento
- Aceitar/Rejeitar orçamento

### Ordens de Serviço
- Geração automática após aceite
- Acompanhar status
- Gerar PDF da ordem

### Contratos
- Geração automática
- Gerar PDF do contrato

### Notas Fiscais
- Geração automática
- Gerar PDF da nota fiscal

### Relatórios
- Relatório de serviços por período
- Relatório de faturamento
- Exportação em PDF/Excel

## Estrutura de Arquivos
```
lantercar/
├── app.py
├── config.py
├── requirements.txt
├── models/
│   ├── __init__.py
│   ├── usuario.py
│   ├── cliente.py
│   ├── material.py
│   ├── orcamento.py
│   └── ordem_servico.py
├── routes/
│   ├── __init__.py
│   ├── auth.py
│   ├── almoxarifado.py
│   ├── clientes.py
│   ├── orcamentos.py
│   └── relatorios.py
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   └── ...
├── static/
│   ├── css/
│   ├── js/
│   └── img/
└── utils/
    ├── __init__.py
    ├── pdf_generator.py
    └── helpers.py
```

## Configurações para Deploy
- Gunicorn 21.2.0
- Variáveis de ambiente para PostgreSQL
- Configuração para Render
- CORS habilitado

