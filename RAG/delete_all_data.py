from pymilvus import Collection, utility
from utils import connect_to_milvus

def delete_collection(collection_name):
    """
    Deletes the specified collection from the Milvus database.
    """
    connect_to_milvus()

    if utility.has_collection(collection_name):
        collection = Collection(collection_name)
        collection.drop()
        print(f"Collection '{collection_name}' has been deleted!")
    else:
        print(f"Collection '{collection_name}' does not exist.")


def main():
    # Ask the user to enter the collection name
    collection_name = input("Enter the name of the collection you want to delete: ")

    # Call the function to delete the specified collection
    delete_collection(collection_name)

if __name__ == "__main__":
    main()
