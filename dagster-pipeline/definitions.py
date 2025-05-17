from dagster import Definitions
from resources import mongodb_resource, spark_resource
from assets import mongo_collection_asset, spark_data_asset

defs = Definitions(
    assets=[mongo_collection_asset, spark_data_asset],
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
        ),
        "spark": spark_resource.configured(
            {
                "app_name": "MongoSparkApp",
                "host": "spark-master",
                "port": 7077
            }
        )
    }
)