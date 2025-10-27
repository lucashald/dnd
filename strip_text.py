#!/usr/bin/env python3
import re

# Read the PDF
with open('lady.pdf', 'rb') as f:
    pdf = f.read()

# Remove text objects: everything between BT and ET
pdf_str = pdf.decode('latin-1', errors='ignore')

# Remove BT...ET blocks (text objects)
pdf_str = re.sub(r'BT\s.*?\sET\s', '', pdf_str, flags=re.DOTALL)

# Encode back
pdf_out = pdf_str.encode('latin-1', errors='ignore')

# Write output
with open('lady_clean.pdf', 'wb') as f:
    f.write(pdf_out)

print("Done - saved to lady_clean.pdf")
