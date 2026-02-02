
import os
import io
import pandas as pd
from extractor import extract_tables_from_buffer
from utils import is_searchable_pdf

# Use the existing test document
file_path = "test_document.pdf"

print(f"Testing with file: {file_path}")

if not os.path.exists(file_path):
    print("Error: Test file not found!")
    exit(1)

with open(file_path, "rb") as f:
    # Read file into memory buffer to simulate Streamlit file_uploader
    file_buffer = io.BytesIO(f.read())

# 1. Test Searchable Check
print("\n--- Testing Searchable Check ---")
file_buffer.seek(0)
is_valid = is_searchable_pdf(file_buffer)
print(f"Is Searchable PDF: {is_valid}")

if not is_valid:
    print("Optimization: File is not searchable. Cannot extract tables.")
    exit(0)

# 2. Test Table Extraction
print("\n--- Testing Table Extraction (All Pages) ---")
file_buffer.seek(0)
tables = extract_tables_from_buffer(file_buffer, pages_indices=None)

if not tables:
    print("No tables found.")
else:
    print(f"Success! Found {len(tables)} tables.")
    for key, df in tables.items():
        print(f"\nTable: {key}")
        print(df.head())
        print(f"Shape: {df.shape}")

print("\n--- Verification Complete ---")
