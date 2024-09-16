from pymilvus import connections, Collection, utility
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

def delete_collection(collection_name):
    """
    Deletes the specified collection from the Milvus database.
    
    Parameters:
    - collection_name (str): The name of the collection to delete.
    """
    connect_to_milvus_server()

    # Check if the collection exists
    if utility.has_collection(collection_name):
        # Load the collection
        collection = Collection(collection_name)
        
        # Drop the collection (this deletes it permanently)
        collection.drop()
        print(f"Collection '{collection_name}' has been deleted!")
    else:
        print(f"Collection '{collection_name}' does not exist.")

if __name__ == "__main__":
    try:
        # Get collection name from user input
        collection_name = input("Enter the collection name to delete: ").strip()
        delete_collection(collection_name)
    except Exception as e:
        print(f"Error deleting the collection: {e}")
