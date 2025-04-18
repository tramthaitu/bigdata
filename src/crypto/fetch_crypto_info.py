from pymongo import MongoClient
from datetime import datetime
from bson import Decimal128
import requests
import logging
from src.utils.config import CMC_API_KEY, CRYPTO_SYMBOLS_LIST

def crawl_and_save_coin_info():
    url = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
    params = {"id": CRYPTO_SYMBOLS_LIST, "convert": "USD"}
    headers = {"Accepts": "application/json", "X-CMC_PRO_API_KEY": CMC_API_KEY}
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        crypto_data = data["data"]
        
        client = MongoClient("mongodb://mongodb:mongodb@mongodb:27017/?authSource=admin")
        db = client["crypto_db"]
        collection = db["crypto_history"]
        
        documents_to_insert = []
        timestamp = datetime.now().isoformat()
        
        for crypto_id, crypto_info in crypto_data.items():
            # Thêm timestamp
            crypto_info["collected_at"] = timestamp
            
            # Hàm để kiểm tra và chuyển đổi số lớn trong dictionary
            def convert_large_numbers(data):
                if isinstance(data, dict):
                    for key, value in data.items():
                        if isinstance(value, int) and abs(value) > 2**63 - 1:
                            data[key] = str(value)  # Chuyển thành chuỗi
                            logging.info(f"Converted {key}={value} to string")
                        elif isinstance(value, dict):
                            convert_large_numbers(value)  # Đệ quy cho dictionary lồng nhau
                        elif isinstance(value, list):
                            for i, item in enumerate(value):
                                if isinstance(item, dict):
                                    convert_large_numbers(item)
                                elif isinstance(item, int) and abs(item) > 2**63 - 1:
                                    value[i] = str(item)
                                    logging.info(f"Converted list item {key}[{i}]={item} to string")
            
            # Áp dụng kiểm tra cho toàn bộ crypto_info
            convert_large_numbers(crypto_info)
            
            # Fix platform nếu là chuỗi "None"
            if crypto_info.get("platform") == "None":
                crypto_info["platform"] = None
            
            documents_to_insert.append(crypto_info)
            logging.info(f"Prepared data for: {crypto_info['name']} ({crypto_info['symbol']})")
        
        if documents_to_insert:
            try:
                result = collection.insert_many(documents_to_insert)
                logging.info(f"✅ Inserted {len(result.inserted_ids)} documents.")
            except Exception as e:
                logging.error(f"Lỗi khi chèn dữ liệu: {e}")
                raise
    
    else:
        logging.error(f"❌ API Error: {response.status_code}")
        logging.error(response.text)
        raise Exception(f"API Error: {response.status_code}")

if __name__ == "__main__":
    crawl_and_save_coin_info()