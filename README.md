📦 Atualização Automática de Estoque – UniversoPet / Shoppub

Script em Python para sincronizar automaticamente o estoque do site (Shoppub / UniversoPet) com o saldo da Empresa 2 no SQL Server.

O script:

Busca todos os produtos do site via API

Identifica produtos com estoque 0 no site

Consulta o saldo da Empresa 2 no banco SQL Server

Atualiza o estoque no site em lote (máx. 50 produtos)

🚀 Funcionalidade

✔ Consulta produtos do site via API Shoppub
✔ Conecta ao SQL Server
✔ Compara estoque do site × saldo do ERP
✔ Atualiza apenas produtos necessários
✔ Respeita o limite de 50 produtos por envio
✔ Gera log detalhado no terminal

🧠 Regras de Negócio

Apenas produtos com estoque = 0 no site são avaliados

Apenas produtos com saldo > 0 na Empresa 2 são atualizados

Atualização ocorre em lote, respeitando:

Limite: 50 produtos por requisição

Delay entre envios

Produtos já com estoque no site não são alterados

🛠 Tecnologias Utilizadas

Python 3.9+

requests

pyodbc

SQL Server

API Shoppub / UniversoPet

📂 Estrutura do Projeto

Atualiza-Estoque-Site/

│

├── UniversoPet.py      # Script principal

├── README.md           # Documentação

⚙️ Configuração

1️⃣ Instalar dependências

pip install requests pyodbc

2️⃣ Configurar acesso à API

No arquivo UniversoPet.py:

HEADERS = {
    "accept": "application/json",
    "authorization": "Token SEU_TOKEN_AQUI",
    "content-type": "application/json"
}


⚠️ Nunca versionar o token em repositórios públicos.

3️⃣ Configurar SQL Server

SQL_CONN_STR = (
    "DRIVER={SQL Server};"
    "SERVER=SEU_SERVIDOR;"
    "DATABASE=BL_MASTER;"
    "UID=USUARIO;"
    "PWD=SENHA"
)

4️⃣ Endpoints utilizados

URL_LISTAR_PRODUTOS = "Colocar a sua url"

URL_ATUALIZAR_ESTOQUE = "Colocar a sua url"

▶️ Execução

python UniversoPet.py

🖥 Exemplo de Execução

🔍 Verificando 1784 produtos do site...

🧮 Produtos a atualizar: 45

➡️ Enviando lote 1/1 (45 produtos)

✅ Lote enviado com sucesso

===================================

📌 Produtos atualizados:

SKU 35119 → 15

SKU 35121 → 32

...

===================================

✅ Atualização finalizada — 45 produtos atualizados com sucesso.

🔐 Segurança

Token da API deve ficar em variável de ambiente em produção

Nunca commitar:

Token

Usuário/senha do banco

Recomendado uso de .env

⚠️ Limitações Conhecidas

A API aceita no máximo 50 produtos por envio

Atualizações acima desse limite resultarão em erro 405

A busca de saldo utiliza comparação por nome do produto

Pode ser ajustado para SKU se necessário 


📦 Atualização Automática de Estoque – UniversoPet (SKU = ID_PRODUTO)

Sistema em Python responsável por sincronizar automaticamente o estoque do site UniversoPet / Shoppub com o saldo real do ERP (SQL Server), utilizando como SKU o ID_PRODUTO.

🎯 Objetivo

Garantir que o estoque do site esteja sempre igual ao estoque do ERP, evitando:

produtos com estoque zerado indevidamente

vendas sem saldo real

divergência entre sistema e e-commerce

🚀 Funcionalidades

✔ Busca produtos do site via API UniversoPet

✔ Utiliza ID_PRODUTO como SKU

✔ Conecta ao SQL Server

✔ Consulta saldo real do ERP

✔ Compara estoque do site × estoque do ERP

✔ Atualiza apenas produtos com diferença

✔ Atualização em lote (máx. 50 produtos por envio)

✔ Delay automático entre requisições

✔ Log detalhado no terminal

🧠 Regras de Negócio

O SKU do site corresponde ao ID_PRODUTO do ERP

Apenas produtos encontrados na API são processados

Apenas produtos com saldo > 0 no ERP são enviados

Produtos sem diferença de estoque não são atualizados

A API aceita no máximo 50 produtos por requisição

Envio ocorre automaticamente em múltiplos lotes

🛠 Tecnologias Utilizadas

Python 3.9+

requests

pyodbc

SQL Server

API UniversoPet / Shoppub

📂 Estrutura do Projeto
Atualiza-Estoque-Site/
│
├── AtualizarSku.py      # Script principal
├── README.md           # Documentação

⚙️ Configuração

1️⃣ Instalar dependências

pip install requests pyodbc

2️⃣ Configurar acesso à API

No arquivo AtualizarSku.py:

HEADERS = {
    "accept": "application/json",
    "authorization": "Token SEU_TOKEN_AQUI",
    "content-type": "application/json"
}


⚠️ Nunca versionar o token em repositórios públicos.

3️⃣ Configurar SQL Server
SQL_CONN_STR = (
    "DRIVER={SQL Server};"
    "SERVER=SEU_SERVIDOR;"
    "DATABASE=BL_MASTER;"
    "UID=USUARIO;"
    "PWD=SENHA"
)

4️⃣ Endpoints utilizados

URL_LISTAR_PRODUTOS = "https://www.universopet.net.br/api/v1/produtos/"

URL_ATUALIZAR_PRODUTOS = "https://www.universopet.net.br/api/v1/produtos"

▶️ Execução

No terminal:

python AtualizarSku.py

🖥 Exemplo de Execução

🔍 SKUs encontrados no site: 7


SKU 43173 | Site: 0 | ERP: 4770

SKU 44032 | Site: 0 | ERP: 40

SKU 44069 | Site: 0 | ERP: 4234

SKU 44065 | Site: 0 | ERP: 365

SKU 44057 | Site: 0 | ERP: 114

SKU 44061 | Site: 0 | ERP: 1320

SKU 37334 | Site: 0 | ERP: 75

🚀 Atualizando 7 produtos...

✅ Atualização finalizada com sucesso.

🔐 Segurança

Recomendações:

Utilizar variáveis de ambiente (.env)

Nunca versionar:

Token da API

Usuário do banco

Senha do banco

Restringir acesso ao servidor SQL

⚠️ Limitações Conhecidas

API aceita no máximo 50 produtos por envio

Envios acima disso retornam erro HTTP

Atualização depende da disponibilidade da API

Estoque elevado pode sofrer delay no painel administrativo

🔄 Melhorias Futuras

 Modo Dry-Run (simulação sem envio)

 Log automático em arquivo .log

 Exportação de relatório .csv

 Atualização automática via Agendador de Tarefas

 Retry automático em falhas de API

 Limite máximo de estoque configurável

 Atualização de preço

 Integração com múltiplas empresas

👤 Autor

Desenvolido por Vinicius Vilaça
Desenvolvido para uso interno – UniversoPet

Automação de estoque via API Shoppub

