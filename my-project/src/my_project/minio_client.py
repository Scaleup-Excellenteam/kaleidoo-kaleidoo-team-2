import os
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv
from io import BytesIO
import json

class MinIOClient:
    def __init__(self):
        load_dotenv()
        self.client = Minio(
            os.getenv("MINIO_URL"),
            access_key=os.getenv("MINIO_ACCESS_KEY"),
            secret_key=os.getenv("MINIO_SECRET_KEY"),
            secure=os.getenv("MINIO_SECURE").lower() == 'true'
        )

    def upload_json_to_minio(self, bucket_name, object_name, json_data):
        """
        Uploads JSON metadata to MinIO.
        """
        try:
            json_bytes = json.dumps(json_data, ensure_ascii=False).encode('utf-8')
            json_stream = BytesIO(json_bytes)
            self.client.put_object(
                bucket_name, object_name, json_stream, len(json_bytes), content_type="application/json"
            )
            print(f"Successfully uploaded JSON metadata '{object_name}' to bucket '{bucket_name}'")
        except S3Error as e:
            print(f"Error uploading JSON metadata: {e}")

    def delete_file_in_bucket(self, bucket_name, file_name):
        """
        Deletes a specific file from a MinIO bucket.
        """
        try:
            self.client.remove_object(bucket_name, file_name)
            print(f"File '{file_name}' successfully deleted from bucket '{bucket_name}'")
        except S3Error as e:
            print(f"Error deleting file '{file_name}' from bucket '{bucket_name}': {e}")

    def get_metadata_from_minio(self, bucket_name, file_name, file_type, page_number=None, start_time=None):
        """
        Retrieves metadata from MinIO.
        """
        metadata_file_name = f"{file_name}_{file_type}.json"
        try:
            response = self.client.get_object(bucket_name, metadata_file_name)
            metadata = json.loads(response.read().decode('utf-8'))
            if file_type == "pdf" and page_number is not None:
                return next((p["content"] for p in metadata['pages'] if p["page_number"] == page_number), f"Page {page_number} not found")
            elif file_type == "mp3" and start_time is not None:
                return next((t["content"] for t in metadata['transcription'] if t["start_time"] == start_time), f"Start time {start_time} not found")
            elif file_type in ["jpg", "png"]:
                return f"Image metadata: {metadata['content']}"
            return "Invalid type or parameters."
        except S3Error as e:
            print(f"Error retrieving metadata: {e}")
            return None
        
    # buckets name : images, audio, pdfs, video    
    def list_files_in_bucket(self, bucket_name):
        """
        Lists all files (objects) in a given MinIO bucket and returns their contents as a dictionary.
        
        Args:
            bucket_name (str): The name of the bucket from which to list files.
        
        Returns:
            dict: A dictionary where the keys are object names and the values are their contents.
        """
        try:
            # Check if the bucket exists
            if not self.client.bucket_exists(bucket_name):
                return f"Bucket '{bucket_name}' does not exist."

            # List all objects in the bucket
            objects = self.client.list_objects(bucket_name)
            file_contents = {}

            # Iterate through each object and retrieve its content
            for obj in objects:
                try:
                    # Get the object content
                    response = self.client.get_object(bucket_name, obj.object_name)
                    content = response.read().decode('utf-8')
                    
                    # Parse JSON content and ensure proper handling of Hebrew text
                    try:
                        file_contents[obj.object_name] = json.loads(content)
                    except json.JSONDecodeError:
                        file_contents[obj.object_name] = content  # In case the file is not valid JSON, return raw content

                except S3Error as e:
                    print(f"Error retrieving object '{obj.object_name}': {e}")
                    file_contents[obj.object_name] = None

            return file_contents

        except S3Error as e:
            print(f"Error listing objects in bucket '{bucket_name}': {e}")
            return None