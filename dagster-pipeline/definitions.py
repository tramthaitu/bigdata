from dagster import Definitions, load_assets_from_modules
from assets import add_initial_data, als_model, cb_model
from resources import mongodb_resource, spark_resource
from jobs import train_als_model_job, train_cb_model_job
from schedules import train_als_model_schedule, train_cb_model_schedule

add_initial_data_assets = load_assets_from_modules([add_initial_data], group_name="initial_data_group")
als_model_assets = load_assets_from_modules([als_model], group_name="als_model_group")
cb_model_assets = load_assets_from_modules([cb_model], group_name="cb_model_group")

defs = Definitions(
    assets=[*add_initial_data_assets, *als_model_assets, *cb_model_assets],
    jobs=[train_als_model_job, train_cb_model_job],
    schedules=[train_als_model_schedule, train_cb_model_schedule],
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
