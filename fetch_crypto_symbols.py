import os
import requests
from dotenv import load_dotenv


def main():
    load_dotenv() # Load biến môi trường từ file .env
    API_KEY = os.getenv("API_KEY") # Lấy API key từ biến môi trường
    

    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    params = {"start": 1, "limit": 200, "convert": "USD", "sort": "market_cap", "sort_dir": "desc"}
    headers = {"Accepts": "application/json", "X-CMC_PRO_API_KEY": API_KEY}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        symbols = [coin["symbol"] for coin in response.json()["data"]]
        print("Symbols:", ", ".join(symbols))
        
        # Lưu symbols vào file
        with open("crypto_symbols.txt", "w") as f:
            f.write(",".join(symbols))
    else:
        print(f"Error: {response.status_code} - {response.text}")



if __name__ == "__main__":
    main()