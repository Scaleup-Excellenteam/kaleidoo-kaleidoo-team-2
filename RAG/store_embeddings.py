from pymilvus import FieldSchema, CollectionSchema, DataType, Collection, utility
from text_embedding import embed_text
from utils import connect_to_milvus
import numpy as np

def create_milvus_collection(collection_name):
    """
    Creates a Milvus collection with the schema if it doesn't exist.
    """
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
        FieldSchema(name="file_path", dtype=DataType.VARCHAR, max_length=500),
        FieldSchema(name="text_content", dtype=DataType.VARCHAR, max_length=5000),
        FieldSchema(name="line_number", dtype=DataType.INT64)  # Add line_number field
    ]
    schema = CollectionSchema(fields, description="Lecture materials embeddings collection")

    if not utility.has_collection(collection_name):
        collection = Collection(name=collection_name, schema=schema)
        print(f"Collection '{collection_name}' created successfully!")
    else:
        collection = Collection(name=collection_name)
        print(f"Collection '{collection_name}' already exists.")
    
    return collection

def store_data_in_milvus_list(collection_name, texts, file_paths):
    """
    Stores a list of text embeddings, raw text content, file paths, and line numbers in Milvus.
    """
    connect_to_milvus()
    collection = create_milvus_collection(collection_name)
    
    # Convert texts to embeddings
    embeddings = [np.array(embed_text(text), dtype=np.float32).flatten() for text in texts]

    # Extract the file paths and line numbers from the tuples
    file_paths_only = [fp[1] for fp in file_paths]  # Access the file path part of the tuple, as strings
    line_numbers = [fp[0] for fp in file_paths]  # Extract the line numbers
    
    # Ensure data alignment
    if len(embeddings) != len(file_paths_only) or len(embeddings) != len(texts) or len(embeddings) != len(line_numbers):
        raise ValueError("Mismatch in the number of embeddings, file paths, texts, or line numbers.")
    
    # Prepare data for insertion
    data_to_insert = [
        embeddings,       # embeddings (list of lists)
        file_paths_only,  # file paths as strings
        texts,            # text content (list of strings)
        line_numbers      # line numbers
    ]
    
    collection.insert(data_to_insert)
    print(f"Inserted {len(embeddings)} records into the collection '{collection_name}'.")
    collection.flush()
    print("Data flushed successfully!")

def store_data_in_milvus_one(collection_name, text, line_number, file_path):
    """
    Stores a single text embedding, raw text content, file path, and line number in Milvus.
    """
    connect_to_milvus()
    collection = create_milvus_collection(collection_name)
    
    # Convert text to embedding
    embedding = np.array(embed_text(text), dtype=np.float32).flatten()

    # Prepare data for insertion (single record)
    data_to_insert = [
        [embedding],    # embeddings as a list of one list
        [file_path],    # file_path as a string
        [text],         # text as a string
        [line_number]   # line_number as an integer
    ]
    
    collection.insert(data_to_insert)
    print(f"Inserted 1 record into the collection '{collection_name}' (Line number: {line_number}, File path: {file_path}).")
    collection.flush()
    print("Data flushed successfully!")

def create_index_on_embeddings(collection_name):
    """
    Creates an index on the 'embedding' field in the specified Milvus collection.
    """
    collection = Collection(collection_name)
    
    index_params = {
        "metric_type": "L2",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 1024}
    }
    
    print(f"Creating index on 'embedding' field in collection '{collection_name}'...")
    collection.create_index(field_name="embedding", index_params=index_params)
    print("Index created successfully!")

# Example of how you can use the functions
def main():
    hebrew_texts = [
        "דאדא או דאדאיזם הוא זרם מחאה באמנות שנוסד בציריך ב-1916, ופעל עד שנת 1923",
        "מרכזי פעילות נוספים של תנועת דאדא היו בברלין, בהנובר, בפריז, בקלן ובניו יורק.",
        "המניע לייסוד תנועת דאדא בציריך היה הזעזוע מזוועות מלחמת העולם הראשונה ומתוצאותיה",
        "בעיני בני התקופה הייתה הטכנולוגיה עתידה להביא לשינוי ולעתיד טוב יותר לאנושות, אך במקום זאת היא הביאה להרס ולאכזבה גדולה שבאו בעקבות המלחמה וזוועותיה"
    ]

    file_paths = [
        (1, "file01"),  # Line number 1
        (2, "file01"),  # Line number 2
        (3, "file01"),  # Line number 3
        (4, "file01")   # Line number 4
    ]

    collection_name = "hebrew_lecture_materials"

    # Store the list of embeddings with line numbers
    store_data_in_milvus_list(collection_name, hebrew_texts, file_paths)

    # Store a single embedding
    single_text = "חברי הדאדא ביטאו את מחשבותיהם נגד המלחמה, כנגד הבורגנות וכנגד האמנות המסורתית"
    store_data_in_milvus_one(collection_name, single_text, 5, "file01")

    collection = Collection(collection_name)
    print(f"Total number of records in the collection '{collection_name}': {collection.num_entities}")

if __name__ == "__main__":
    main()
