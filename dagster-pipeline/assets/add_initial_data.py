import pandas as pd
from dagster import asset, AssetExecutionContext
from pymongo import MongoClient

def add_inittial_data_from_csv(
    connector: MongoClient, 
    database: str, 
    collection: str,
    path_to_csv: str,
    chunksize: int = 10000
) -> None:
    # Kết nối đến MongoDB Collection
    mongodb_client: MongoClient = connector
    db = mongodb_client[database]
    coll = db[collection]

    # Đọc file theo từng chunk (batch)
    for chunk in pd.read_csv(filepath_or_buffer=path_to_csv, chunksize=chunksize):
        data = chunk.to_dict(orient="records")
        coll.insert_many(data)

@asset(required_resource_keys={"mongodb"})
def add_initial_books_details(context: AssetExecutionContext):
    """
    Tải thông tin về những cuốn sách 
    Lưu ý: chỉ cập nhật khi nhập sách mới - thủ công hoặc dùng external trigger
    """
    
    add_inittial_data_from_csv(
        connector=context.resources.mongodb,
        database="books_db",
        collection="books_details",
        path_to_csv="/opt/dagster/app/initial_books_data/books_data.csv",
        chunksize=10000
    )
    return "Data loaded successfully into MongoDB collection."

@asset(
    required_resource_keys={"mongodb"},
    deps=["add_initial_books_details"]
)
def add_initial_books_reviews(context: AssetExecutionContext):
    """
    Tải thông tin về những lượt review sách
    Lưu ý: 
        - Dữ liệu này đúng ra là được cập nhật vào mongodb mỗi khi có review mới.
        - Tuy nhiên, để phục vụ việc demo, ta sẽ tải lại toàn bộ dữ liệu này từ file CSV.
    """

    add_inittial_data_from_csv(
        connector=context.resources.mongodb,
        database="books_db",
        collection="books_reviews",
        path_to_csv="/opt/dagster/app/initial_books_data/books_rating.csv",
        chunksize=10000
    )
    return "Data loaded successfully into MongoDB collection."