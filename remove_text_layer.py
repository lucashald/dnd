#!/usr/bin/env python3
"""
Remove text layer from PDF, keeping only image content.
Uses PyPDF2 to manipulate PDF structure.
"""

import PyPDF2
import sys
from pathlib import Path

def remove_text_layer(input_pdf, output_pdf):
    """
    Remove all text content from a PDF while preserving images.

    Args:
        input_pdf: Path to input PDF file
        output_pdf: Path to output PDF file
    """

    # Open the PDF
    with open(input_pdf, 'rb') as infile:
        pdf_reader = PyPDF2.PdfReader(infile)
        pdf_writer = PyPDF2.PdfWriter()

        print(f"Processing {len(pdf_reader.pages)} pages...")

        for page_num, page in enumerate(pdf_reader.pages):
            print(f"Processing page {page_num + 1}...")

            # Get the content stream
            if "/Contents" in page:
                content = page["/Contents"]

                # Handle different content stream types
                if content is not None:
                    # Extract the content data
                    try:
                        if hasattr(content, 'get_data'):
                            content_data = content.get_data()
                        else:
                            # Try to get data from object
                            content_data = content.get_object().get_data()

                        # Remove text-related operators
                        # Common text operators: Tj, TJ, ', ", TD, Td, T*, Tm, Tw, Tz, TL, Tf, Tr, Ts
                        lines = content_data.decode('latin-1', errors='ignore').split('\n')
                        filtered_lines = []

                        in_text_object = False
                        for line in lines:
                            line_stripped = line.strip()

                            # Detect text objects
                            if line_stripped == 'BT':  # Begin text
                                in_text_object = True
                                continue
                            elif line_stripped == 'ET':  # End text
                                in_text_object = False
                                continue

                            # Skip text operators and font setting
                            if in_text_object:
                                continue

                            # Filter out text operators
                            text_operators = [' Tj', ' TJ', " '", ' "', ' Td', ' TD', ' T*',
                                            ' Tm', ' Tw', ' Tz', ' TL', ' Tf', ' Tr', ' Ts']

                            skip = False
                            for op in text_operators:
                                if line_stripped.endswith(op):
                                    skip = True
                                    break

                            if not skip:
                                filtered_lines.append(line)

                        # Update the content stream
                        new_content = '\n'.join(filtered_lines).encode('latin-1')
                        page["/Contents"] = PyPDF2.generic.ContentStream(
                            PyPDF2.generic.ArrayObject([
                                PyPDF2.generic.DictionaryObject({
                                    PyPDF2.generic.NameObject("/Length"): len(new_content)
                                }),
                                new_content
                            ]),
                            pdf_reader
                        )
                    except Exception as e:
                        print(f"Warning: Could not process page {page_num + 1}: {e}")
                        # Keep original page if processing fails

            pdf_writer.add_page(page)

        # Write the output PDF
        with open(output_pdf, 'wb') as outfile:
            pdf_writer.write(outfile)

        print(f"Successfully created {output_pdf}")

if __name__ == "__main__":
    input_file = "lady.pdf"
    output_file = "lady_clean.pdf"

    if not Path(input_file).exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)

    remove_text_layer(input_file, output_file)
