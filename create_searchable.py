#!/usr/bin/env python3
"""
Create truly searchable PDF by overlaying invisible text on images.
"""

import os
from PIL import Image, ImageDraw
import pdfplumber
import io
from google.cloud import vision
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
import PyPDF2

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '/workspaces/dnd/prefab-bonito-469915-f9-56f19d9c4ff8.json'

def create_searchable_pdf_with_text(input_pdf, output_pdf):
    """
    Create searchable PDF by:
    1. Rendering pages to images
    2. Running OCR to get text
    3. Creating PDF with text overlaid at zero opacity
    """

    print("Reading OCR results...")
    with open('ocr_results.txt', 'r') as f:
        content = f.read()
        pages_text = []
        for section in content.split('--- Page '):
            if section.strip():
                # Extract text after first newline
                text = section.split('\n', 1)[1] if '\n' in section else ''
                pages_text.append(text.strip())

    print(f"Loaded OCR text for {len(pages_text)} pages")

    # Read original PDF structure
    with pdfplumber.open(input_pdf) as pdf:
        total_pages = len(pdf.pages)

        # Create output PDF using reportlab + pypdf merge
        temp_text_pdf = '/tmp/text_layer.pdf'
        c = canvas.Canvas(temp_text_pdf, pagesize=letter)

        print(f"Creating text layer for {total_pages} pages...")

        for idx, page in enumerate(pdf.pages, 1):
            if idx % 50 == 0 or idx == 1:
                print(f"  Page {idx}/{total_pages}")

            # Get page dimensions
            page_width = page.width
            page_height = page.height

            # Set page size
            c.setPageSize((page_width, page_height))

            # Add text with zero opacity (invisible but searchable)
            if idx <= len(pages_text):
                text = pages_text[idx - 1]
                if text:
                    # Draw text at tiny size with transparency
                    # Use Helvetica at very small size
                    c.setFont("Helvetica", 1)
                    c.setFillAlpha(0)  # Invisible

                    # Add text at top (won't be visible due to zero opacity)
                    y_pos = page_height - 20
                    for line in text.split('\n')[:10]:  # First 10 lines to keep reasonable
                        c.drawString(10, y_pos, line[:100])  # Max 100 chars per line
                        y_pos -= 10

            c.showPage()

        c.save()
        print(f"Text layer created at {temp_text_pdf}")

    # Now merge the original image PDF with the text layer
    print("Merging image PDF with text layer...")

    from PyPDF2 import PdfReader, PdfWriter

    with open(input_pdf, 'rb') as f1, open(temp_text_pdf, 'rb') as f2:
        reader_image = PdfReader(f1)
        reader_text = PdfReader(f2)
        writer = PdfWriter()

        for idx in range(len(reader_image.pages)):
            # Get image page
            img_page = reader_image.pages[idx]

            # Merge with text page if available
            if idx < len(reader_text.pages):
                text_page = reader_text.pages[idx]
                img_page.merge_page(text_page)

            writer.add_page(img_page)

    with open(output_pdf, 'wb') as f:
        writer.write(f)

    print(f"Searchable PDF created: {output_pdf}")
    print(f"File size: {os.path.getsize(output_pdf) / 1024 / 1024:.1f} MB")

if __name__ == "__main__":
    create_searchable_pdf_with_text('lady_clean.pdf', 'lady_searchable.pdf')
