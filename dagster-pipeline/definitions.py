from dagster import Definitions, load_assets_from_modules
from assets import add_initial_data, train_model
from resources import mongodb_resource, spark_resource
from jobs import train_model_job
from schedules import train_model_schedule

add_initial_data_assets = load_assets_from_modules([add_initial_data], group_name="initial_data_group")
train_model_assets = load_assets_from_modules([train_model], group_name="train_model_group")

defs = Definitions(
    assets=[*add_initial_data_assets, *train_model_assets],
    jobs=[train_model_job],
    schedules=[train_model_schedule],
    resources={
        "mongodb": mongodb_resource.configured(
            {
                "mongodb-host": "mongodb",
                "mongodb-port": 27017,
                "mongodb-username": "mongo_user",
                "mongodb-password": "mongo_password"
            }
        ),
        "spark": spark_resource.configured(
            {
                "spark-app-name": "MongoSparkApp",
                "spark-master-host": "spark-master",
                "spark-master-port": 7077,
                "mongodb-host": "mongodb",
                "mongodb-port": 27017,
                "mongodb-username": "mongo_user",
                "mongodb-password": "mongo_password"
            }
        )
    }
)
