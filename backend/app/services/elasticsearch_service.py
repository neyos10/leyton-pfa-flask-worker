import os

import pandas as pd
from elasticsearch import Elasticsearch, NotFoundError
from elasticsearch.helpers import bulk, scan


INDEX_NAME = "gics_codes"
TASKS_INDEX_NAME = "tasks_index"
MERGED_RESULTS_INDEX_NAME = "merged_results"
DEFAULT_ELASTICSEARCH_URL = "http://localhost:9200"

GICS_MAPPING = {
    "sub_industry_id": {"type": "keyword"},
    "sub_industry": {"type": "text"},
    "sub_industry_description": {"type": "text"},
    "industry_id": {"type": "keyword"},
    "industry": {"type": "text"},
    "industry_group_id": {"type": "keyword"},
    "industry_group": {"type": "text"},
    "sector_id": {"type": "keyword"},
    "sector": {"type": "text"},
}

TASKS_MAPPING = {
    "task_id": {"type": "keyword"},
    "file_location": {"type": "text"},
    "status": {"type": "keyword"},
    "created_at": {"type": "date"},
    "updated_at": {"type": "date"},
}

MERGED_RESULTS_MAPPING = {
    "merged_doc": {
        "type": "object",
        "dynamic": True,
    }
}

CSV_COLUMNS = {
    "SectorId": "sector_id",
    "Sector": "sector",
    "IndustryGroupId": "industry_group_id",
    "IndustryGroup": "industry_group",
    "IndustryId": "industry_id",
    "Industry": "industry",
    "SubIndustryId": "sub_industry_id",
    "SubIndustry": "sub_industry",
    "SubIndustryDescription": "sub_industry_description",
}


def get_es_client():
    elasticsearch_url = os.getenv("ELASTICSEARCH_URL", DEFAULT_ELASTICSEARCH_URL)
    return Elasticsearch(elasticsearch_url)


def create_index():
    es = get_es_client()

    if es.indices.exists(index=INDEX_NAME):
        return False

    es.indices.create(
        index=INDEX_NAME,
        mappings={"properties": GICS_MAPPING},
    )
    return True


def create_tasks_index():
    es = get_es_client()

    if es.indices.exists(index=TASKS_INDEX_NAME):
        return False

    es.indices.create(
        index=TASKS_INDEX_NAME,
        mappings={"properties": TASKS_MAPPING},
    )
    return True


def create_merged_results_index():
    es = get_es_client()

    if es.indices.exists(index=MERGED_RESULTS_INDEX_NAME):
        return False

    es.indices.create(
        index=MERGED_RESULTS_INDEX_NAME,
        mappings={"properties": MERGED_RESULTS_MAPPING},
    )
    return True


def _row_to_document(row):
    document = {
        target_field: str(row[source_column]).strip()
        for source_column, target_field in CSV_COLUMNS.items()
    }

    if not document["sub_industry_id"]:
        raise ValueError("sub_industry_id is required for every GICS row")

    return document


def _task_to_document(task):
    return {
        "task_id": str(task.id),
        "file_location": task.file_location,
        "status": task.status,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
    }


def ingest_gics_csv(csv_path):
    create_index()

    dataframe = pd.read_csv(csv_path, dtype=str).fillna("")
    missing_columns = set(CSV_COLUMNS) - set(dataframe.columns)

    if missing_columns:
        sorted_columns = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required GICS CSV columns: {sorted_columns}")

    actions = []

    for _, row in dataframe.iterrows():
        document = _row_to_document(row)
        actions.append(
            {
                "_op_type": "index",
                "_index": INDEX_NAME,
                "_id": document["sub_industry_id"],
                "_source": document,
            }
        )

    if not actions:
        return 0

    inserted_count, _ = bulk(get_es_client(), actions)
    return inserted_count


def index_task(task):
    create_tasks_index()

    document = _task_to_document(task)
    return get_es_client().index(
        index=TASKS_INDEX_NAME,
        id=str(task.id),
        document=document,
    )


def search_tasks_by_status(status):
    create_tasks_index()

    query = {
        "query": {
            "term": {
                "status": str(status).strip(),
            }
        }
    }

    return [
        hit["_source"]
        for hit in scan(
            get_es_client(),
            index=TASKS_INDEX_NAME,
            query=query,
        )
    ]


def index_merged_result(merged_doc, doc_id):
    create_merged_results_index()

    return get_es_client().index(
        index=MERGED_RESULTS_INDEX_NAME,
        id=str(doc_id),
        document={"merged_doc": merged_doc},
    )


def search_by_code(code):
    es = get_es_client()

    try:
        response = es.search(
            index=INDEX_NAME,
            query={"term": {"sub_industry_id": str(code).strip()}},
            size=1,
        )
    except NotFoundError:
        return None

    hits = response["hits"]["hits"]

    if not hits:
        return None

    return hits[0]["_source"]
