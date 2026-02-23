import pdfplumber
import re

# 1. We tell pdfplumber to open our file
with pdfplumber.open("dummy_invoice.pdf") as pdf:
    
    # 2. We grab the very first page of the document (Index 0)
    first_page = pdf.pages[0]
    
    # 3. We command it to extract all the text it sees into a single string
    raw_text = first_page.extract_text()

    print("------- ANALYSE DE LA FACTURE -------")

    # 2. REGEX MAGIC: Find the Invoice Number
    # \S+ means "grab all characters until the next space"
    match_facture = re.search(r'Facture N°:\s*(\S+)',raw_text)

    if match_facture:
        num_facture = match_facture.group(1) # .group(1) pulls out the exact match
        print(f"📄 Numéro de Facture : {num_facture}")

    # 3. REGEX MAGIC: Find the Total Amount
    # \d+ means "grab all the digits (numbers)"

    match_total = re.search(r"Total TTC :\s*(\d+)\s*DH",raw_text)
    
    if match_total:
        montant_total = match_total.group(1)
        print(f"💰 Montant Total TTC : {montant_total} DH")


    match_year = re.search(r"Date:.*(\d{4})\s*",raw_text)

    if match_year:
        year = match_year.group(1)
        print(f"🗓️  Delivery year : {year}")