from src.qbo.qbo import query

from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    tax_codes = query("select * from TaxCode").json()["QueryResponse"]["TaxCode"]
    for tax_code in tax_codes:
        print(tax_code["Id"], tax_code["Name"])
