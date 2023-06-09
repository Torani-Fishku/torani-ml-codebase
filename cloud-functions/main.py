import requests
import pandas as pd
import numpy as np
from google.cloud import storage
from google.cloud import bigquery

def outlier_filter_zscore(df, column_name, threshold=3):
    z_scores = np.abs((df[column_name] - df[column_name].mean()) / df[column_name].std())
    filtered_df = df[z_scores <= threshold].copy()
    return filtered_df

def main(request):
    # Scrape the data from the web into a CSV file
    url = 'https://datacenterpds.id/priceList'
    json_data = requests.get(url).json()
    df = pd.json_normalize(json_data['data'])
    df['harga'] = df['harga'].str.replace(',', '').astype(int)
    df['tanggal_input'] = pd.to_datetime(df['tanggal_input'])

    df = df.loc[df['nama_pasar'] == 'PASAR IKAN MODERN MUARA BARU']
    df = df.loc[df['nama_ikan'].isin(['kembung\nlelaki', 'tongkol abu-\nabu', 'tenggiri', 'bandeng', 'tongkol\nkomo'])]
    df['nama_ikan'] = df['nama_ikan'].str.replace('\n', ' ')
    df.drop(['provinsi', 'kabupaten', 'nama_latin', 'nama_pasar'], axis=1, inplace=True)

    df = outlier_filter_zscore(df, 'harga', threshold=3)
    indexes = df[(df['harga'] < 10000)].index
    df.drop(indexes , inplace=True)

    df.sort_values('tanggal_input', inplace=True)
    df['tanggal_input'] = df['tanggal_input'].dt.date
    df = df.groupby(['tanggal_input', 'nama_ikan'])['harga'].median().reset_index()
    df['tanggal_input'] = pd.to_datetime(df['tanggal_input'])
    
    # Store the CSV file to a cloud bucket
    client = storage.Client()
    bucket_name = 'data-harga-stunning-prism-382306'
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob('data_harga_pds.csv')
    blob.upload_from_string(df.to_csv(index=False), 'text/csv')

    # Import the CSV file to a BigQuery database
    bq_client = bigquery.Client()
    dataset_id = 'data_harga'
    table_id = 'data-harga-table'
    dataset_ref = bq_client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_id)
    
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
        )
    
    load_job = bq_client.load_table_from_uri(
        f'gs://{bucket_name}/data_harga_pds.csv',
        table_ref,
        job_config=job_config
        )
    
    load_job.result()

    # Create a model in BigQuery
    model_query = """
        -- Create a BigQuery ML model for forecasting prices
        CREATE OR REPLACE MODEL data_harga.forecast_by_product
        OPTIONS(model_type='ARIMA_PLUS',
                time_series_timestamp_col='tanggal_input',
                time_series_data_col='harga',
                time_series_id_col='nama_ikan',
                auto_arima=True,
                data_frequency='AUTO_FREQUENCY',
                holiday_region='ID',
                decompose_time_series=True
                ) AS
        SELECT
          tanggal_input,
          harga,
          nama_ikan
        FROM `stunning-prism-382306.data_harga.data-harga-table`;
        """
    
    model_job = bq_client.query(model_query)
    
    model_job.result()

    # Store the forecasted data into a new CSV file
    forecast_query = """
        -- Create table for forecasted price
        CREATE OR REPLACE TABLE data_harga.outputdata_datastudio AS (
          SELECT
            tanggal_input AS timestamp,
            nama_ikan,
            harga AS history_value,
            NULL AS forecast_value,
            NULL AS prediction_interval_lower_bound,
            NULL AS prediction_interval_upper_bound
          FROM
            `stunning-prism-382306.data_harga.data-harga-table`
          UNION ALL
          SELECT
            EXTRACT(DATE
            FROM
              forecast_timestamp) AS timestamp,
            nama_ikan,
            NULL AS history_value,
            forecast_value,
            prediction_interval_lower_bound,
            prediction_interval_upper_bound
          FROM
            ML.FORECAST(MODEL data_harga.forecast_by_product,
              STRUCT(7 AS horizon, 0.8 AS confidence_level)) 
          ORDER BY timestamp
          )
        """
    
    forecast_job = bq_client.query(forecast_query)
    
    forecast_job.result()

    # Export the table to a CSV file in the cloud bucket
    destination_uri = f'gs://{bucket_name}/outputdata_datastudio.csv'
    dataset_ref = bq_client.dataset(dataset_id)
    table_ref = dataset_ref.table('outputdata_datastudio')
    
    extract_job = bq_client.extract_table(
        table_ref,
        destination_uri,
        location='US'
        )
    
    extract_job.result()

    return 'Data processed and saved successfully!'
