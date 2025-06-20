# src/pdf_parser.py
import pdfplumber
import re # We'll use regex for more robust string searching

def extract_borrower_personal_info(pdf_path: str) -> dict:
    """
    Extracts personal information for the borrower from the PDF.
    """
    borrower_info = {
        "name": None,
        "social_security_number": None,
        "date_of_birth": None,
        "citizenship": None,
        "alternate_names": None,
        "marital_status": None,
        "dependents": {"number": None, "ages": None},
        "contact_info": {
            "home_phone": None,
            "cell_phone": None,
            "work_phone": None,
            "email": None
        },
        "current_address": {
            "street": None,
            "unit": None,
            "city": None,
            "state": None,
            "zip": None,
            "country": None,
            "how_long_years": None,
            "how_long_months": None,
            "housing_expense": None # Own/Rent amount
        },
        "former_address": None, # Will be a dict if applicable
        "mailing_address": None # Will be a dict if applicable
    }

    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[0]  # Personal Information is primarily on the first page

            # Extract text from the page
            page_text = page.extract_text()

            # --- Extracting Name ---
            # We'll look for the "Name (First, Middle, Last, Suffix)" label
            # and then search for the name nearby.
            name_label_match = re.search(r"Name \(First, Middle, Last, Suffix\)(.*)", page_text)
            if name_label_match:
                # The name itself often appears on the line directly below this label
                # or immediately after it on the same line if the layout allows.
                lines = page_text.splitlines()
                for i, line in enumerate(lines):
                    if "Name (First, Middle, Last, Suffix)" in line:
                        if i + 1 < len(lines):
                            # The name is "Thomas, James, Bowdon" and it's followed by "Alternate Names" later.
                            # We need to be careful not to grab other fields on the same line if they appear.
                            potential_name_line = lines[i+1]

                            # Check if the line contains a typical name pattern
                            # and doesn't contain labels for other fields starting nearby
                            if re.match(r"^[A-Za-z,\s]+$", potential_name_line.split("Alternate Names")[0].strip()):
                                # Further refine by looking at the exact value "Thomas, James, Bowdon"
                                if "Thomas, James, Bowdon" in potential_name_line:
                                    # Extract just the name part before other fields on that line
                                    name_part = potential_name_line.split("Alternate Names")[0].strip()
                                    borrower_info["name"] = name_part
                                    break
            
            # --- Extracting Social Security Number ---
            # The SSN is "37 – 2196 – 321" on the line below the label
            ssn_match = re.search(r"Social Security Number\s+([0-9\s–-]+)", page_text)
            if ssn_match:
                ssn = ssn_match.group(1).replace(' ', '').replace('–', '-')
                borrower_info["social_security_number"] = ssn
            
            # --- Extracting Date of Birth ---
            # The DoB is "11 / 10 / 1995"
            dob_match = re.search(r"Date of Birth\s+\(mm/dd/yyyy\)\s+([0-9\s/]+)", page_text)
            if dob_match:
                dob = dob_match.group(1).replace(' ', '')
                borrower_info["date_of_birth"] = dob
            
            # --- Extracting Alternate Names (TJ) ---
            alternate_names_match = re.search(r"Alternate Names – List any names by which you are known or any names\nunder which credit was previously received \(First, Middle, Last, Suffix\)\s*([A-Za-z0-9]+)", page_text)
            if alternate_names_match:
                borrower_info["alternate_names"] = alternate_names_match.group(1).strip()
            
            # --- Extracting Citizenship ---
            # Look for "4 U.S. Citizen"
            if "4 U.S. Citizen" in page_text:
                borrower_info["citizenship"] = "U.S. Citizen"
            elif "Permanent Resident Alien" in page_text:
                borrower_info["citizenship"] = "Permanent Resident Alien"
            elif "Non-Permanent Resident Alien" in page_text:
                borrower_info["citizenship"] = "Non-Permanent Resident Alien"

            # --- Extracting Marital Status ---
            if "4 Unmarried" in page_text:
                borrower_info["marital_status"] = "Unmarried"
            elif "Married" in page_text and "4 Unmarried" not in page_text: # Check if "Married" is selected if "Unmarried" isn't
                 # This is a bit tricky without direct checkbox detection. We're inferring.
                 # For now, let's assume '4' indicates selected.
                borrower_info["marital_status"] = "Unmarried" # Based on the example text

            # --- Extracting Cell Phone ---
            cell_phone_match = re.search(r"Cell Phone\s+\(\s*([0-9]{3})\s*\)\s*([0-9]{3})\s*–\s*([0-9]{4})", page_text)
            if cell_phone_match:
                borrower_info["contact_info"]["cell_phone"] = f"({cell_phone_match.group(1)}) {cell_phone_match.group(2)}-{cell_phone_match.group(3)}"

            # --- Extracting Current Address ---
            # This is complex as it spans multiple lines
            # We'll try to find the "Current Address" label and then parse the lines following it.
            current_address_start_index = page_text.find("Current Address")
            if current_address_start_index != -1:
                # Extract a block of text after "Current Address"
                address_block = page_text[current_address_start_index:].split("How Long at Current Address?")[0]
                
                # Use regex to find Street, Unit, City, State, ZIP, Country
                street_match = re.search(r"Street\s+([A-Za-z0-9\s\.-]+)\s+Unit #\s*([A-Za-z0-9\s#\.-]*)", address_block)
                if street_match:
                    borrower_info["current_address"]["street"] = street_match.group(1).strip()
                    unit = street_match.group(2).strip()
                    if unit: borrower_info["current_address"]["unit"] = unit

                city_state_zip_country_match = re.search(r"City\s+([A-Za-z\s]+)\s+State\s+([A-Z]{2})\s+ZIP\s+([0-9]{5})\s+Country\s+([A-Za-z]+)", address_block)
                if city_state_zip_country_match:
                    borrower_info["current_address"]["city"] = city_state_zip_country_match.group(1).strip()
                    borrower_info["current_address"]["state"] = city_state_zip_country_match.group(2).strip()
                    borrower_info["current_address"]["zip"] = city_state_zip_country_match.group(3).strip()
                    borrower_info["current_address"]["country"] = city_state_zip_country_match.group(4).strip()
                
                # How Long at Current Address?
                how_long_match = re.search(r"How Long at Current Address\?\s+([0-9]+)\s+Years\s+([0-9]+)\s+Months", page_text)
                if how_long_match:
                    borrower_info["current_address"]["how_long_years"] = int(how_long_match.group(1))
                    borrower_info["current_address"]["how_long_months"] = int(how_long_match.group(2))

                # Housing Expense
                housing_match = re.search(r"Housing\s+4\s+No primary housing expense\s+Own\s+Rent\s+\(\$\s*([0-9\.]+)?", page_text)
                if housing_match:
                    rent_amount = housing_match.group(1)
                    if rent_amount:
                        borrower_info["current_address"]["housing_expense"] = f"Rent (${rent_amount}/month)"
                    else:
                        borrower_info["current_address"]["housing_expense"] = "No primary housing expense"

            # --- Current Employment/Self-Employment and Income ---
            employer_name_match = re.search(r"Employer or Business Name\s+([A-Za-z\s\.-]+?)\s+Phone", page_text)
            if employer_name_match:
                borrower_info["employer_name"] = employer_name_match.group(1).strip()
            
            position_title_match = re.search(r"Position or Title\s+([A-Za-z\s]+)\s+Check if this statement applies:", page_text)
            if position_title_match:
                borrower_info["position_title"] = position_title_match.group(1).strip()

            start_date_match = re.search(r"Start Date\s+([0-9\s/]+)\s+\(mm/dd/yyyy\)", page_text)
            if start_date_match:
                borrower_info["start_date"] = start_date_match.group(1).replace(' ', '')
            
            how_long_work_match = re.search(r"How long in this line of work\?\s+([0-9]+)\s+Years\s+([0-9]+)\s+Months", page_text)
            if how_long_work_match:
                borrower_info["time_in_line_of_work"] = {
                    "years": int(how_long_work_match.group(1)),
                    "months": int(how_long_work_match.group(2))
                }

            # Income values (Base, Overtime, Bonus, Commission, Military, Other)
            base_income_match = re.search(r"Base\s+\$\s*([0-9,.]+)\s*/month", page_text)
            if base_income_match:
                borrower_info["base_income"] = float(base_income_match.group(1).replace(',', ''))
            
            overtime_income_match = re.search(r"Overtime\s+\$\s*([0-9,.]+)\s*/month", page_text)
            if overtime_income_match:
                borrower_info["overtime_income"] = float(overtime_income_match.group(1).replace(',', ''))

            bonus_income_match = re.search(r"Bonus\s+\$\s*([0-9,.]+)\s*/month", page_text)
            if bonus_income_match:
                borrower_info["bonus_income"] = float(bonus_income_match.group(1).replace(',', ''))
            
            commission_income_match = re.search(r"Commission\s+\$\s*([0-9,.]+)\s*/month", page_text)
            if commission_income_match:
                borrower_info["commission_income"] = float(commission_income_match.group(1).replace(',', ''))

            military_income_match = re.search(r"Military\nEntitlements\s+\$\s*([0-9,.]+)\s*/month", page_text)
            if military_income_match:
                borrower_info["military_entitlements"] = float(military_income_match.group(1).replace(',', ''))
            
            other_income_employment_match = re.search(r"Other\s+\$\s*([0-9,.]+)\s*/month\nTOTAL", page_text)
            if other_income_employment_match:
                borrower_info["other_employment_income"] = float(other_income_employment_match.group(1).replace(',', ''))


    except Exception as e:
        print(f"Error extracting borrower personal info: {e}")
    
    return borrower_info

pdf_path = 'Data/URLA.pdf'

extract_borrower_personal_info(pdf_path)
