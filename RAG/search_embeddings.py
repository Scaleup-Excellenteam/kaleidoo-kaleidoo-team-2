from pymilvus import Collection
from text_embedding import embed_text
from utils import connect_to_milvus
import numpy as np

def create_index_on_embeddings(collection_name="hebrew_lecture_materials"):
    """
    Creates an index on the 'embedding' field in the specified Milvus collection.
    """
    collection = Collection(collection_name)
    index_params = {
        "metric_type": "L2",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 1024}
    }
    collection.create_index(field_name="embedding", index_params=index_params)
    print("Index created successfully!")


def search_embeddings(query, collection_name="hebrew_lecture_materials"):
    """
    Searches the Milvus collection for embeddings that are similar to the given query.
    """
    connect_to_milvus()
    collection = Collection(collection_name)
    
    # Ensure the collection has an index
    if not collection.has_index():
        print("No index found, creating one...")
        create_index_on_embeddings(collection_name)
    
    # Load the collection into memory for searching
    collection.load()

    # Convert query text into embeddings
    query_embedding = np.array(embed_text(query), dtype=np.float32).flatten()
    
    # Milvus expects the query to be a list of lists, so we wrap the query embedding
    query_embedding = [query_embedding]

    # Perform the search in Milvus
    search_params = {"metric_type": "L2", "params": {"nprobe": 10}}
    
    try:
        results = collection.search(
            data=query_embedding,  # Pass the embedding as a list of float arrays
            anns_field="embedding",
            param=search_params,
            limit=5,
            output_fields=["file_path", "text_content", "line_number"]  # Include line_number in output
        )
    
        # Fetch and return the file paths, text content, and line numbers
        retrieved_data = []
        for hits in results:
            for hit in hits:
                retrieved_data.append({
                    "file_path": hit.entity.get('file_path'),
                    "text_content": hit.entity.get('text_content'),
                    "line_number": hit.entity.get('line_number'),  # Retrieve the line number
                    "distance": hit.distance
                })
        return retrieved_data
    except Exception as e:
        print(f"Error during search: {e}")
        raise e
