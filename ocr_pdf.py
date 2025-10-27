#!/usr/bin/env python3
import ocrmypdf

print("Running OCR on lady_clean.pdf...")

try:
    ocrmypdf.ocr('lady_clean.pdf', 'lady_searchable.pdf', language='eng')
    print("Done! Saved to lady_searchable.pdf")
except Exception as e:
    print(f"Error: {e}")
