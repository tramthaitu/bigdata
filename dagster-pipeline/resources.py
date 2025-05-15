from dagster import resource, InitResourceContext
from pymongo import MongoClient

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