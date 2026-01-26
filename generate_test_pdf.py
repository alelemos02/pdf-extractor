from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

def create_test_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Page 1 - Text and Table
    c.drawString(100, 750, "Test PDF Page 1")
    c.drawString(100, 730, "This is a searchable PDF.")
    
    # Draw a simple grid for a table
    data = [["Col1", "Col2", "Col3"], ["A", "B", "C"], ["1", "2", "3"]]
    x_start = 100
    y_start = 700
    row_height = 20
    col_width = 50
    
    for i, row in enumerate(data):
        y = y_start - (i * row_height)
        for j, cell in enumerate(row):
            x = x_start + (j * col_width)
            c.drawString(x + 5, y + 5, cell)
            c.rect(x, y, col_width, row_height)
            
    c.showPage()
    
    # Page 2 - Text Only
    c.drawString(100, 750, "Test PDF Page 2")
    c.drawString(100, 730, "No table here.")
    c.showPage()
    
    # Page 3 - Image like text (but actually searchable for this test, let's keep it simple)
    c.drawString(100, 750, "Test PDF Page 3")
    c.save()

if __name__ == "__main__":
    create_test_pdf("test_document.pdf")
