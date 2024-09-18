import os
from minio import Minio
from minio.error import S3Error
from dotenv import load_dotenv

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

def delete_file_in_bucket(bucket_name, file_name):
    """
    Deletes a specific file (object) from a bucket in MinIO.
    
    Args:
        bucket_name (str): The name of the bucket containing the file.
        file_name (str): The name of the file (object) to delete.
    """
    try:
        minio_client.remove_object(bucket_name, file_name)
        print(f"File '{file_name}' successfully deleted from bucket '{bucket_name}'")
    except S3Error as e:
        print(f"Error deleting file '{file_name}' from bucket '{bucket_name}': {e}")

def delete_bucket(bucket_name):
    """
    Deletes an entire bucket from MinIO.
    
    Args:
        bucket_name (str): The name of the bucket to delete.
    """
    try:
        # Check if the bucket is empty
        objects = minio_client.list_objects(bucket_name)
        if any(objects):
            print(f"Bucket '{bucket_name}' is not empty. Please empty the bucket before deletion.")
        else:
            minio_client.remove_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' successfully deleted.")
    except S3Error as e:
        print(f"Error deleting bucket '{bucket_name}': {e}")

def get_user_choice():
    """
    Prompts the user to choose between deleting a bucket or a file inside a bucket.
    
    Returns:
        int: The user's choice (1 for deleting a bucket, 2 for deleting a file).
    """
    print("Choose an option:")
    print("1 - Delete a bucket")
    print("2 - Delete a file in a bucket")
    
    while True:
        try:
            choice = int(input("Enter your choice (1 or 2): "))
            if choice in [1, 2]:
                return choice
            else:
                print("Invalid choice. Please enter 1 or 2.")
        except ValueError:
            print("Invalid input. Please enter a number (1 or 2).")

def main():
    """
    Main function to handle user interaction and perform the chosen delete operation.
    """
    user_choice = get_user_choice()
    
    if user_choice == 1:
        # Delete bucket
        bucket_name = input("Enter the name of the bucket to delete: ").strip()
        confirmation = input(f"Are you sure you want to delete the bucket '{bucket_name}'? (yes/no): ").lower()
        if confirmation == "yes":
            delete_bucket(bucket_name)
        else:
            print("Bucket deletion canceled.")
    
    elif user_choice == 2:
        # Delete file in bucket
        bucket_name = input("Enter the name of the bucket: ").strip()
        file_name = input("Enter the name of the file to delete: ").strip()
        confirmation = input(f"Are you sure you want to delete the file '{file_name}' in bucket '{bucket_name}'? (yes/no): ").lower()
        if confirmation == "yes":
            delete_file_in_bucket(bucket_name, file_name)
        else:
            print("File deletion canceled.")

if __name__ == "__main__":
    main()
