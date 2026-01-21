import requests
import pyodbc
import time
from math import ceil

# =========================
# CONFIGURAÇÕES API
# =========================

HEADERS = {
    "accept": "application/json",
    "authorization": "Colocar aqui o token de autorização",
    "content-type": "application/json"
}

URL_LISTAR_PRODUTOS = "colcoar a url de listagem de produtos aqui"
URL_ATUALIZAR_PRODUTOS = "colcoar a url de atualização de produtos aqui"

LIMITE_POR_ENVIO = 50
DELAY_ENTRE_LOTES = 1

# =========================
# SKUs (ID_PRODUTO)
# =========================

SKUS_PARA_ATUALIZAR = [
    "37334",
    "44061",
    "44057",
    "44065",
    "44069",
    "44032",
    "43173"
]

# =========================
# CONFIGURAÇÕES SQL
# =========================

SQL_CONN_STR = (
    "DRIVER={SQL Server};"
    "SERVER=colocar o servidor;"
    "DATABASE=colocar a database;"
    "UID=colocar o usuário;"
    "PWD=colocar aqui a senha;" 
)

# =========================
# FUNÇÕES
# =========================

def conectar_sql():
    return pyodbc.connect(SQL_CONN_STR)


def buscar_produtos_site():
    produtos = []
    url = URL_LISTAR_PRODUTOS

    while url:
        r = requests.get(url, headers=HEADERS)
        data = r.json()
        produtos.extend(data.get("results", []))
        url = data.get("next")

    return produtos


def consultar_saldo(conn, id_produto):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT ISNULL(SUM(Saldo), 0)
        FROM VIEW_PRODUTOS_DW
        WHERE ID_PRODUTO = ?
    """, id_produto)

    return int(cursor.fetchone()[0])


def enviar_lote(lote):
    r = requests.post(URL_ATUALIZAR_PRODUTOS, json=lote, headers=HEADERS)
    return r.status_code in (200, 201)


# =========================
# MAIN
# =========================

def main():
    conn = conectar_sql()

    print("🔄 Buscando produtos do site...\n")

    produtos_site = buscar_produtos_site()

    produtos_filtrados = [
        p for p in produtos_site
        if str(p.get("sku")) in SKUS_PARA_ATUALIZAR
    ]

    print(f"🔍 SKUs encontrados no site: {len(produtos_filtrados)}\n")

    atualizar = []

    for p in produtos_filtrados:
        sku = str(p["sku"])
        estoque_site = int(p.get("estoque", 0))

        saldo_erp = consultar_saldo(conn, int(sku))

        print(
            f"SKU {sku} | Site: {estoque_site} | ERP: {saldo_erp}"
        )

        if saldo_erp != estoque_site:
            atualizar.append({
                "sku": sku,
                "estoque": saldo_erp
            })

    conn.close()

    if not atualizar:
        print("\n✅ Estoque já está sincronizado.")
        return

    print(f"\n🚀 Atualizando {len(atualizar)} produtos...\n")

    for i in range(0, len(atualizar), LIMITE_POR_ENVIO):
        lote = atualizar[i:i + LIMITE_POR_ENVIO]

        enviar_lote(lote)
        time.sleep(DELAY_ENTRE_LOTES)

    print(f"\n✅ Atualização finalizada com sucesso.")


if __name__ == "__main__":
    main()
