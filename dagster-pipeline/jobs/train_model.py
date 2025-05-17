from dagster import define_asset_job, AssetSelection

train_model_job = define_asset_job(
    name="train_model",
    selection=AssetSelection.groups("train_model_group"),
    description="ETL job to process data from MongoDB to Spark DataFrame."
)