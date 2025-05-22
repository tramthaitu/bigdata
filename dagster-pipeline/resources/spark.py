from dagster import resource, InitResourceContext
from pyspark.sql import SparkSession

@resource(
    config_schema={
        "spark-app-name": str,
        "spark-master-host": str,
        "spark-master-port": int,
        "mongodb-host": str,
        "mongodb-port": int,
        "mongodb-username": str,
        "mongodb-password": str,
    }
)
def spark_resource(context: InitResourceContext):
    """
    Connector để khởi tạo SparkSession với cấu hình kết nối đến MongoDB.
    """
    cfg = context.resource_config

    spark_session = (
        SparkSession.builder
        .appName(cfg["spark-app-name"])
        .master(f"spark://{cfg['spark-master-host']}:{cfg['spark-master-port']}")
        .config(
            "spark.jars.packages",
            "org.mongodb.spark:mongo-spark-connector_2.12:10.5.0,"
            "org.postgresql:postgresql:42.5.0"
        )
        .config(
            "spark.mongodb.read.connection.uri",
            f"mongodb://{cfg['mongodb-username']}:{cfg['mongodb-password']}@"
            f"{cfg['mongodb-host']}:{cfg['mongodb-port']}/"
        )
        .config(
            "spark.mongodb.write.connection.uri",
            f"mongodb://{cfg['mongodb-username']}:{cfg['mongodb-password']}@"
            f"{cfg['mongodb-host']}:{cfg['mongodb-port']}/"
        )
        .getOrCreate()
    )

    return spark_session
