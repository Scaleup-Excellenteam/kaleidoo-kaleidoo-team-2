import os
from typing import List, Dict, Any
from pymilvus import connections, Collection, CollectionSchema, FieldSchema, DataType
from pymilvus.orm import utility
from tqdm import tqdm

from embedding_module import EmbeddingModule

class MilvusDB:
    def __init__(self, host: str = "localhost", port: str = "19530"):
        self.host = host
        self.port = port
        self.connect()
        self.collections = {
            "document": "rag_document_collection",
            "audio": "rag_audio_collection",
            "image": "rag_image_collection",
        }

        self.embedder = EmbeddingModule()

        self.embedding_dim = self.get_embedding_dim()

    def connect(self):
        connections.connect("default", host=self.host, port=self.port)

    def disconnect(self):
        connections.disconnect("default")

    def get_embedding_dim(self) -> int:
        sample_text = "This is a sample text to get embedding dimension."
        embedding = self.embedder.get_embedding(sample_text, model='bgem3')
        return len(embedding)

    def create_collection(self, name: str):
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name="file", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=self.embedding_dim),
            FieldSchema(name="metadata", dtype=DataType.JSON)
        ]
        schema = CollectionSchema(fields, f"{name} embeddings")
        collection = Collection(name=name, schema=schema)
        index_params = {
            "metric_type": "L2",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
        collection.create_index(field_name="embedding", index_params=index_params)
        return collection

    def insert(self, data: List[Dict[str, Any]]):
        for item in data:
            collection_name = self.collections[item['type']]
            collection = Collection(name=collection_name)

            embedding = self.embedder.get_embedding(item['text'], model='bgem3')

            if len(embedding) != self.embedding_dim:
                raise ValueError(f"Embedding dimension mismatch. Expected {self.embedding_dim}, got {len(embedding)}")

            # Extract metadata (all fields except 'type', 'file', and 'text')
            metadata = {k: v for k, v in item.items() if k not in ['type', 'file', 'text']}

            document = {
                "file": item['file'],
                "embedding": embedding.tolist(),
                "metadata": metadata
            }

            collection.insert([document])

    def similarity_search(self, query_text: str, top_k: int = 5):
        query_embedding = self.embedder.get_embedding(query_text, model='bgem3')
        all_results = []

        for collection_name in self.collections.values():
            collection = Collection(name=collection_name)
            collection.load()

            results = collection.search(
                data=[query_embedding.tolist()],
                anns_field="embedding",
                param={"metric_type": "L2", "params": {"nprobe": 10}},
                limit=top_k,
                output_fields=["file", "metadata"]
            )

            for hit in results[0]:
                all_results.append({
                    "collection": collection_name,
                    "file": hit.entity.get('file'),
                    "metadata": hit.entity.get('metadata'),
                    "distance": hit.distance
                })

            collection.release()

        all_results.sort(key=lambda x: x['distance'])

        return all_results[:top_k]

    def remove_all_collections(self):
        existing_collections = utility.list_collections()
        for collection_name in existing_collections:
            utility.drop_collection(collection_name)

    def list_collections(self):
        return connections.list_collections()

# Example usage
if __name__ == "__main__":
    def load_moby_dick(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return [line.strip() for line in file if line.strip()]

    moby_dick_path = '../../../mobydick.txt'
    moby_dick_lines = load_moby_dick(moby_dick_path)
    milvus = MilvusDB()
    milvus.remove_all_collections()

    # Create collections for each media type
    for collection_name in milvus.collections.values():
        print(f"Creating collection: {collection_name}")
        milvus.create_collection(collection_name)

    # Prepare Moby Dick data
    moby_dick_data = []
    for i, line in enumerate(moby_dick_lines):
        moby_dick_data.append({
            "type": "document",
            "file": "mobydick.txt",
            "page": i // 40 + 1,  # Assuming 40 lines per page
            "line": i % 40 + 1,
            "text": line
        })

    # Insert embeddings using BGE-M3
    print(f"Inserting {len(moby_dick_data)} lines from Moby Dick...")
    for item in tqdm(moby_dick_data):
        milvus.insert([item])

    # Perform a similarity search
    query_text = "Call me Ishmael"
    results = milvus.similarity_search(query_text, top_k=5)

    print("\nSearch results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. File: {result['file']}")
        print(f"   Page: {result['metadata']['page']}, Line: {result['metadata']['line']}")
        print(f"   Distance: {result['distance']}")
        print(f"   Text: {moby_dick_lines[result['metadata']['page'] * 40 + result['metadata']['line'] - 41]}")
        print()

    milvus.disconnect()