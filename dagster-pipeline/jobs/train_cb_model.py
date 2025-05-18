from dagster import define_asset_job, AssetSelection

train_cb_model_job = define_asset_job(
    name="cb_model_group",
    selection=AssetSelection.groups("cb_model_group"),
    description="ETL job to process data from MongoDB to Spark DataFrame."
)