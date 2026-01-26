import re
import pdfplumber

def is_searchable_pdf(file_buffer):
    """
    Checks if a PDF has extracting text.
    Returns:
        bool: True if text is detected, False otherwise.
    """
    try:
        with pdfplumber.open(file_buffer) as pdf:
            if not pdf.pages:
                return False
            
            # Check a few pages to see if there is text
            # We check the first up to 3 pages
            pages_to_check = pdf.pages[:3]
            for page in pages_to_check:
                text = page.extract_text()
                if text and len(text.strip()) > 0:
                    return True
            
            # If we checked pages and found no text, returns False
            return False
            
    except Exception as e:
        print(f"Error checking PDF: {e}")
        return False

def parse_page_selection(selection_str, total_pages):
    """
    Parses a string like "1, 3-5, 10" into a list of 0-based indices.
    
    Args:
        selection_str (str): The user input string.
        total_pages (int): Total number of pages in the PDF.
        
    Returns:
        list[int]: Sorted list of unique 0-based indices.
    """
    selection_str = selection_str.strip()
    if not selection_str:
        return []
    
    pages = set()
    parts = selection_str.split(',')
    
    for part in parts:
        part = part.strip()
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                # Handle generic user inputs like "5-3" by swapping or ignoring. Let's range min-max.
                # Also clamp to valid pages.
                s = max(1, min(start, end)) # 1-based
                e = min(total_pages, max(start, end)) # 1-based
                for p in range(s, e + 1):
                    pages.add(p - 1) # convert to 0-based
            except ValueError:
                continue
        else:
            try:
                p = int(part)
                if 1 <= p <= total_pages:
                    pages.add(p - 1)
            except ValueError:
                continue
                
    return sorted(list(pages))
