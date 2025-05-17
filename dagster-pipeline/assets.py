from dagster import asset, AssetExecutionContext, AssetKey
from typing import Any, List, Dict
from pymongo.collection import Collection
from pyspark.sql import SparkSession

@asset(required_resource_keys={"mongodb"})
def mongo_collection_asset(context: AssetExecutionContext) -> List[dict]:
    """
    1. Prepare sample data
    2. Drop existing collection (for idempotency)
    3. Insert new sample documents
    4. Return the list of inserted documents
    """
    coll: Collection = context.resources.mongodb
    sample_data = [
        {"name": "Alice", "age": 30, "city": "Paris"},
        {"name": "Bob", "age": 25, "city": "London"},
        {"name": "Charlie", "age": 35, "city": "New York"},
        {"name": "Diana", "age": 28, "city": "Berlin"},
    ]
    # Clear any existing data
    coll.drop()
    context.log.info("Dropped existing MongoDB collection.")

    # Insert sample docs
    result = coll.insert_many(sample_data)
    context.log.info(f"Inserted {len(result.inserted_ids)} documents into MongoDB.")

    return sample_data

@asset(
        required_resource_keys={"spark", "mongodb"},
        deps=[mongo_collection_asset]
)
def spark_data_asset(context: AssetExecutionContext) -> None:
    """
    1. Read back the data from MongoDB
    2. Create a Spark DataFrame and perform simple transformations
    3. Log/display results
    """
    spark: SparkSession = context.resources.spark

    # Re-query MongoDB
    cursor = context.resources.mongodb.find({})
    raw_data = list(cursor)

    if not raw_data:
        context.log.warn("No data found in MongoDB for Spark job.")
        return

    # Convert ObjectId -> str (hoặc pop '_id') để Spark có thể infer schema
    clean_data: List[Dict[str, Any]] = []
    for doc in raw_data:
        # Nếu không cần _id: doc.pop("_id", None)
        doc["_id"] = str(doc["_id"])
        clean_data.append(doc)

    # Tạo DataFrame
    df = spark.createDataFrame(clean_data)

    # Example transformations
    context.log.info("All records:")
    df.show(truncate=False)

    context.log.info("Filter age > 30:")
    df.filter(df.age > 30).show(truncate=False)

    context.log.info("Count by city for age > 30:")
    df.filter(df.age > 30).groupBy("city").count().show(truncate=False)