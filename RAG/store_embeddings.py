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
        FieldSchema(name="text_content", dtype=DataType.VARCHAR, max_length=5000)
    ]
    schema = CollectionSchema(fields, description="Lecture materials embeddings collection")

    if not utility.has_collection(collection_name):
        collection = Collection(name=collection_name, schema=schema)
        print(f"Collection '{collection_name}' created successfully!")
    else:
        collection = Collection(name=collection_name)
        print(f"Collection '{collection_name}' already exists.")
    
    return collection

def store_data_in_milvus(collection_name, texts, file_paths):
    """
    Stores text embeddings, raw text content, and file paths in Milvus.
    """
    connect_to_milvus()
    collection = create_milvus_collection(collection_name)
    
    # Convert texts to embeddings and ensure they are in the correct format (NumPy float32 arrays)
    embeddings = [np.array(embed_text(text), dtype=np.float32).flatten() for text in texts]
    
    # Insert embeddings, file paths, and text content into Milvus
    collection.insert([embeddings, file_paths, texts])
    print(f"Inserted {len(embeddings)} records into the collection '{collection_name}'.")
    collection.flush()
    print("Data flushed successfully!")
    
    # Create index for efficient search
    create_index_on_embeddings(collection_name)
    
    print(f"Total number of records in the collection '{collection_name}': {collection.num_entities}")


def create_index_on_embeddings(collection_name):
    """
    Creates an index on the 'embedding' field in the specified Milvus collection.
    """
    collection = Collection(collection_name)
    
    index_params = {
        "metric_type": "L2",
        "index_type": "IVF_FLAT",
        "params": {"nlist": 128}
    }
    
    print(f"Creating index on 'embedding' field in collection '{collection_name}'...")
    collection.create_index(field_name="embedding", index_params=index_params)
    print("Index created successfully!")

def main():

    hebrew_text_1 = [
        "הנדסת חשמל היא תחום מדעי והנדסי המתמקד בלימוד ייצור, הולכה, ושימוש בחשמל.",
        "מהנדסי חשמל עוסקים בתכנון מערכות חשמליות, פיתוח רכיבים אלקטרוניים, תכנון מערכות תקשורת.",
        "תחום זה כולל את יישום חוקי הפיזיקה והמתמטיקה במערכות אלקטרומגנטיות ואנרגיה.",
        "הנדסת חשמל מהווה בסיס לפיתוחים טכנולוגיים בתחומים כמו תקשורת סלולרית, מחשבים, ורובוטיקה."
    ]

    file_path_1 = [
        "/path/to/file1.pdf",
        "/path/to/file1.pdf",
        "/path/to/file1.pdf",
        "/path/to/file1.pdf"
    ]

    hebrew_text_2 = [
        "מדעי המחשב הם תחום מחקר העוסק בתיאוריה וביישום של מערכות מחשוב.",
        "התחום כולל תיאוריה של אלגוריתמים, מדעי הנתונים, עיבוד תמונה, ניתוח נתונים, פיתוח מערכות הפעלה, ועיצוב רשתות מחשבים.",
        "מדעי המחשב עוסקים גם בפיתוח טכנולוגיות חדשות שנמצאות בבסיס מערכות המידע המודרניות.",
        "התחום דורש ידע מתמטי נרחב ויכולת לפתח פתרונות לבעיות מורכבות בתחום התוכנה והחומרה."
    ]

    file_path_2 = [
        "/path/to/file2.pdf",
        "/path/to/file2.pdf",
        "/path/to/file2.pdf",
        "/path/to/file2.pdf"
    ]
    
    # Name of the Milvus collection
    collection_name = "hebrew_lecture_materials"

    # Store the embeddings, file paths, and text content in Milvus
    store_data_in_milvus(collection_name, hebrew_text_1, file_path_1)
    store_data_in_milvus(collection_name, hebrew_text_2, file_path_2)


if __name__ == "__main__":
    main()
