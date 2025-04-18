from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
from src.crypto.fetch_crypto_info import crawl_and_save_coin_info
import pendulum
local_tz = pendulum.timezone("Asia/Ho_Chi_Minh")

with DAG(
    dag_id="crypto_info_dag",
    description="DAG lấy dữ liệu crypto từ CoinMarketCap",
    schedule="* * * * *",
    start_date=datetime(2025, 4, 19, 0, 0, 0, tzinfo=local_tz),
    catchup=False,
    is_paused_upon_creation=False
) as dag: 
    
    def extract():
        crawl_and_save_coin_info()
        print("Start extracting data")
    def transform():
        pass
    def load():
        pass

    extract_task = PythonOperator(
        task_id="extract",
        python_callable=extract
    )
    
    extract_task