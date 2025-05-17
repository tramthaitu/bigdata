from dagster import resource, InitResourceContext
from pymongo import MongoClient
from pyspark.sql import SparkSession

@resource(
    config_schema={
        "host": str,
        "port": int,
        "username": str,
        "password": str,
        "database": str,
        "collection_name": str
    }
)
def mongodb_resource(context: InitResourceContext):
    cfg = context.resource_config
    client = MongoClient(
        host=cfg["host"],
        port=cfg["port"],
        username=cfg["username"],
        password=cfg["password"]
    )
    db = client[cfg["database"]]
    coll = db[cfg["collection_name"]]
    return coll

@resource(
    config_schema={
        "app_name": str,
        "host": str,
        "port": int,
    }
)
def spark_resource(context: InitResourceContext):
    cfg = context.resource_config
    spark_session = SparkSession.builder \
        .appName(cfg["app_name"]) \
        .master(f"spark://{cfg['host']}:{cfg['port']}") \
        .getOrCreate()
    return spark_session