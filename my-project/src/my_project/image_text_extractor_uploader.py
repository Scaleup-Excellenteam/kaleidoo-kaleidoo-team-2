import os
import time
from PIL import Image
import pytesseract
from minio_client import MinIOClient

class ImageTextExtractorUploader:
    def __init__(self):
        self.minio_client = MinIOClient()

    def extract_text_from_image(self, image_path, lang='heb', tess_cmd=r'C:\Program Files\Tesseract-OCR\tesseract.exe'):
        pytesseract.pytesseract.tesseract_cmd = tess_cmd
        img = Image.open(image_path)
        custom_config = f'--oem 3 --psm 6 -l {lang}'
        return pytesseract.image_to_string(img, config=custom_config)

    def upload_image_metadata(self, image_path):
        file_name_without_extension = os.path.basename(image_path).split('.')[0]
        file_extension = os.path.basename(image_path).split('.')[1]
        extracted_text = self.extract_text_from_image(image_path)
        image_metadata = {
            "file_name": file_name_without_extension,
            "type": file_extension,
            "content": extracted_text
        }
        object_name = f"{file_name_without_extension}_{file_extension}.json"
        self.minio_client.upload_json_to_minio("images", object_name, image_metadata)

    def run(self, image_path):
        start_time = time.time()
        self.upload_image_metadata(image_path)
        print(f"Time taken: {time.time() - start_time:.6f} seconds")
