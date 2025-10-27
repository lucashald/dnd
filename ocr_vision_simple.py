#!/usr/bin/env python3
"""
OCR PDF using Google Cloud Vision API and create searchable PDF.
Uses pdfplumber for PDF handling and Vision API for OCR.
"""

import os
import pdfplumber
import io
from PIL import Image
from google.cloud import vision
from PyPDF2 import PdfWriter
import sys

# Set up credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/workspaces/dnd/prefab-bonito-469915-f9-56f19d9c4ff8.json'

def create_searchable_pdf(input_pdf, output_pdf):
    """
    Create searchable PDF by rendering pages and running OCR via Google Cloud Vision.
    """
    print(f"Opening {input_pdf}...")

    with pdfplumber.open(input_pdf) as pdf:
        total_pages = len(pdf.pages)
        print(f"Total pages: {total_pages}")
        print("Starting OCR with Google Cloud Vision API...\n")

        client = vision.ImageAnnotatorClient()
        all_texts = []

        for idx, page in enumerate(pdf.pages, 1):
            if idx % 10 == 0 or idx == 1:
                print(f"Processing page {idx}/{total_pages}...", file=sys.stderr)

            try:
                # Render page to image
                pil_image = page.to_image()

                # Convert PIL image to bytes
                img_byte_arr = io.BytesIO()
                pil_image.save(img_byte_arr, format='PNG')
                img_byte_arr.seek(0)
                content = img_byte_arr.read()

                # Send to Vision API
                vision_image = vision.Image(content=content)
                response = client.document_text_detection(image=vision_image)

                # Extract text
                text = response.full_text_annotation.text if response.full_text_annotation else ""
                all_texts.append(text)

                char_count = len(text)
                print(f"  Page {idx}: {char_count} characters")

            except Exception as e:
                print(f"  Error on page {idx}: {e}", file=sys.stderr)
                all_texts.append("")

    print(f"\nAll pages processed. Extracted text from {len(all_texts)} pages.")
    print("Saving OCR results...")

    # Save results to text file for reference
    with open('ocr_results.txt', 'w') as f:
        for idx, text in enumerate(all_texts, 1):
            f.write(f"--- Page {idx} ---\n{text}\n\n")

    print("OCR results saved to ocr_results.txt")

    # For searchable PDF with text layer embedded, we'd need additional tools
    # For now, create a copy with metadata
    from PyPDF2 import PdfReader
    reader = PdfReader(input_pdf)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    with open(output_pdf, 'wb') as f:
        writer.write(f)

    print(f"Saved basic PDF to {output_pdf}")
    print("\nNote: For full searchable PDF with embedded text layer, use ocrmypdf or similar tool.")

if __name__ == "__main__":
    create_searchable_pdf('lady_clean.pdf', 'lady_searchable.pdf')
