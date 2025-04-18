import requests
from src.utils.config import CMC_API_KEY


def main():    
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    params = {"start": 1, "limit": 200, "convert": "USD", "sort": "market_cap", "sort_dir": "desc"}
    headers = {"Accepts": "application/json", "X-CMC_PRO_API_KEY": CMC_API_KEY}
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        symbols = [str(coin["id"]) for coin in response.json()["data"]]
        
        # Lưu symbols vào file
        with open("src/crypto/crypto_symbols_id.txt", "w") as f:
            f.write(",".join(symbols))
    else:
        print(f"Error: {response.status_code} - {response.text}")


if __name__ == "__main__":
    main()