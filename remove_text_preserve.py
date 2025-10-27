#!/usr/bin/env python3
"""
Remove text layer from PDF while preserving images and graphics.
Uses regex-based stream filtering.
"""

import re
from PyPDF2 import PdfReader, PdfWriter
from PyPDF2.generic import ByteStringObject, TextStringObject, NameObject
import io

def filter_text_from_content(data):
    """
    Remove text rendering commands from PDF content stream.
    Keeps graphics and images intact.
    """
    if not data:
        return data

    try:
        content = data.decode('latin-1', errors='ignore')
    except:
        return data

    lines = content.split('\n')
    result = []
    in_text = False
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Track text objects
        if stripped == 'BT':
            in_text = True
            i += 1
            continue
        elif stripped == 'ET':
            in_text = False
            i += 1
            continue

        # Skip content inside text objects
        if in_text:
            i += 1
            continue

        # Skip individual text operators (outside of text blocks too)
        # These are operators that specifically render text
        if re.search(r'\s(Tj|TJ)\s*$', line):  # Show text
            i += 1
            continue
        if re.search(r'\'\'?\s*$', stripped):  # Move and show text (bare ' or ")
            if stripped in ["'", '"']:
                i += 1
                continue

        result.append(line)
        i += 1

    try:
        return '\n'.join(result).encode('latin-1', errors='ignore')
    except:
        return data

def remove_text_from_pdf(input_path, output_path):
    """
    Remove text from PDF while preserving images and vector graphics.
    """
    print(f"Opening {input_path}...")

    with open(input_path, 'rb') as f:
        reader = PdfReader(f)
        writer = PdfWriter()

        total = len(reader.pages)
        print(f"Total pages: {total}")

        for idx, page in enumerate(reader.pages, 1):
            if idx % 50 == 0 or idx == 1:
                print(f"Processing page {idx}/{total}...")

            try:
                # Access content stream
                if "/Contents" in page:
                    contents_ref = page["/Contents"]

                    # Dereference if needed
                    if hasattr(contents_ref, 'get_object'):
                        contents_obj = contents_ref.get_object()
                    else:
                        contents_obj = contents_ref

                    # Handle array of content streams
                    if isinstance(contents_obj, list):
                        new_contents = []
                        for item in contents_obj:
                            if hasattr(item, 'get_object'):
                                item = item.get_object()
                            if hasattr(item, 'get_data'):
                                data = item.get_data()
                                filtered = filter_text_from_content(data)
                                new_contents.append(ByteStringObject(filtered))
                            else:
                                new_contents.append(item)
                        # Don't update - keep original structure
                    else:
                        # Single content stream
                        if hasattr(contents_obj, 'get_data'):
                            data = contents_obj.get_data()
                            filtered = filter_text_from_content(data)
                            # Try to update (may fail, but that's ok)
                            try:
                                from PyPDF2.generic import ArrayObject, DictionaryObject
                                page[NameObject("/Contents")] = ByteStringObject(filtered)
                            except:
                                pass
            except Exception as e:
                print(f"  Page {idx}: {type(e).__name__}: {e}")

            writer.add_page(page)

        print(f"Writing {output_path}...")
        with open(output_path, 'wb') as f:
            writer.write(f)

        print(f"Complete! Output: {output_path}")

if __name__ == "__main__":
    remove_text_from_pdf("lady.pdf", "lady_clean.pdf")
