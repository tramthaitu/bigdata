from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from fetch_crypto_info import crawl_coin_info

with DAG(
    dag_id="crypto_info_dag",
    description="DAG lấy dữ liệu crypto từ CoinMarketCap",
    schedule="* * * * *",
    start_date=datetime(2025, 4, 3),
    end_date=None,
    catchup=False
) as dag: 
    
    def extract():
        pass
    def transform():
        pass
    def load():
        pass

    extract_task = PythonOperator(
        task_id="extract",
        python_callable=extract
    )
    transform_task = PythonOperator(
        task_id="transform",
        python_callable=transform
    )
    load_task = PythonOperator(
        task_id="load",
        python_callable=load
    )
    
    extract_task >> transform_task >> load_task