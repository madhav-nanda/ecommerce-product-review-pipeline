"""Bronze layer Mongo writer."""
from pymongo import MongoClient, UpdateOne


def upsert_bronze(mongo_uri: str, db_name: str, rows: list[dict], run_id: str) -> int:
    client = MongoClient(mongo_uri)
    coll = client[db_name]["flipkart_reviews_bronze"]
    ops = []
    for row in rows:
        doc = {**row, "ingestion_run_id": run_id}
        ops.append(UpdateOne({"review_id": row["review_id"]}, {"$set": doc}, upsert=True))
    if not ops:
        return 0
    result = coll.bulk_write(ops, ordered=False)
    return result.upserted_count + result.modified_count
