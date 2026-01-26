import pdfplumber
import pandas as pd
import io

def extract_tables_from_buffer(file_buffer, pages_indices=None):
    """
    Extracts tables from a PDF file buffer.
    
    Args:
        file_buffer: The file-like object containing the PDF.
        pages_indices (list of int, optional): 0-indexed page numbers to extract from.
                                               If None, extracts from all pages.
    
    Returns:
        dict: A dictionary where keys are "Page X Table Y" and values are DataFrames.
    """
    dataset = {}
    
    with pdfplumber.open(file_buffer) as pdf:
        # Determine which pages to process
        if pages_indices is None:
            pages_to_process = pdf.pages
        else:
            # Filter valid pages
            pages_to_process = []
            for idx in pages_indices:
                if 0 <= idx < len(pdf.pages):
                    pages_to_process.append(pdf.pages[idx])
        
        for i, page in enumerate(pages_to_process):
            # If specific indices were passed, we want to know the original page number (1-based)
            # pdf.pages is a list, so we can find the index if needed, or just track it.
            # To be safe and simple, let's trust the page.page_number if available or index.
            
            # pdfplumber page.page_number is usually 1-indexed
            page_num = page.page_number
            
            tables = page.extract_tables()
            
            for j, table in enumerate(tables):
                # Convert to DataFrame
                # We assume the first row might be headers, but often tables are messy.
                # Let's just create a raw DF for now. User might want to do header inference later.
                # For this MVP, we treat the first row as columns if it looks like one,
                # otherwise generic columns. Let's stick to raw generic for safety or basic inference.
                
                if not table:
                    continue
                    
                if not table:
                    continue
                    
                # Robust Header Handling
                if len(table) > 1:
                    headers = table[0]
                    data = table[1:]
                    
                    # Sanitize headers
                    clean_headers = []
                    counts = {}
                    
                    for h in headers:
                        # Handle None or whitespace
                        if h is None or str(h).strip() == "":
                            base_name = "Unnamed"
                        else:
                            base_name = str(h).strip()
                        
                        # Handle duplicates
                        if base_name in counts:
                            counts[base_name] += 1
                            clean_headers.append(f"{base_name}.{counts[base_name]}")
                        else:
                            counts[base_name] = 0
                            clean_headers.append(base_name)
                            
                    df = pd.DataFrame(data, columns=clean_headers)
                else:
                    # Table with only one row or just data
                    df = pd.DataFrame(table)
                
                # Check if empty
                if df.empty:
                    continue

                
                key = f"Pág {page_num} - Tab {j+1}"
                dataset[key] = df
                
    return dataset

def convert_to_excel(dataset):
    """
    Converts a dictionary of DataFrames to an Excel byte stream.
    """
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        if not dataset:
            # Create a dummy sheet if empty
            pd.DataFrame(["Nenhuma tabela encontrada"]).to_excel(writer, sheet_name="Info", header=False, index=False)
        else:
            for sheet_name, df in dataset.items():
                # Excel sheet names have limits (31 chars). Truncate if needed.
                safe_name = sheet_name[:31] 
                df.to_excel(writer, sheet_name=safe_name, index=False)
    
    return output.getvalue()
