from dagster import resource, InitResourceContext
from pymongo import MongoClient

@resource(
    config_schema={
        "mongodb-host": str,
        "mongodb-port": int,
        "mongodb-username": str,
        "mongodb-password": str
    }
)
def mongodb_resource(context: InitResourceContext) -> MongoClient:
    """
    Connector để kết nối đến MongoDB.
    """
    cfg = context.resource_config
    client = MongoClient(
        host=cfg["mongodb-host"],
        port=cfg["mongodb-port"],
        username=cfg["mongodb-username"],
        password=cfg["mongodb-password"]
    )
    return client