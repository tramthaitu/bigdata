import requests, pandas
from config import CMC_API_KEY, CRYPTO_SYMBOLS_LIST

def crawl_coin_info():

    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    params = {"symbol": CRYPTO_SYMBOLS_LIST, "convert": "USD"}
    headers = {"Accepts": "application/json", "X-CMC_PRO_API_KEY": CMC_API_KEY}
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        
        # Chuẩn bị list để lưu dữ liệu
        crypto_data = []
        
        for symbol in data["data"]:
            coin = data["data"][symbol]
            
            # Trích xuất các thông tin cần thiết
            coin_data = {
                'id': coin['id'],
                'name': coin['name'],
                'symbol': coin['symbol'],
                'slug': coin['slug'],
                'cmc_rank': coin['cmc_rank'],
                'max_supply': coin['max_supply'],
                'circulating_supply': coin['circulating_supply'],
                'total_supply': coin['total_supply'],
                'date_added': coin['date_added'],
                'last_updated': coin['last_updated'],
                'price': coin['quote']['USD']['price'],
                'volume_24h': coin['quote']['USD']['volume_24h'],
                'percent_change_1h': coin['quote']['USD']['percent_change_1h'],
                'percent_change_24h': coin['quote']['USD']['percent_change_24h'],
                'percent_change_7d': coin['quote']['USD']['percent_change_7d'],
                'percent_change_30d': coin['quote']['USD']['percent_change_30d'],
                'percent_change_60d': coin['quote']['USD']['percent_change_60d'],
                'percent_change_90d': coin['quote']['USD']['percent_change_90d'],
                'market_cap': coin['quote']['USD']['market_cap'],
                'market_cap_dominance': coin['quote']['USD']['market_cap_dominance'],
                'fully_diluted_market_cap': coin['quote']['USD']['fully_diluted_market_cap'],
                'tags': ','.join(coin['tags']) if coin['tags'] else ''
            }
            
            crypto_data.append(coin_data)
        
        # Tạo DataFrame từ dữ liệu
        df = pandas.DataFrame(crypto_data)
        
        # Sắp xếp theo thứ hạng CMC
        df = df.sort_values('cmc_rank')
        
        # Hiển thị thông tin
        print(f"Đã lấy dữ liệu của {len(df)} đồng tiền điện tử")
        print(df.head())
        
        # Lưu DataFrame vào file CSV
        df.to_csv('crypto_data.csv', index=False)
        print("Đã lưu dữ liệu vào file crypto_data.csv")
        
        return df
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None