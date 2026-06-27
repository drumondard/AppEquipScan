import uuid
from google.cloud import bigquery

def salvar_inventario(dados_bot: dict, bq_client) -> bool:
    table_id = "vtal-inventariorede-prd.telegram_bot.tb_ref_foto_bot"
    row = {
        "id_registro": str(uuid.uuid4()),
        "user_id": dados_bot.get('user_id', 0),
        "idsap": dados_bot.get('idsap', 'N/A'),
        "hostname": dados_bot.get('hostname', 'N/A'),
        "localizacao": "POINT(0 0)",
        **dados_bot.get('dados_ia', {}),
        "gcs_url": dados_bot.get('gcs_url', 'N/A')
    }
    errors = bq_client.insert_rows_json(table_id, [row])
    return not errors