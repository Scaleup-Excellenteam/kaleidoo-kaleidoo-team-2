from pymilvus import connections, Collection
from text_embedding import embed_text
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def connect_to_milvus_server():
    """
    Establishes a connection to the Milvus server using credentials from the environment variables.
    """
    public_endpoint = os.getenv('PUBLIC_ENDPOINT')
    token = os.getenv('TOKEN')
    
    connections.connect(
        alias="default", 
        uri=f"{public_endpoint}",  
        token=token  
    )
    print("Connected to Milvus Cloud!")

def search_embeddings(query):
    """
    Searches the Milvus collection for embeddings that are similar to the given query.
    
    Parameters:
    - query (str): Input query text to be embedded and searched.
    
    Returns:
    - A list of results with file paths and distances.
    """
    collection_name = "lecture_materials_embeddings"

    # Connect to Milvus and load the collection
    connect_to_milvus_server()
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
        output_fields=["file_path"]
    )

    # Display the search results
    print(f"Search results for query '{query}':")
    for hits in results:
        for hit in hits:
            print(f"File Path: {hit.entity.get('file_path')}, Distance: {hit.distance}")

if __name__ == "__main__":
    query = input("Enter the query text: ")
    try:
        search_embeddings(query)
    except Exception as e:
        print(f"Error during search: {e}")

# Optional: Check the number of records in the collection
collection = Collection("lecture_materials_embeddings")
print(f"Number of records in the collection: {collection.num_entities}")
