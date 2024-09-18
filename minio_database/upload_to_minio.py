import json
from minio import Minio
from io import BytesIO
from minio.error import S3Error
from dotenv import load_dotenv
import os

# Example JSON metadata for a PDF file
pdf_metadata = {
    "file_name": "lecture21523",
    "type": "pdf",
    "pages": [
        {"page_number": 1, "content": "This is the content of page 1..."},
        {"page_number": 2, "content": "This is the content of page 2..."}
    ]
}

# Example JSON metadata for an audio file (transcription)
audio_metadata = {
    "file_name": "lecture21523",
    "type": "mp3",
    "transcription": [
        {"start_time": "00:00:00", "content": "Introduction to the lecture..."},
        {"start_time": "00:01:01", "content": "Discussion about the main topic..."}
    ]
}

# Example JSON metadata for an image file with metadata as text
image_metadata = {
    "file_name": "lecture_image",
    "type": "jpg",
    "description": "This image shows a diagram related to the lecture.",
    "metadata": "Ayham, Raz, Boris and anto will be the best"
}
# Load environment variables from the .env file
load_dotenv()

# Retrieve values from environment variables
minio_url = os.getenv("MINIO_URL")
minio_access_key = os.getenv("MINIO_ACCESS_KEY")
minio_secret_key = os.getenv("MINIO_SECRET_KEY")
minio_secure = os.getenv("MINIO_SECURE").lower() == 'true'  # Convert to boolean

# Initialize MinIO client using environment variables
minio_client = Minio(
    minio_url,
    access_key=minio_access_key,
    secret_key=minio_secret_key,
    secure=minio_secure 
)

# Function to upload JSON metadata to MinIO (no media files involved)
def upload_json_to_minio(bucket_name, object_name, json_data):
    """
    Uploads a JSON file (metadata) to MinIO.

    Args:
        bucket_name (str): The name of the bucket in MinIO.
        object_name (str): The name of the JSON file to be stored.
        json_data (dict): The JSON data to upload.
    """
    try:
        # Convert JSON to bytes and create a BytesIO stream
        json_bytes = json.dumps(json_data, ensure_ascii=False).encode('utf-8')
        json_stream = BytesIO(json_bytes)
        
        # Upload the JSON stream to MinIO
        minio_client.put_object(
            bucket_name, object_name, json_stream, len(json_bytes), content_type="application/json"
        )
        print(f"Successfully uploaded JSON metadata '{object_name}' to bucket '{bucket_name}'")
    except S3Error as e:
        print(f"Error uploading JSON metadata: {e}")

# Function to retrieve metadata from MinIO
def get_metadata_from_minio(bucket_name, file_name, file_type, page_number=None, start_time=None):
    """
    Retrieves metadata (JSON) from MinIO and returns specific content based on the file type and provided parameters.

    Args:
        bucket_name (str): The name of the bucket in MinIO.
        file_name (str): The name of the file (without extension) for which metadata is stored.
        file_type (str): The type of the file (either 'pdf', 'mp3', or 'jpg').
        page_number (int, optional): The page number to retrieve for PDF files.
        start_time (str, optional): The start time to retrieve transcription for audio files.

    Returns:
        str: The content of the specific page or transcription, or an error message if not found.
    """
    metadata_file_name = f"{file_name}_{file_type}.json"  # Construct the metadata file name
    
    try:
        # Retrieve the JSON metadata from MinIO
        response = minio_client.get_object(bucket_name, metadata_file_name)
        metadata_content = response.read().decode('utf-8')
        metadata = json.loads(metadata_content)

        # Return the specified page content for PDF files
        if file_type == "pdf" and page_number is not None:
            for page in metadata['pages']:
                if page['page_number'] == page_number:
                    return f"Content of {file_name}.pdf, Page {page_number}: {page['content']}"
            return f"Page {page_number} not found in {file_name}.pdf"

        # Return the specified transcription content for audio files
        elif file_type == "mp3" and start_time is not None:
            for transcription in metadata['transcription']:
                if transcription['start_time'] == start_time:
                    return f"Transcription of {file_name}.mp3, Start Time {start_time}: {transcription['content']}"
            return f"Transcription starting at {start_time} not found in {file_name}.mp3"
        
        # Return the image metadata
        elif file_type == "jpg" or file_type== "png":
            return f"Image metadata for {file_name}.{metadata['type']}: content: {metadata['content']}"
            return f"Image metadata for {file_name}: {metadata['description']} - Metadata: {metadata['metadata']}"
        
        else:
            return "Invalid file type or missing parameters."
    
    except S3Error as e:
        print(f"Error retrieving metadata: {e}")
        return None

# Main function to upload metadata only (for testing purposes)
def upload_metadata_only():
    """
    Uploads example PDF, image, and audio metadata to the relevant MinIO buckets.
    """
    bucket_name_pdf = "pdfs"
    bucket_name_audio_video = "audio-video"
    bucket_name_images = "images"
    
    # Ensure the buckets for PDFs, audio/video, and images exist
    if not minio_client.bucket_exists(bucket_name_pdf):
        minio_client.make_bucket(bucket_name_pdf)
    if not minio_client.bucket_exists(bucket_name_audio_video):
        minio_client.make_bucket(bucket_name_audio_video)
    if not minio_client.bucket_exists(bucket_name_images):
        minio_client.make_bucket(bucket_name_images)

    # Upload PDF metadata
    upload_json_to_minio(bucket_name_pdf, f"{pdf_metadata['file_name']}_{pdf_metadata['type']}.json", pdf_metadata)

    # Upload audio metadata
    upload_json_to_minio(bucket_name_audio_video, f"{audio_metadata['file_name']}_{audio_metadata['type']}.json", audio_metadata)

    # Upload image metadata
    upload_json_to_minio(bucket_name_images, f"{image_metadata['file_name']}_{image_metadata['type']}.json", image_metadata)

if __name__ == "__main__":
    # Upload the metadata for testing
    upload_metadata_only()

    # Retrieve and print metadata for testing
    pdf_meta = get_metadata_from_minio("pdfs", "lecture21523", "pdf", page_number=2)
    print(pdf_meta)

    audio_meta = get_metadata_from_minio("audio-video", "lecture21523", "mp3", start_time="00:01:01")
    print(audio_meta)

    image_meta = get_metadata_from_minio("images", "lecture_image", "jpg")
    print(image_meta)


