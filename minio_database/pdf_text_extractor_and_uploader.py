import PyPDF2
import json
import time
import os
from upload_to_minio import upload_json_to_minio, get_metadata_from_minio

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from each page of the given PDF file and structures it into a list of pages with their content.
    
    Args:
        pdf_path (str): The path to the PDF file.
    
    Returns:
        list: A list of dictionaries, each containing the page number and the content of that page.
    """
    # Open the PDF file
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        pages_content = []

        # Iterate over each page and extract text
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            page_text = page.extract_text()

            if page_text:
                # Append the page content along with its page number
                pages_content.append({"page_number": page_num + 1, "content": page_text})

    return pages_content

def upload_pdf_metadata_to_minio(pdf_path):
    """
    Extracts text from a PDF, structures it into JSON metadata, and uploads it to MinIO.
    
    Args:
        pdf_path (str): The path to the PDF file.
    """
    # Extract content from the PDF
    pages_content = extract_text_from_pdf(pdf_path)

    # Get the base name of the file without the '.pdf' extension
    file_name_without_extension = os.path.basename(pdf_path)[:-4]  

    # Create the metadata dictionary
    pdf_metadata = {
        "file_name": file_name_without_extension,
        "type": "pdf",
        "pages": pages_content
    }

    # Upload the JSON metadata to the "pdfs" bucket in MinIO
    object_name = f"{pdf_metadata['file_name']}_{pdf_metadata['type']}.json"
    upload_json_to_minio("pdfs", object_name, pdf_metadata)

if __name__ == "__main__":
    # Path to the PDF file you want to upload
    pdf_path = 'RAG/clean_document_heb.pdf'  # Replace with the path to your PDF file

    # Measure the time taken for the entire process
    start_time = time.time()

    # Extract text from the PDF and upload its metadata as JSON to MinIO
    upload_pdf_metadata_to_minio(pdf_path)

    # Calculate and print the time elapsed during the process
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Time taken to extract and upload metadata: {elapsed_time:.6f} seconds")
    print(get_metadata_from_minio("pdfs", "clean_document_heb", "pdf", 40, start_time=None))

