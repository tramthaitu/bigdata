from dagster import define_asset_job, AssetSelection

train_als_model_job = define_asset_job(
    name="als_model_group",
    selection=AssetSelection.groups("als_model_group"),
    description="ETL job to process data from MongoDB to Spark DataFrame."
)