from dagster import Definitions
from resources import mongodb_resource
from assets import mongo_collection_asset

defs = Definitions(
    assets=[mongo_collection_asset],
    resources={
        "mongodb": mongodb_resource.configured(
            {
                "host": "mongodb",
                "port": 27017,
                "username": "mongo_user",
                "password": "mongo_password",
                "database": "testdb",
                "collection_name": "users"
            }
        )
    }
)