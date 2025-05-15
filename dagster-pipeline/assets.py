from dagster import asset, AssetExecutionContext
from typing import Any, List

@asset(required_resource_keys={"mongodb"})
def mongo_collection_asset(context: AssetExecutionContext) -> List[Any]:
    coll = context.resources.mongodb
    cursor = coll.find({})
    data = list(cursor)
    return data