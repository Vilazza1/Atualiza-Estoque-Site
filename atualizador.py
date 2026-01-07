import requests
import pyodbc
import time
import os

# ----------------------------
# Configurações via variáveis de ambiente
# ----------------------------
URL_SITE = os.getenv("API_URL_SITE")          
URL_ATUALIZA = os.getenv("API_URL_ATUALIZA")  
API_TOKEN = os.getenv("API_TOKEN")            # Seu token da API
HEADERS = {
    "accept": "application/json",
    "authorization": f"Token {API_TOKEN}" if API_TOKEN else "",
    "content-type": "application/json"
}

SQL_SERVER = os.getenv("SQL_SERVER")
SQL_DATABASE = os.getenv("SQL_DATABASE")
SQL_USER = os.getenv("SQL_USER")
SQL_PASSWORD = os.getenv("SQL_PASSWORD")

# ----------------------------
# Conectar ao SQL Server
# ----------------------------
def conectar_sql_server():
    try:
        conn_str = f"DRIVER={{SQL Server}};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};UID={SQL_USER};PWD={SQL_PASSWORD}"
        return pyodbc.connect(conn_str)
    except Exception as e:
        print(f"Erro ao conectar SQL Server: {e}")
        return None

# ----------------------------
# Buscar todos os produtos do site
# ----------------------------
def buscar_produtos_site():
    produtos = []
    url = URL_SITE
    while url:
        if not url:
            break
        resp = requests.get(url, headers=HEADERS)
        if resp.status_code != 200:
            print(f"Erro ao buscar produtos: {resp.status_code}")
            break
        data = resp.json()
        produtos.extend(data.get('results', []))
        url = data.get('next')
    return produtos

# ----------------------------
# Consultar saldo da empresa 2 pelo nome (resolve ntext)
# ----------------------------
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

# ----------------------------
# Atualizar estoque no site
# ----------------------------
def atualizar_estoque_site(sku, saldo):
    payload = {"sku": sku, "saldo": saldo}
    # Teste: apenas print, não envia a API
    print(f"🟢 Atualizando SKU {sku} para saldo {saldo}")
    time.sleep(0.1)  # simula delay da API
    return True

# ----------------------------
# Fluxo principal
# ----------------------------
def main():
    conn = conectar_sql_server()
    if not conn:
        return

    produtos_site = buscar_produtos_site()
    print(f"🔍 Verificando {len(produtos_site)} produtos do site...\n")

    atualizados = []
    for p in produtos_site:
        sku = p.get('sku')
        nome = p.get('nome')
        saldo_site = p.get('estoque', 0)

        resultado_sql = consultar_saldo_empresa_2_por_nome(conn, nome)
        if resultado_sql:
            id_produto_sql, saldo_empresa2 = resultado_sql.ID_PRODUTO, int(resultado_sql.SALDO)
            if saldo_site == 0 and saldo_empresa2 > 0:
                # Atualiza estoque
                sucesso = atualizar_estoque_site(sku, saldo_empresa2)
                if sucesso:
                    atualizados.append({
                        "SKU": sku,
                        "Nome": nome,
                        "Saldo_antigo": saldo_site,
                        "Saldo_novo": saldo_empresa2
                    })

    # ----------------------------
    # Resultado final
    # ----------------------------
    if atualizados:
        print("\n📌 Produtos atualizados:")
        for p in atualizados:
            print(f"SKU: {p['SKU']} | Nome: {p['Nome']} | Saldo antigo: {p['Saldo_antigo']} → Saldo novo: {p['Saldo_novo']}")
    print(f"\n✅ Teste finalizado — {len(atualizados)} produtos atualizados com sucesso.")

    conn.close()

if __name__ == "__main__":
    main()
