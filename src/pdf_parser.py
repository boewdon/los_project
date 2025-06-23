# src/pdf_parser.py
import pdfplumber
import re
from typing import Dict, List

def extract_borrower_personal_info(pdf_path: str) -> dict:
    """
    Extracts information from all sections of the URLA PDF based on raw text analysis.
    This version uses highly specific anchors for each field to handle jumbled text.
    """
    # Initialize the main data structure
    extracted_data = {
        "borrower_info": {"dependents": {}, "contact_info": {}, "current_address": {}},
        "employment_info": {
            "current_employment": {"gross_monthly_income": {}, "address": {}, "how_long_in_work": {}},
            "additional_employment": {"gross_monthly_income": {}, "address": {}, "how_long_in_work": {}}
        },
        "other_income_sources": [], "assets": {"bank_retirement_other": [], "other_assets_credits": []},
        "liabilities": {"credit_cards_debts_leases": [], "other_liabilities_expenses": []},
        "real_estate_owned": [], "loan_property_info": {"property_address": {}},
        "other_new_mortgage_loans": [], "rental_income_on_property": {}, "gifts_grants": [],
        "declarations": {}, "military_service": {},
        "demographic_info": {"ethnicity": [], "race": [], "do_not_wish_to_provide": {}},
        "loan_originator_info": {}
    }

    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                page_text = page.extract_text(x_tolerance=1)
                if page_text:
                    full_text += page_text + "\n"

            # --- Section 1: Borrower Info ---
            if m := re.search(r"Name \(First, Middle, Last, Suffix\).*?\n.*?\n([^\n]+)", full_text): extracted_data["borrower_info"]["name"] = m.group(1).strip()
            if m := re.search(r"Social Security Number\s+([\d\s–-]+)", full_text): extracted_data["borrower_info"]["social_security_number"] = m.group(1).replace('–', '-').replace(' ', '').strip()
            if m := re.search(r"Alternate Names[^\n]+\n([^\n]+)", full_text): extracted_data["borrower_info"]["alternate_names"] = m.group(1).strip()
            if m := re.search(r"T\.A\.\s+([\d\s/]+)\s+Permanent", full_text): extracted_data["borrower_info"]["date_of_birth"] = m.group(1).replace(" ", "")
            if re.search(r"4 U\.S\. Citizen", full_text): extracted_data["borrower_info"]["citizenship"] = "U.S. Citizen"
            if re.search(r"4 Unmarried", full_text): extracted_data["borrower_info"]["marital_status"] = "Unmarried"
            if m := re.search(r"Email\s+([\w.@]+)", full_text): extracted_data["borrower_info"]["contact_info"]["email"] = m.group(1).strip()
            if m := re.search(r"Home Phone\s+\(.*?(\d{3}).*?([\d\s–]+)", full_text): extracted_data["borrower_info"]["contact_info"]["home_phone"] = f"({m.group(1)}) {m.group(2).replace('–', '-').replace(' ', '').strip()}"
            if m := re.search(r"Cell Phone\s+\(.*?(\d{3}).*?([\d\s–]+)", full_text): extracted_data["borrower_info"]["contact_info"]["cell_phone"] = f"({m.group(1)}) {m.group(2).replace('–', '-').replace(' ', '').strip()}"
            if m := re.search(r"Work Phone\s+\(.*?(\d{3}).*?(\d{3}).*?(\d{4}).*?Ext\.\s*(\d+)", full_text): extracted_data["borrower_info"]["contact_info"]["work_phone"] = f"({m.group(1)}) {m.group(2)}-{m.group(3)} Ext. {m.group(4)}"
            if m := re.search(r"Current Address\nStreet\s+([\w\s.]+)\s+Unit #\s+([\w\d]+)\nCity\s+([\w\s]+)\s+State\s+(\w{2})\s+ZIP\s+(\d+)\s+Country\s+(\w+)", full_text):
                addr = extracted_data["borrower_info"]["current_address"]
                addr["street"], addr["unit"], addr["city"], addr["state"], addr["zip"], addr["country"] = [s.strip() for s in m.groups()]
            if m := re.search(r"How Long at Current Address\?\s+(\d+)\s+Years\s+(\d+)\s+Months", full_text):
                extracted_data["borrower_info"]["current_address"]["how_long_years"], extracted_data["borrower_info"]["current_address"]["how_long_months"] = int(m.group(1)), int(m.group(2))
            if re.search(r"Housing No primary housing expense\s+4\s+Own", full_text): extracted_data["borrower_info"]["current_address"]["housing_expense"] = "Own"

            # --- Sections 1b & 1c: Employment ---
            for section_id, emp_key in [("1b", "current_employment"), ("1c", "additional_employment")]:
                if emp_block_match := re.search(fr"{section_id}\.([\s\S]+?)(?=\n1[c-e]\.|\nSection 2:)", full_text):
                    emp_block = emp_block_match.group(1)
                    emp_data = extracted_data["employment_info"][emp_key]
                    if m := re.search(r"Employer or Business Name\s+([^\s]+)", emp_block): emp_data["employer_name"] = m.group(1)
                    if m := re.search(r"Phone\s+\(([\d\s]+)\)\s+([\d\s–]+)", emp_block): emp_data["phone"] = f"({m.group(1).strip()}) {m.group(2).replace('–','-').replace(' ','').strip()}"
                    if m := re.search(r"Position or Title\s+([^\n]+?)(?=\s+Check)", emp_block): emp_data["position_title"] = m.group(1).strip()
                    if m := re.search(r"Start Date\s+([^\(]+)", emp_block): emp_data["start_date"] = m.group(1).replace(" ", "")
                    if m := re.search(r"How long in this line of work\?\s+(\d+)\s+Years\s+(\d+)\s+Months", emp_block):
                        emp_data["how_long_in_work"]["years"], emp_data["how_long_in_work"]["months"] = int(m.group(1)), int(m.group(2))
                    income = emp_data["gross_monthly_income"]
                    if m := re.search(r"Base\s+\$\s+([\d,./]+)", emp_block): income["base"] = float(m.group(1).replace(",", "").split('/')[0])
                    if m := re.search(r"Overtime\s+\$\s+([\d,./]+)", emp_block): income["overtime"] = float(m.group(1).replace(",", "").split('/')[0])
                    if m := re.search(r"Bonus\s+\$\s+([\d,./]+)", emp_block): income["bonus"] = float(m.group(1).replace(",", "").split('/')[0])
                    if m := re.search(r"Commission\s+\$\s+([\d,./]+)", emp_block): income["commission"] = float(m.group(1).replace(",", "").split('/')[0])
                    if m := re.search(r"Street\s+([^\n]+?)\s+Unit #\s+([^\n]+)\nCity\s+([^\n]+?)\s+State\s+([A-Z]{2})\s+ZIP\s+(\d+)\s+Country\s+([A-Z]+)", emp_block):
                        addr = emp_data["address"]
                        addr["street"], addr["unit"], addr["city"], addr["state"], addr["zip"], addr["country"] = [s.strip() for s in m.groups()]

            # --- Section 1e: Other Income ---
            if m := re.search(r"Social Security\s+\$\s+([\d,]+)", full_text):
                extracted_data["other_income_sources"].append({"source": "Social Security", "monthly_income": float(m.group(1).replace(",", ""))})

            # --- Section 2: Assets & Liabilities ---
            asset_rows = re.findall(r"\n(Checking|Savings|Stocks)\s+([\w\s]+)\s+([\d-]+)\s+\$\s+([\d,]+)", full_text)
            for row in asset_rows:
                extracted_data["assets"]["bank_retirement_other"].append({"account_type": row[0], "financial_institution": row[1].strip(), "account_number": row[2], "cash_or_market_value": float(row[3].replace(",", ""))})
            if m := re.search(r"Earnest Money\s+\$\s+([\d,]+)", full_text):
                extracted_data["assets"]["other_assets_credits"].append({"asset_or_credit_type": "Earnest Money", "cash_or_market_value": float(m.group(1).replace(",", ""))})

            # --- Section 4: Loan and Property ---
            loan_info = extracted_data["loan_property_info"]
            if m := re.search(r"Loan Amount\s+\$\s([\d,]+)", full_text): loan_info["loan_amount"] = float(m.group(1).replace(",", ""))
            if re.search(r"Loan Purpose\s+4\s+Purchase", full_text): loan_info["loan_purpose"] = "Purchase"

    except Exception as e:
        print(f"An error occurred during parsing: {e}")

    return extracted_data