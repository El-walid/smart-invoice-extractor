import pdfplumber
import re
from fastapi import FastAPI

# Initialize the API
app = FastAPI()

# Create the web endpoint
@app.get("/extract")
def extract_invoice():
    # 1. Open the PDF
    with pdfplumber.open("dummy_invoice.pdf") as pdf:
        first_page = pdf.pages[0]
        raw_text = first_page.extract_text()

    # 2. Extract Variables
    match_invoice = re.search(r'Invoice No:\s*(\S+)', raw_text)
    invoice_num = match_invoice.group(1) if match_invoice else "Not found"

    match_total = re.search(r"Total Amount :\s*(\d+)\s*DH", raw_text)
    total_amount = match_total.group(1) if match_total else "Not found"

    match_year = re.search(r"Date:.*(\d{4})", raw_text)
    year = match_year.group(1) if match_year else "Not found"

    # 3. Package into the JSON Dictionary
    invoice_data = {
        "invoice_number": invoice_num,
        "total_amount_dh": total_amount,
        "delivery_year": year
    }

    # API returns the JSON directly
    return invoice_data