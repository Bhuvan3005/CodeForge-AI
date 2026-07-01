from typing import Any, Dict, List, Optional


def normalize_mongo_doc(
    doc: Optional[Dict[str, Any]],
    id_field: str = "id",
) -> Optional[Dict[str, Any]]:
    """Map MongoDB ``_id`` to a string API field and remove the raw ObjectId."""
    if not doc:
        return doc

    if "_id" in doc:
        doc[id_field] = str(doc["_id"])
        del doc["_id"]

    return doc


def normalize_mongo_docs(
    docs: List[Dict[str, Any]],
    id_field: str = "id",
) -> List[Dict[str, Any]]:
    return [normalize_mongo_doc(doc, id_field) for doc in docs]
