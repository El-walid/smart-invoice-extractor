import io
import re
import pdfplumber
from datetime import datetime
from fastapi import FastAPI, File, UploadFile
from sqlalchemy.orm import Session
from database import SessionLocal, Client, Product, Invoice, Invoice_Item

app = FastAPI()

# Helper function to convert "February 26, 2026" into a database-friendly Date object
def parse_date(date_str):
    try:
        # Strips spaces and converts string to Date
        return datetime.strptime(date_str.strip(), "%B %d, %Y").date()
    except Exception:
        # Fallback to today if regex grabs something weird
        return datetime.now().date() 

@app.post("/extract_and_save")
async def extract_invoice(file: UploadFile = File(...)):
    # 1. READ THE UPLOADED PDF
    file_bytes = await file.read()
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        first_page = pdf.pages[0]
        raw_text = first_page.extract_text()
        table_data = first_page.extract_table()

    # 2. EXTRACT HEADER DATA (REGEX)
    # Using group(1) to pull the exact match from the parentheses
    invoice_num = re.search(r"INVOICE:\s*(#\S+)", raw_text).group(1)
    ice_num = re.search(r"ICE:\s*(\d+)", raw_text).group(1)
    date_str = re.search(r"Date:\s*([A-Za-z]+\s\d{1,2},\s\d{4})", raw_text).group(1)
    
    # Grab the string right after "Billed To:"
    client_match = re.search(r"Billed To:\s*\n?(.*?)\n", raw_text)
    client_name = client_match.group(1).strip() if client_match else "Unknown Client"

    # Grab the total, remove the comma, convert to float
    total_ttc_str = re.search(r"Total Amount Payable \(TTC\):\s*([\d,]+)", raw_text).group(1)
    total_ttc = float(total_ttc_str.replace(",", ""))
    
    invoice_date = parse_date(date_str)

    # 3. OPEN THE DATABASE CONNECTION
    db: Session = SessionLocal()
    
    try:
        # --- PHASE A: UPSERT THE CLIENT ---
        # Check if ICE already exists. If not, create them.
        client = db.query(Client).filter(Client.ice_number == ice_num).first()
        if not client:
            client = Client(company_name=client_name, address="Marrakech", ice_number=ice_num)
            db.add(client)
            db.flush() # Saves to DB temporarily to generate the new Client ID
            
        # --- PHASE B: CREATE THE INVOICE ---
        new_invoice = Invoice(
            client_id=client.id, 
            invoice_number=invoice_num, 
            date=invoice_date, 
            total_ttc=total_ttc
        )
        db.add(new_invoice)
        db.flush() # Generate the new Invoice ID

        # --- PHASE C: PROCESS THE TABLE ITEMS ---
        if table_data:
            # Slice [1:] to skip the header row
            for row in table_data[1:]:
                # Clean the data: remove newlines, commas, and convert types
                desc = row[0].replace("\n", " ").strip()
                qty = int(row[1])
                unit_price = float(row[2].replace(",", ""))
                
                # Check if Product exists. If not, create it.
                product = db.query(Product).filter(Product.description == desc).first()
                if not product:
                    product = Product(description=desc, standard_price=unit_price)
                    db.add(product)
                    db.flush() # Generate the new Product ID
                    
                # Link everything together in the Invoice_Items table
                new_item = Invoice_Item(
                    invoice_id=new_invoice.id,
                    product_id=product.id,
                    quantity=qty
                )
                db.add(new_item)
        
        # --- PHASE D: COMMIT EVERYTHING ---
        # If no errors happened, lock all the changes into Azure SQL permanently
        db.commit()
        
        return {
            "status": "Success! Database Updated.",
            "client": client.company_name,
            "invoice_number": new_invoice.invoice_number,
            "total_saved_ttc": new_invoice.total_ttc,
            "items_processed": len(table_data[1:]) if table_data else 0
        }
        
    except Exception as e:
        # If ANYTHING fails (Regex crash, bad data), rollback so we don't save half an invoice
        db.rollback()
        return {"error": f"Failed to process: {str(e)}"}
    finally:
        # Always close the connection
        db.close()