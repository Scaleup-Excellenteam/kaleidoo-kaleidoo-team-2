import os
import time
from PyPDF2 import PdfReader
from minio_client import MinIOClient

class PDFTextExtractorUploader:
    def __init__(self):
        self.minio_client = MinIOClient()

    def extract_text_from_pdf(self, pdf_path):
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            pages_content = [{"page_number": page_num + 1, "content": page.extract_text()}
                             for page_num, page in enumerate(reader.pages)]
        return pages_content

    def upload_pdf_metadata(self, pdf_path):
        file_name_without_extension = os.path.basename(pdf_path)[:-4]
        pages_content = self.extract_text_from_pdf(pdf_path)
        pdf_metadata = {
            "file_name": file_name_without_extension,
            "type": "pdf",
            "pages": pages_content
        }
        object_name = f"{file_name_without_extension}_pdf.json"
        self.minio_client.upload_json_to_minio("pdfs", object_name, pdf_metadata)

    def run(self, pdf_path):
        start_time = time.time()
        self.upload_pdf_metadata(pdf_path)
        print(f"Time taken: {time.time() - start_time:.6f} seconds")

# how to use :
    # pdf_uploader = PDFTextExtractorUploader()
    # pdf_path = "RAG/clean_document_heb.pdf"  

    # Upload PDF metadata:
    #   pdf_uploader.run(pdf_path)

    # Retrieve PDF metadata from MinIO:
    #   pdf_name = pdf_path.split('/')[-1].split('.')[0]  # Extract the file name without extension
    #   retrieved_pdf_metadata = minio_client.get_metadata_from_minio("pdfs", pdf_name, "pdf", page_number=1)

    # Print the retrieved PDF metadata:
    #   print(f"Retrieved PDF metadata for page 1: {retrieved_pdf_metadata}")

# the json file look like 
    # {
    #     "file_name": "clean_document_heb",
    #       "type": "pdf",
    #         "pages":
    #           [ {"page_number": 1,
    #               "content": " \n \n \n \nסיפורים קצרים \nמלאי מסרים \nלכל גיל וזמן \nולמרחב המוגן \n \n \n \n \n \n \n \n \n \n \n \n \n"
    #               },
    #             {.....}
    #           ]
    # }