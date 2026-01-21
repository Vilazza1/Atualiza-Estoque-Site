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

def conectar_sql_server():
    return pyodbc.connect(SQL_CONN_STR)

def buscar_produtos_site():
    produtos = []
    url = URL_LISTAR_PRODUTOS

    while url:
        r = requests.get(url, headers=HEADERS)
        if r.status_code != 200:
            raise Exception(f"Erro ao listar produtos: {r.status_code} - {r.text}")

        data = r.json()
        produtos.extend(data.get("results", []))
        url = data.get("next")

    return produtos

def consultar_saldo_empresa_2(conn, nome):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM(SALDO)
        FROM BL_MASTER.dbo.VIEW_PRODUTOS_DW
        WHERE ID_EMPRESA = 1
          AND CONVERT(NVARCHAR(MAX), NM_ORIGINAL) LIKE ?
    """, ('%' + nome + '%',))

    row = cursor.fetchone()
    return int(row[0]) if row and row[0] else 0

def enviar_lote(produtos):
    r = requests.post(
        URL_ATUALIZAR_PRODUTOS,
        json=produtos,
        headers=HEADERS
    )

    if r.status_code in (200, 201):
        return True
    else:
        print(f"❌ Erro {r.status_code}: {r.text}")
        return False

# =========================
# MAIN
# =========================

def main():
    conn = conectar_sql_server()
    produtos_site = buscar_produtos_site()

    print(f"🔍 Verificando {len(produtos_site)} produtos do site...\n")

    produtos_para_atualizar = []

    for p in produtos_site:
        sku = p["sku"]
        nome = p["nome"]
        saldo_site = int(p.get("estoque", 0))

        if saldo_site > 0:
            continue

        saldo_empresa_2 = consultar_saldo_empresa_2(conn, nome)

        if saldo_empresa_2 > 0:
            produtos_para_atualizar.append({
                "sku": sku,
                "estoque": saldo_empresa_2,
                "nome": nome
            })

    conn.close() 
    if not produtos_para_atualizar:
        print("✅ Nenhum produto precisou ser atualizado.")
        return

    print(f"🧮 Produtos a atualizar: {len(produtos_para_atualizar)}\n")

    for p in produtos_para_atualizar:
        print(f"SKU {p['sku']} | {p['nome']} | 0 → {p['estoque']}")

    total_lotes = ceil(len(produtos_para_atualizar) / LIMITE_POR_ENVIO)
    atualizados = []

    print("\n🚀 Iniciando atualização...\n")

    for i in range(total_lotes):
        inicio = i * LIMITE_POR_ENVIO
        fim = inicio + LIMITE_POR_ENVIO

        lote = [
            {"sku": p["sku"], "estoque": p["estoque"]}
            for p in produtos_para_atualizar[inicio:fim]
        ]

        print(f"➡️ Enviando lote {i+1}/{total_lotes} ({len(lote)} produtos)")

        if enviar_lote(lote):
            atualizados.extend(lote)
            print("✅ Lote enviado com sucesso\n")
        else:
            print("❌ Falha no envio do lote\n")

        time.sleep(DELAY_ENTRE_LOTES)

    print("===================================")
    print("📌 Produtos atualizados:")
    for p in atualizados:
        print(f"SKU {p['sku']} → {p['estoque']}")
    print("===================================")

    print(f"\n✅ Atualização finalizada — {len(atualizados)} produtos atualizados com sucesso.")

if __name__ == "__main__":
    main()
