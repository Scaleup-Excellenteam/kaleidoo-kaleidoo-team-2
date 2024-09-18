import pytesseract
from PIL import Image
import json
import os
import time
from upload_to_minio import upload_json_to_minio, get_metadata_from_minio

def extract_text_from_image(image_path, lang='heb', tess_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
    """
    Extracts text from an image using Tesseract OCR.

    Parameters:
    - image_path: str : Path to the image file.
    - lang: str : Language code for the text extraction. Default is 'heb' for Hebrew.
    - tess_cmd: str : Path to the Tesseract-OCR executable.

    Returns:
    - str: Extracted text from the image.
    """
    try:
        # Set the path to the Tesseract executable
        pytesseract.pytesseract.tesseract_cmd = tess_cmd
        
        # Open the image file
        img = Image.open(image_path)
        
        # Set custom configuration for Tesseract
        custom_config = f'--oem 3 --psm 6 -l {lang}'
        
        # Perform OCR on the image
        extracted_text = pytesseract.image_to_string(img, config=custom_config)
        
        return extracted_text
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return ""

def upload_image_metadata_to_minio(image_path):
    """
    Extracts text from an image, structures it into JSON metadata, and uploads it to MinIO.
    
    Args:
        image_path (str): The path to the image file.
    """
    # Extract content from the image
    extracted_text = extract_text_from_image(image_path)

    # Get the base name of the image file without the extension
    file_name_without_extension = os.path.basename(image_path).split('.')[0]
    file_extension = os.path.basename(image_path).split('.')[-1]

    # Create the metadata dictionary
    image_metadata = {
        "file_name": file_name_without_extension,
        "type": file_extension,
        "content": extracted_text
    }

    # Upload the JSON metadata to the "images" bucket in MinIO
    object_name = f"{image_metadata['file_name']}_{image_metadata['type']}.json"
    upload_json_to_minio("images", object_name, image_metadata)

if __name__ == "__main__":
    # Path to your image file
    image_path = 'POC_Examples/clean_text_image_heb.png'  # Replace with your image file path

    # Measure the time taken for the entire process
    start_time = time.time()

    # Extract text from the image and upload its metadata as JSON to MinIO
    upload_image_metadata_to_minio(image_path)

    # Calculate and print the time elapsed during the process
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken to extract and upload image metadata: {elapsed_time:.6f} seconds")
    print(get_metadata_from_minio("images", "clean_text_image_heb", "png"))


