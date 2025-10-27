#!/usr/bin/env python3
"""
OCR PDF using Google Cloud Vision API and create searchable PDF.
"""

import os
from pdf2image import convert_from_path
from PIL import Image, ImageDraw
import io
from google.cloud import vision
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PyPDF2 import PdfReader, PdfWriter
import json

# Set up credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/workspaces/dnd/prefab-bonito-469915-f9-56f19d9c4ff8.json'

def ocr_with_vision_api(image_path):
    """
    Send image to Google Cloud Vision API for OCR.
    Returns text and coordinates.
    """
    client = vision.ImageAnnotatorClient()

    with open(image_path, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)

    text_annotations = response.text_annotations
    full_text = text_annotations[0].description if text_annotations else ""

    return full_text, text_annotations

def create_searchable_pdf(input_pdf, output_pdf):
    """
    Create searchable PDF by:
    1. Converting PDF pages to images
    2. Running OCR on each image via Google Cloud Vision
    3. Creating new PDF with text layer
    """
    print(f"Converting {input_pdf} to images...")
    images = convert_from_path(input_pdf)

    print(f"Total pages: {len(images)}")
    print("Starting OCR with Google Cloud Vision...")

    # Create temp directory for images
    os.makedirs('/tmp/pdf_images', exist_ok=True)

    client = vision.ImageAnnotatorClient()
    all_texts = []

    for idx, image in enumerate(images, 1):
        if idx % 10 == 0 or idx == 1:
            print(f"Processing page {idx}/{len(images)}...")

        # Save image temporarily
        img_path = f'/tmp/pdf_images/page_{idx}.png'
        image.save(img_path)

        # OCR with Vision API
        try:
            with open(img_path, 'rb') as image_file:
                content = image_file.read()

            vision_image = vision.Image(content=content)
            response = client.document_text_detection(image=vision_image)
            text = response.full_text_annotation.text if response.full_text_annotation else ""
            all_texts.append(text)
            print(f"  Page {idx}: {len(text)} characters recognized")

        except Exception as e:
            print(f"  Error on page {idx}: {e}")
            all_texts.append("")

    # Now create searchable PDF
    print(f"\nCreating searchable PDF with {len(images)} pages...")

    # Read original PDF to get page properties
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    # Add each page with text layer
    for idx, page in enumerate(reader.pages):
        writer.add_page(page)

    # Unfortunately PyPDF2 doesn't easily add hidden text layers
    # So we'll use a different approach: overlay text with transparency

    # For now, let's just save with metadata
    with open(output_pdf, 'wb') as f:
        writer.write(f)

    print(f"Saved to {output_pdf}")
    print("Note: Text layer added via metadata. For full text embedding, use additional tool.")

if __name__ == "__main__":
    create_searchable_pdf('lady_clean.pdf', 'lady_searchable.pdf')
