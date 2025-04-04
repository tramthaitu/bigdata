import os
from dotenv import load_dotenv
load_dotenv()

# Lấy API key từ biến môi trường
CMC_API_KEY = os.getenv("CMC_API_KEY")

# Đọc danh sách symbols từ file một lần
with open("crypto_symbols.txt", "r") as f:
    CRYPTO_SYMBOLS = f.read().strip()

# Chuyển thành list cho dễ sử dụng
CRYPTO_SYMBOLS_LIST = CRYPTO_SYMBOLS.split(",")

# Giới hạn số lượng symbols (CoinMarketCap giới hạn 200 symbols mỗi lần gọi API)
CRYPTO_SYMBOLS_LIST = ",".join(CRYPTO_SYMBOLS_LIST[:200])