#!/usr/bin/env python3
"""
Remove text layer from PDF using binary stream manipulation.
This directly modifies PDF content streams to remove text operators.
"""

import re
from typing import List, Tuple

def remove_text_from_stream(data: bytes) -> bytes:
    """
    Remove text rendering operators from PDF content stream.

    Removes:
    - BT...ET blocks (text objects)
    - Text showing operators: Tj, TJ, ', "
    - Text positioning: Td, TD, T*, Tm
    - Font and text state: Tf, Tw, Tz, TL, Tr, Ts, Tc
    """

    try:
        # Try to decode as latin-1 or utf-8
        text = data.decode('utf-8', errors='ignore')
    except:
        try:
            text = data.decode('latin-1', errors='ignore')
        except:
            return data

    # Split into lines
    lines = text.split('\n')
    result_lines = []
    i = 0
    in_text_block = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Handle text blocks
        if stripped == 'BT':  # Begin Text
            in_text_block += 1
            i += 1
            continue
        elif stripped == 'ET':  # End Text
            if in_text_block > 0:
                in_text_block -= 1
            i += 1
            continue

        # Skip everything inside text blocks
        if in_text_block > 0:
            i += 1
            continue

        # Remove text operators
        # Match operators at end of line
        text_operators = [
            r' Tj$',      # Show text
            r' TJ$',      # Show text with positioning
            r" '$",       # Move to next line and show text
            r' "$',       # Set spacing and show text
            r' Td$',      # Text position
            r' TD$',      # Text position and leading
            r' T\*$',     # Next line
            r' Tm$',      # Text matrix
            r' Tw$',      # Word spacing
            r' Tz$',      # Horizontal scaling
            r' TL$',      # Text leading
            r' Tf$',      # Font and size
            r' Tr$',      # Rendering mode
            r' Ts$',      # Text rise
            r' Tc$',      # Character spacing
        ]

        # Check if line ends with any text operator
        is_text_op = False
        for op_pattern in text_operators:
            if re.search(op_pattern, stripped):
                is_text_op = True
                break

        if is_text_op:
            i += 1
            continue

        # Skip font resource definitions in dictionary context
        if re.match(r'/\w+\s+\d+\s+R$', stripped) and '/Font' in ''.join(lines[max(0, i-5):i]):
            i += 1
            continue

        # Keep everything else
        result_lines.append(line)
        i += 1

    result = '\n'.join(result_lines)
    try:
        return result.encode('utf-8')
    except:
        return result.encode('latin-1', errors='ignore')

def remove_text_from_pdf(input_path: str, output_path: str):
    """
    Remove text layer from PDF file.
    """
    print(f"Reading {input_path}...")

    with open(input_path, 'rb') as f:
        pdf_data = f.read()

    print("Processing PDF streams...")

    # Find all content streams in the PDF
    # Look for stream...endstream patterns
    stream_pattern = rb'stream\s*\n(.*?)\nendstream'

    def replace_stream(match):
        stream_content = match.group(1)
        cleaned = remove_text_from_stream(stream_content)
        return b'stream\n' + cleaned + b'\nendstream'

    # Replace all streams
    modified_data = re.sub(stream_pattern, replace_stream, pdf_data, flags=re.DOTALL)

    print(f"Writing {output_path}...")

    with open(output_path, 'wb') as f:
        f.write(modified_data)

    print(f"Successfully created {output_path}")

if __name__ == "__main__":
    remove_text_from_pdf("lady.pdf", "lady_clean.pdf")
