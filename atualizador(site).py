import requests
import pyodbc
import time

# CONFIGURAÇÕES (substitua pelos seus dados)
URL_SITE = "<URL_DA_API_DE_PRODUTOS>"
URL_ATUALIZA = "<URL_DA_API_ATUALIZAR_ESTOQUE>"
HEADERS = {
    "accept": "application/json",
    "authorization": "Token <SEU_TOKEN_AQUI>",
    "content-type": "application/json"
}

# Conectar ao SQL Server
def conectar_sql_server():
    try:
        conn_str = "DRIVER={SQL Server};SERVER=<SEU_SERVIDOR>;DATABASE=<SEU_BANCO>;UID=<USUARIO>;PWD=<SENHA>"
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"Erro ao conectar SQL Server: {e}")
        return None

# Buscar todos os produtos do site (paginação)
def buscar_produtos_site():
    produtos = []
    url = URL_SITE
    while url:
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code != 200:
            print(f"Erro ao buscar produtos: {resp.status_code}")
            break
        data = resp.json()
        produtos.extend(data['results'])
        url = data.get('next')
    return produtos

# Consultar saldo da empresa 2 pelo nome (resolve ntext/varchar issues)
def consultar_saldo_empresa_2_por_nome(conn, nome_produto):
    cursor = conn.cursor()
    query = """
        SELECT ID_PRODUTO, SALDO
        FROM BL_MASTER.dbo.VIEW_PRODUTOS_DW
        WHERE CONVERT(NVARCHAR(MAX), NM_ORIGINAL) LIKE ?
          AND ID_EMPRESA = 2
    """
    cursor.execute(query, ('%' + nome_produto + '%',))
    return cursor.fetchone()

# Atualizar estoque no site
def atualizar_estoque_site(sku, saldo):
    payload = {"sku": sku, "saldo": saldo}
    resp = requests.post(URL_ATUALIZA, json=payload, headers=HEADERS)
    if resp.status_code == 200:
        print(f"✅ Estoque atualizado: SKU {sku} → {saldo}")
        return True
    else:
        print(f"❌ Erro ao atualizar SKU {sku}: {resp.status_code} - {resp.text}")
        return False

# Fluxo principal
def main():
    conn = conectar_sql_server()
    if not conn:
        return

    produtos_site = buscar_produtos_site()
    print(f"🔍 Verificando {len(produtos_site)} produtos do site...\n")

    atualizados = []

    # Atualiza estoque somente se saldo site = 0 e saldo empresa 2 > 0
    for p in produtos_site:
        sku = p.get('sku')
        nome = p.get('nome')
        saldo_site = p.get('estoque', 0)

        resultado_sql = consultar_saldo_empresa_2_por_nome(conn, nome)
        if resultado_sql:
            id_produto_sql, saldo_empresa2 = resultado_sql.ID_PRODUTO, int(resultado_sql.SALDO)
            if saldo_site == 0 and saldo_empresa2 > 0:
                sucesso = atualizar_estoque_site(sku, saldo_empresa2)
                if sucesso:
                    atualizados.append({
                        "sku": sku,
                        "nome": nome,
                        "saldo_antigo": saldo_site,
                        "saldo_novo": saldo_empresa2
                    })

    print("\n📌 Produtos atualizados:")
    for p in atualizados:
        print(f"SKU: {p['sku']} | Nome: {p['nome']} | Saldo antigo: {p['saldo_antigo']} → Saldo novo: {p['saldo_novo']}")

    print(f"\n✅ Atualização finalizada — {len(atualizados)} produtos atualizados com sucesso.")
    conn.close()

if __name__ == "__main__":
    main()
