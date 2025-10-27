#!/usr/bin/env python3
"""
Remove text layer from PDF using low-level PDF manipulation.
This approach directly modifies the content stream to remove text operations.
"""

import PyPDF2
from io import BytesIO
import re

def remove_text_layer_v2(input_pdf, output_pdf):
    """
    Remove text content from PDF by modifying content streams.
    """
    with open(input_pdf, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        writer = PyPDF2.PdfWriter()

        print(f"Processing {len(reader.pages)} pages...")

        for page_num, page in enumerate(reader.pages):
            print(f"Processing page {page_num + 1}...", end='\r')

            # Get the content stream
            if "/Contents" in page:
                contents = page["/Contents"]

                # Handle different content types
                try:
                    if isinstance(contents, PyPDF2.generic.ArrayObject):
                        # Multiple content streams
                        new_contents = []
                        for content in contents:
                            if hasattr(content, 'get_data'):
                                data = content.get_data()
                            else:
                                obj = content.get_object() if hasattr(content, 'get_object') else content
                                data = obj.get_data() if hasattr(obj, 'get_data') else content

                            filtered = filter_text_operations(data)
                            new_contents.append(PyPDF2.generic.ByteStringObject(filtered))

                        # Create new content stream
                        page["/Contents"] = PyPDF2.generic.ArrayObject(new_contents)
                    else:
                        # Single content stream
                        if hasattr(contents, 'get_data'):
                            data = contents.get_data()
                        else:
                            obj = contents.get_object() if hasattr(contents, 'get_object') else contents
                            data = obj.get_data() if hasattr(obj, 'get_data') else contents

                        filtered = filter_text_operations(data)
                        page["/Contents"] = PyPDF2.generic.ByteStringObject(filtered)

                except Exception as e:
                    print(f"Could not process page {page_num + 1}: {e}")

            writer.add_page(page)

        with open(output_pdf, 'wb') as f:
            writer.write(f)

        print(f"\nSuccessfully created {output_pdf}")

def filter_text_operations(data):
    """
    Remove text-related operations from PDF content stream.
    """
    try:
        # Try to decode as latin-1
        text = data.decode('latin-1', errors='ignore')
    except:
        return data

    lines = text.split('\n')
    filtered_lines = []
    in_text_block = False

    for line in lines:
        stripped = line.strip()

        # Skip entire text blocks
        if stripped == 'BT':  # Begin text
            in_text_block = True
            continue
        elif stripped == 'ET':  # End text
            in_text_block = False
            continue

        # Skip lines within text blocks
        if in_text_block:
            continue

        # Skip text-related operators
        if any(stripped.endswith(op) for op in [
            ' Tj',   # Show text
            ' TJ',   # Show text with positioning
            " '",    # Move to next line and show text
            ' "',    # Set spacing and show text
            ' Td',   # Set text position
            ' TD',   # Set text position and leading
            ' T*',   # Move to next text line
            ' Tm',   # Set text matrix
            ' Tw',   # Set word spacing
            ' Tz',   # Set horizontal scaling
            ' TL',   # Set text leading
            ' Tf',   # Set font and size
            ' Tr',   # Set text rendering mode
            ' Ts',   # Set text rise
            ' Tc',   # Set character spacing
        ]):
            continue

        # Skip font resource definitions (optional, but helps)
        if '/Font' in line or '/Type' in line and 'Font' in ''.join(lines[max(0, lines.index(line)-2):lines.index(line)+2]):
            continue

        filtered_lines.append(line)

    result = '\n'.join(filtered_lines)
    return result.encode('latin-1', errors='ignore')

if __name__ == "__main__":
    remove_text_layer_v2("lady.pdf", "lady_clean.pdf")
