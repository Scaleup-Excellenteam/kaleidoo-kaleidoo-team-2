from minio_client import MinIOClient
from milvus_module import MilvusClient


class FileVectorMigrator:
    def __init__(self, minio, milvus):
        """
        minio: instance of MinIO client.
        milvus: instance of Milvus client.
        """
        self.minio = minio
        self.milvus = milvus
        # Defining collections and corresponding MinIO buckets directly in the code
        self.collections = {
            "pdfs",
            "audio",
            "images",
            "video"
        }

    def migrate(self):
        # List to hold data to be inserted into Milvus
        data_to_insert = []

        for collection in self.collections:




        # Loop through the collections (buckets and corresponding Milvus collections)
        for bucket_name, milvus_collection in self.collections.items():
            print(f"Starting migration for bucket '{bucket_name}' and collection '{milvus_collection}'")

            # Iterate over the objects in the MinIO bucket using the client
            objects = self.minio.client.list_objects(bucket_name, recursive=True)
            for obj in objects:
                # get the object from MinIO
                output = self.minio.get_metadata_from_minio(bucket_name, obj.object_name, bucket_name, page_number=None, start_time=None)
                #TODO Implement the logic to extract text from audio, image, and video files
                text = output['content']
                # Collect the data to be inserted into Milvus
                data_to_insert.append({
                    'type': milvus_collection,
                    'file': obj.object_name,
                    'text': text
                })

        # Insert the collected data into Milvus
        self.milvus.insert(data_to_insert)

        print("Migration completed for all collections!")


# Example usage
if __name__ == "__main__":
    # Create instances of MinIO and Milvus clients
    minio_client = MinIOClient()
    milvus_client = MilvusClient()

    # Create and run the migration
    migrator = FileVectorMigrator(minio_client, milvus_client)
    migrator.migrate()
