from pymilvus import Collection
from text_embedding import embed_text
from utils import connect_to_milvus

def search_embeddings(query, collection_name="hebrew_lecture_materials"):
    """
    Searches the Milvus collection for embeddings that are similar to the given query.
    """
    connect_to_milvus()
    collection = Collection(collection_name)
    collection.load()

    # Convert query text into embeddings
    query_embedding = embed_text(query)

    # Perform the search in Milvus
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    results = collection.search(
        data=query_embedding,
        anns_field="embedding",
        param=search_params,
        limit=5,
        output_fields=["file_path", "text_content"]
    )

    # Fetch and return the file paths and text content
    retrieved_data = []
    for hits in results:
        for hit in hits:
            retrieved_data.append({
                "file_path": hit.entity.get('file_path'),
                "text_content": hit.entity.get('text_content'),
                "distance": hit.distance
            })
    
    return retrieved_data
