#!/usr/bin/env python3
"""
Remove text layer from PDF using PyPDF2.
Creates a copy of pages with text streams removed.
"""

from PyPDF2 import PdfReader, PdfWriter
import sys

def remove_text_from_pdf(input_pdf, output_pdf):
    """
    Remove text from PDF by filtering content streams.
    """
    print(f"Opening {input_pdf}...", file=sys.stderr)

    try:
        with open(input_pdf, 'rb') as infile:
            reader = PdfReader(infile)
            writer = PdfWriter()

            total_pages = len(reader.pages)
            print(f"Total pages: {total_pages}", file=sys.stderr)

            for page_num, page in enumerate(reader.pages, 1):
                if page_num % 50 == 0 or page_num == 1:
                    print(f"Processing page {page_num}/{total_pages}...", file=sys.stderr)

                try:
                    # Try to remove text from content stream
                    if "/Contents" in page:
                        obj = page["/Contents"]

                        # Get the object
                        if hasattr(obj, 'get_object'):
                            obj = obj.get_object()

                        # Try to get data
                        if hasattr(obj, 'get_data'):
                            data = obj.get_data()

                            # Decode and process
                            try:
                                content_str = data.decode('latin-1', errors='ignore')
                            except:
                                content_str = str(data)

                            # Remove text operations
                            lines = content_str.split('\n')
                            filtered_lines = []
                            skip_until_ET = False

                            for line in lines:
                                stripped = line.strip()

                                # Skip BT...ET blocks
                                if stripped == 'BT':
                                    skip_until_ET = True
                                    continue
                                elif stripped == 'ET':
                                    skip_until_ET = False
                                    continue

                                if skip_until_ET:
                                    continue

                                # Skip text operators
                                skip_line = False
                                for op in [' Tj', ' TJ', " '", ' "', ' Td', ' TD', ' T*', ' Tm', ' Tw', ' Tz', ' TL', ' Tf', ' Tr', ' Ts', ' Tc']:
                                    if stripped.endswith(op):
                                        skip_line = True
                                        break

                                if not skip_line:
                                    filtered_lines.append(line)

                            # Update content
                            new_content = '\n'.join(filtered_lines)
                            from PyPDF2.generic import ByteStringObject
                            try:
                                page["/Contents"] = ByteStringObject(new_content.encode('latin-1', errors='ignore'))
                            except:
                                pass
                except Exception as e:
                    print(f"  Warning on page {page_num}: {type(e).__name__}", file=sys.stderr)

                # Add page to output
                writer.add_page(page)

            print(f"Writing output to {output_pdf}...", file=sys.stderr)
            with open(output_pdf, 'wb') as outfile:
                writer.write(outfile)

            print(f"Done! Created {output_pdf}", file=sys.stderr)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    remove_text_from_pdf("lady.pdf", "lady_clean.pdf")
