from google.cloud import bigquery

# Substitua pelo ID da sua tabela real
TABELA_ID = "vtal-inventariorede-prd.telegram_bot.tb_ref_foto_bot"

def salvar_inventario(dados, client):
    rows = [{
        "id_registro": dados.get('id_registro'),
        "user_id": int(dados.get('user_id', 123)),
        "idsap": dados.get('idsap'),
        "hostname": dados.get('hostname'),
        "fabricante": dados.get('fabricante'),
        "modelo": dados.get('modelo'),
        "funcao": dados.get('funcao'),
        "serial_number": dados.get('serial_number'),
        "gcs_url": dados.get('gcs_url'),
        "localizacao": "POINT(0 0)"
    }]
    errors = client.insert_rows_json(TABELA_ID, rows)
    if errors:
        raise Exception(f"Erro ao inserir: {errors}")

def atualizar_inventario(dados, client):
    query = f"""
        UPDATE `{TABELA_ID}`
        SET idsap = @idsap,
            hostname = @hostname,
            fabricante = @fabricante,
            modelo = @modelo,
            funcao = @funcao,
            serial_number = @serial_number
        WHERE id_registro = @id_registro
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("idsap", "STRING", dados.get('idsap')),
            bigquery.ScalarQueryParameter("hostname", "STRING", dados.get('hostname')),
            bigquery.ScalarQueryParameter("fabricante", "STRING", dados.get('fabricante')),
            bigquery.ScalarQueryParameter("modelo", "STRING", dados.get('modelo')),
            bigquery.ScalarQueryParameter("funcao", "STRING", dados.get('funcao')),
            bigquery.ScalarQueryParameter("serial_number", "STRING", dados.get('serial_number')),
            bigquery.ScalarQueryParameter("id_registro", "STRING", dados.get('id_registro')),
        ]
    )
    client.query(query, job_config=job_config).result()