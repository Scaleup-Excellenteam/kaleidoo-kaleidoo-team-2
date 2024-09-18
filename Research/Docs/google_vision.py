import os
import io
from google.cloud import vision
import fitz
from PIL import Image
from pathlib import Path

src_path = "TestingSamples/PDF_example.pdf"
dst_path = "TestingOutputs/pdf_to_img_example_transcript.txt"

poppler_path = '/usr/bin/pdfinfo' # for pdf to img lib

# Load JSON key into env var
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'kaleidoo-435715-96fdd3ef71f6.json' 

def detect_text_from_image(image_path):
    client = vision.ImageAnnotatorClient()

    with open(image_path, "rb") as image_file:
        content = image_file.read()

    print ("Processing...")

    image = vision.Image(content=content)

    image_context = vision.ImageContext(
        language_hints=['he']  
    )

    response = client.text_detection(image=image, image_context=image_context)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    if texts:
        with open(dst_path, 'w', encoding='utf-8') as file:
            file.write(texts[0].description)
    else:
        print("No text detected.")
    
    print ("Done Processing.")

    if response.error.message:
        raise Exception(f'{response.error.message}')


# Convert single-page PDF to an image
img_dst_path = 'TestingSamples/image_path.png'
def pdf_to_image(pdf_path):
    pdf_document = fitz.open(pdf_path)
    page = pdf_document.load_page(0)
    pix = page.get_pixmap()
    img = Image.open(io.BytesIO(pix.tobytes()))
    img.save(img_dst_path, format='PNG')
    pdf_document.close()
    return img_dst_path


pdf_path = src_path
detect_text_from_image(pdf_to_image(pdf_path))
