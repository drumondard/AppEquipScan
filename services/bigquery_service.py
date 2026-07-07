from google.cloud import bigquery

client = bigquery.Client()
TABELA_ID = "vtal-inventariorede-prd.telegram_bot.tb_ref_foto_bot"

def buscar_equipamentos_por_modelo_e_local(modelo: str, uf: str, estacao: str):
    modelo_limpo = "".join(filter(str.isalnum, modelo.upper()))
    localizacao_param = f"{uf.upper()}-{estacao.upper()}"
    query = """
        SELECT equipamento, hostname, modelo, fabricante, num_serie, funcao, tipo_item
        FROM `vtal-inventariorede-prd.sap_trusted.vw_eam_ih08_unificada`
        WHERE (
            UPPER(REGEXP_REPLACE(modelo, r'[^A-Z0-9]', '')) LIKE CONCAT('%', UPPER(REGEXP_REPLACE(@modelo, r'[^A-Z0-9]', '')), '%')
            OR
            UPPER(REGEXP_REPLACE(@modelo, r'[^A-Z0-9]', '')) LIKE CONCAT('%', UPPER(REGEXP_REPLACE(modelo, r'[^A-Z0-9]', '')), '%')        
        )
        AND (
            CONCAT(
                SPLIT(REGEXP_REPLACE(local_instalacao, r'^I-BR-', ''), '-')[SAFE_OFFSET(0)], '-',
                SPLIT(REGEXP_REPLACE(local_instalacao, r'^I-BR-', ''), '-')[SAFE_OFFSET(2)]
            ) = @localizacao
        )
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("modelo", "STRING", modelo_limpo),
            bigquery.ScalarQueryParameter("localizacao", "STRING", localizacao_param)
        ]
    )
    query_job = client.query(query, job_config=job_config)
    return [dict(row) for row in query_job]

def salvar_inventario(dados):
    rows = [{
        "id_registro": dados.get('id_registro'),
        "user_id": int(dados.get('user_id', 123)),
        "idsap": dados.get('idsap'),
        "tipo_item": dados.get('tipo_item'),
        "hostname": dados.get('hostname'),
        "fabricante": dados.get('fabricante'),
        "modelo": dados.get('modelo'),
        "funcao": dados.get('funcao'),
        "serial_number": dados.get('serial_number'),
        "gcs_url": dados.get('gcs_url'),
        "uf": dados.get('uf'),
        "est": dados.get('estacao'),
        "localizacao": "POINT(0 0)"
    }]
    errors = client.insert_rows_json(TABELA_ID, rows)
    if errors:
        raise Exception(f"Erro ao inserir: {errors}")

def atualizar_inventario(dados):
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
