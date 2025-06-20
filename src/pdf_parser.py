# src/pdf_parser.py
import pdfplumber
import re
from typing import Dict, Optional

def extract_borrower_personal_info(pdf_path: str) -> dict:
    """
    Extracts information from various sections of the URLA PDF.
    """
    extracted_data = {
        "borrower_info": {
            "name": None,
            "alternate_names": None,
            "social_security_number": None,
            "date_of_birth": None,
            "citizenship": None,
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
                "housing_expense": None
            },
            "former_address": None,
            "mailing_address": None
        },
        "employment_info": {
            "current_employment": {
                "employer_name": None,
                "phone": None,
                "gross_monthly_income": {
                    "base": None,
                    "overtime": None,
                    "bonus": None,
                    "commission": None,
                    "military_entitlements": None,
                    "other": None,
                    "total": None
                },
                "address": {
                    "street": None,
                    "unit": None,
                    "city": None,
                    "state": None,
                    "zip": None,
                    "country": None
                },
                "position_title": None,
                "start_date": None,
                "how_long_in_work": {"years": None, "months": None},
                "employed_by_family_member": None,
                "business_owner_or_self_employed": None,
                "ownership_share_less_25": None,
                "ownership_share_25_or_more": None,
                "monthly_income_loss": None
            },
            "additional_employment": { # Placeholder for Amazon
                "employer_name": None,
                "phone": None,
                "gross_monthly_income": {
                    "base": None,
                    "overtime": None,
                    "bonus": None,
                    "commission": None,
                    "military_entitlements": None,
                    "other": None,
                    "total": None
                },
                "position_title": None,
                "start_date": None,
                "how_long_in_work": {"years": None, "months": None}
            },
            "previous_employment": None # Placeholder
        },
        "other_income_sources": [],
        "assets": {
            "bank_retirement_other": [],
            "other_assets_credits": []
        },
        "liabilities": {
            "credit_cards_debts_leases": [],
            "other_liabilities_expenses": []
        },
        "real_estate_owned": [],
        "loan_property_info": {
            "loan_amount": None,
            "loan_purpose": None,
            "property_address": {
                "street": None,
                "unit": None,
                "city": None,
                "state": None,
                "zip": None,
                "county": None
            },
            "number_of_units": None,
            "property_value": None,
            "occupancy": None,
            "mixed_use_property": None,
            "manufactured_home": None
        },
        "other_new_mortgage_loans": [],
        "rental_income_on_property": {
            "expected_monthly_rental_income": None,
            "expected_net_monthly_rental_income": None
        },
        "gifts_grants": [],
        "declarations": {
            "occupy_primary_residence": None,
            "ownership_interest_in_other_property_past_3_years": None,
            "property_type_owned": None,
            "how_held_title": None,
            "family_business_affiliation_seller": None,
            "borrowing_other_money": None,
            "amount_of_other_money": None,
            "applying_for_other_mortgage": None,
            "applying_for_new_credit": None,
            "property_subject_to_lien": None,
            "co_signer_guarantor": None,
            "outstanding_judgments": None,
            "delinquent_federal_debt": None,
            "party_to_lawsuit": None,
            "conveyed_title_lieu_foreclosure": None,
            "pre_foreclosure_short_sale": None,
            "property_foreclosed_upon": None,
            "declared_bankruptcy": None,
            "bankruptcy_types": []
        },
        "military_service": {
            "ever_served": None,
            "currently_serving": None,
            "retired_discharged_separated": None,
            "non_activated_reserve_national_guard": None,
            "surviving_spouse": None
        },
        "demographic_info": {
            "ethnicity": [],
            "race": [],
            "sex": None,
            "do_not_wish_to_provide": {
                "ethnicity": None,
                "race": None,
                "sex": None
            }
        },
        "loan_originator_info": {
            "organization_name": None,
            "address": None,
            "nmlsr_id": None,
            "originator_name": None,
            "originator_nmlsr_id": None,
            "email": None,
            "state_license_id": None,
            "phone": None
        }
    }

    try:
        with pdfplumber.open(pdf_path) as pdf:
            full_text = ""
            for page in pdf.pages:
                full_text += page.extract_text() + "\n" # Add newline for consistent separation

            # Define regex patterns for section headers
            section_patterns = {
                "section_1": r"Section 1: Borrower Information\b",
                "section_2": r"Section 2: Financial Information - Assets and Liabilities\b",
                "section_3": r"Section 3: Financial Information\s+Real Estate\b",
                "section_4": r"Section 4: Loan and Property Information\b",
                "section_5": r"Section 5: Declarations\b",
                "section_6": r"Section 6: Acknowledgments and Agreements\b",
                "section_7": r"Section 7: Military Service\b",
                "section_8": r"Section 8: Demographic Information\b",
                "section_9": r"Section 9: Loan Originator Information\b"
            }

            # Find start and end indices for each section
            section_indices = {}
            section_names_ordered = list(section_patterns.keys())

            for i, section_key in enumerate(section_names_ordered):
                start_match = re.search(section_patterns[section_key], full_text)
                if start_match:
                    section_indices[section_key] = {"start": start_match.start()}
                    # Determine end of current section by start of next, or end of document
                    if i + 1 < len(section_names_ordered):
                        next_section_key = section_names_ordered[i+1]
                        # Search for next section from the end of the current section's start match
                        next_start_match = re.search(section_patterns[next_section_key], full_text[start_match.start():])
                        if next_start_match:
                            section_indices[section_key]["end"] = start_match.start() + next_start_match.start()
                        else:
                            section_indices[section_key]["end"] = len(full_text) # If next not found, it's till end
                    else:
                        section_indices[section_key]["end"] = len(full_text) # Last section goes to end of document
            
            # Extract text for each section
            sections_text: Dict[str, str] = {}
            for section_key, indices in section_indices.items():
                sections_text[section_key] = full_text[indices["start"]:indices["end"]]


            # --- Parsing Section 1: Borrower Information ---
            if "section_1" in sections_text:
                sec1_text = sections_text["section_1"]
                
                # Name: Adjusted to handle optional newlines and look for "Alternate Names" or "Social Security Number"
                name_match = re.search(r"Name \(First, Middle, Last, Suffix\)\s*[\r\n]*\s*([A-Za-z,\s.'-]+?)(?=\s*[\r\n]*\s*Alternate Names|\s*[\r\n]*\s*Social Security Number|\s*[\r\n]*\s*Date of Birth)", sec1_text)
                if name_match:
                    extracted_data["borrower_info"]["name"] = name_match.group(1).strip()
                
                # Alternate Names: Adjusted for optional newlines and lookahead
                alternate_names_match = re.search(r"Alternate Names - List any names by which you are known or any names\s*under which credit was previously received \(First, Middle, Last, Suffix\)\s*([\r\n]*\s*[A-Za-z0-9\s.'-]+?)(?=\s*[\r\n]*\s*Social Security Number|\s*[\r\n]*\s*Date of Birth)", sec1_text)
                if alternate_names_match:
                    extracted_data["borrower_info"]["alternate_names"] = alternate_names_match.group(1).strip()

                # Social Security Number
                ssn_match = re.search(r"Social Security Number\s+([0-9\s-]+)", sec1_text)
                if ssn_match:
                    extracted_data["borrower_info"]["social_security_number"] = ssn_match.group(1).replace(' ', '')
                
                # Date of Birth: Adjusted for optional newlines/spaces
                dob_match = re.search(r"Date of Birth\s*\(mm/dd/yyyy\)\s*([0-9/]+)", sec1_text)
                if dob_match:
                    extracted_data["borrower_info"]["date_of_birth"] = dob_match.group(1).strip()

                # Citizenship (using more precise regex for checkboxes)
                if re.search(r"U\.S\. Citizen\s*☑", sec1_text):
                    extracted_data["borrower_info"]["citizenship"] = "U.S. Citizen"
                elif re.search(r"Permanent Resident Alien\s*☑", sec1_text):
                    extracted_data["borrower_info"]["citizenship"] = "Permanent Resident Alien"
                elif re.search(r"Non-Permanent Resident Alien\s*☑", sec1_text):
                    extracted_data["borrower_info"]["citizenship"] = "Non-Permanent Resident Alien"
                
                # Marital Status (using more precise regex for checkboxes)
                if re.search(r"Unmarried\s*☑", sec1_text):
                    extracted_data["borrower_info"]["marital_status"] = "Unmarried"
                elif re.search(r"Married\s*☑", sec1_text): # Assuming checkbox marks selection
                    extracted_data["borrower_info"]["marital_status"] = "Married"
                elif re.search(r"Separated\s*☑", sec1_text):
                    extracted_data["borrower_info"]["marital_status"] = "Separated"

                # Dependents
                dependents_match = re.search(r"Dependents \(not listed by another Borrower\)\s*\nNumber\s*(\d+)?\s*Ages\s*(\d+)?", sec1_text)
                if dependents_match:
                    extracted_data["borrower_info"]["dependents"]["number"] = int(dependents_match.group(1)) if dependents_match.group(1) else None
                    extracted_data["borrower_info"]["dependents"]["ages"] = int(dependents_match.group(2)) if dependents_match.group(2) else None
                
                # Contact Information - Phone Numbers (made patterns more flexible for common formats)
                home_phone_match = re.search(r"Home Phone\s*[\r\n]*\s*\(?(\d{3})\)?[\s.-]*(\d{3})[\s.-]*(\d{4})", sec1_text)
                if home_phone_match:
                    extracted_data["borrower_info"]["contact_info"]["home_phone"] = f"({home_phone_match.group(1)}) {home_phone_match.group(2)}-{home_phone_match.group(3)}"
                
                cell_phone_match = re.search(r"Cell Phone\s*[\r\n]*\s*\(?(\d{3})\)?[\s.-]*(\d{3})[\s.-]*(\d{4})", sec1_text)
                if cell_phone_match:
                    extracted_data["borrower_info"]["contact_info"]["cell_phone"] = f"({cell_phone_match.group(1)}) {cell_phone_match.group(2)}-{cell_phone_match.group(3)}"

                work_phone_match = re.search(r"Work Phone\s*[\r\n]*\s*\(?(\d{3})\)?[\s.-]*(\d{3})[\s.-]*(\d{4})(?:\s*Ext\.\s*(\d+))?", sec1_text)
                if work_phone_match:
                    phone_num = f"({work_phone_match.group(1)}) {work_phone_match.group(2)}-{work_phone_match.group(3)}"
                    if work_phone_match.group(4):
                        phone_num += f" Ext. {work_phone_match.group(4)}"
                    extracted_data["borrower_info"]["contact_info"]["work_phone"] = phone_num
                
                email_match = re.search(r"Email\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", sec1_text)
                if email_match:
                    extracted_data["borrower_info"]["contact_info"]["email"] = email_match.group(1).strip()
                
                # Current Address
                # Making street and unit non-greedy and adding lookaheads for next fields
                current_address_start_idx = sec1_text.find("Current Address")
                current_address_end_idx = sec1_text.find("How Long at Current Address?")
                if current_address_start_idx != -1 and current_address_end_idx != -1:
                    address_block = sec1_text[current_address_start_idx:current_address_end_idx]

                    street_match = re.search(r"Street\s+([A-Za-z0-9\s.,#-]+?)\s+(?:Unit #\s*([A-Za-z0-9#-]*))?", address_block)
                    if street_match:
                        extracted_data["borrower_info"]["current_address"]["street"] = street_match.group(1).strip()
                        extracted_data["borrower_info"]["current_address"]["unit"] = street_match.group(2).strip() if street_match.group(2) else None

                    city_state_zip_country_match = re.search(r"City\s+([A-Za-z\s.-]+?)\s+State\s+([A-Z]{2})\s+ZIP\s+([0-9]{5})\s+Country\s+([A-Za-z]+)", address_block)
                    if city_state_zip_country_match:
                        extracted_data["borrower_info"]["current_address"]["city"] = city_state_zip_country_match.group(1).strip()
                        extracted_data["borrower_info"]["current_address"]["state"] = city_state_zip_country_match.group(2).strip()
                        extracted_data["borrower_info"]["current_address"]["zip"] = city_state_zip_country_match.group(3).strip()
                        extracted_data["borrower_info"]["current_address"]["country"] = city_state_zip_country_match.group(4).strip()
                
                how_long_current_address_match = re.search(r"How Long at Current Address\?\s*(\d+)\s*Years\s*(\d+)\s*Months", sec1_text)
                if how_long_current_address_match:
                    extracted_data["borrower_info"]["current_address"]["how_long_years"] = int(how_long_current_address_match.group(1))
                    extracted_data["borrower_info"]["current_address"]["how_long_months"] = int(how_long_current_address_match.group(2))

                # Housing Expense (corrected checkbox parsing)
                if re.search(r"No primary housing expense\s*☑", sec1_text):
                    extracted_data["borrower_info"]["current_address"]["housing_expense"] = "No primary housing expense"
                elif re.search(r"Own\s*☑", sec1_text):
                    extracted_data["borrower_info"]["current_address"]["housing_expense"] = "Own"
                elif re.search(r"Rent\s+\(\$([\d,.]+)/month\)\s*☑", sec1_text):
                    rent_match = re.search(r"Rent\s+\(\$([\d,.]+)/month\)\s*☑", sec1_text)
                    if rent_match:
                        extracted_data["borrower_info"]["current_address"]["housing_expense"] = f"Rent (${float(rent_match.group(1).replace(',', ''))}/month)"


                # Current Employment (made employer name non-greedy, position title more precise)
                emp_start_idx = sec1_text.find("Current Employment/Self-Employment and Income")
                if emp_start_idx != -1:
                    emp_block = sec1_text[emp_start_idx:]
                    
                    emp_name_match = re.search(r"Employer or Business Name\s+([A-Za-z\s.-]+?)\s+Phone", emp_block)
                    if emp_name_match:
                        extracted_data["employment_info"]["current_employment"]["employer_name"] = emp_name_match.group(1).strip()
                    
                    emp_phone_match = re.search(r"Phone\s+\(?(\d{3})\)?[\s.-]*(\d{3})[\s.-]*(\d{4})", emp_block) # More flexible phone number format
                    if emp_phone_match:
                        extracted_data["employment_info"]["current_employment"]["phone"] = f"({emp_phone_match.group(1)}) {emp_phone_match.group(2)}-{emp_phone_match.group(3)}"
                    
                    # Position Title: made non-greedy and looks ahead for "Start Date" or "How long"
                    position_match = re.search(r"Position or Title\s+([A-Za-z\s.-]+?)(?=\s*Start Date|\s*How long in this line of work\?)", emp_block)
                    if position_match:
                        extracted_data["employment_info"]["current_employment"]["position_title"] = position_match.group(1).strip()
                    
                    start_date_match = re.search(r"Start Date\s+([0-9/ ]+)\s+\(mm/dd/yyyy\)", emp_block)
                    if start_date_match:
                        extracted_data["employment_info"]["current_employment"]["start_date"] = start_date_match.group(1).replace(' ', '')
                    
                    how_long_match = re.search(r"How long in this line of work\?\s*(\d+)\s*Years\s*(\d+)\s*Months", emp_block)
                    if how_long_match:
                        extracted_data["employment_info"]["current_employment"]["how_long_in_work"]["years"] = int(how_long_match.group(1))
                        extracted_data["employment_info"]["current_employment"]["how_long_in_work"]["months"] = int(how_long_match.group(2))
                    
                    # Income details for current employment (used \$ for literal dollar sign)
                    base_income_match = re.search(r"Base\s+\$([\d,.]+)/month", emp_block)
                    if base_income_match:
                        extracted_data["employment_info"]["current_employment"]["gross_monthly_income"]["base"] = float(base_income_match.group(1).replace(',', ''))
                    
                    overtime_income_match = re.search(r"Overtime\s+\$([\d,.]+)/month", emp_block)
                    if overtime_income_match:
                        extracted_data["employment_info"]["current_employment"]["gross_monthly_income"]["overtime"] = float(overtime_income_match.group(1).replace(',', ''))
                    
                    bonus_income_match = re.search(r"Bonus\s+\$([\d,.]+)/month", emp_block)
                    if bonus_income_match:
                        extracted_data["employment_info"]["current_employment"]["gross_monthly_income"]["bonus"] = float(bonus_income_match.group(1).replace(',', ''))
                    
                    commission_income_match = re.search(r"Commission\s+\$([\d,.]+)/month", emp_block)
                    if commission_income_match:
                        extracted_data["employment_info"]["current_employment"]["gross_monthly_income"]["commission"] = float(commission_income_match.group(1).replace(',', ''))

            # --- Parsing Section 1c: Additional Employment ---
            if "section_2" in sections_text: # Assuming section 1c often flows into page 2
                sec_1c_text_block = full_text # Search whole document for this section
                # Replaced hardcoded "Amazon" with a general capture group for employer name
                add_emp_name_match = re.search(r"Employer or Business Name\s+([A-Za-z\s.-]+?)\s+Phone\s*\(?(\d{3})\)?[\s.-]*(\d{3})[\s.-]*(\d{4})", sec_1c_text_block)
                if add_emp_name_match:
                    extracted_data["employment_info"]["additional_employment"]["employer_name"] = add_emp_name_match.group(1).strip()
                    extracted_data["employment_info"]["additional_employment"]["phone"] = f"({add_emp_name_match.group(2)}) {add_emp_name_match.group(3)}{add_emp_name_match.group(4)}"
                    
                    # Made address block detection dynamic by looking for "Street" followed by actual street
                    # and ending before "Position or Title"
                    add_emp_address_start_idx = re.search(r"Street\s+[A-Za-z0-9\s.-]+", sec_1c_text_block)
                    add_emp_address_end_idx = re.search(r"Position or Title", sec_1c_text_block)
                    
                    if add_emp_address_start_idx and add_emp_address_end_idx:
                        address_start = add_emp_address_start_idx.start()
                        address_end = add_emp_address_end_idx.start()
                        add_emp_address_block = sec_1c_text_block[address_start:address_end]

                        street_match = re.search(r"Street\s+([A-Za-z0-9\s.,#-]+?)\s*(?:Unit #\s*([A-Za-z0-9#-]*))?", add_emp_address_block) # Made non-greedy
                        if street_match:
                            extracted_data["employment_info"]["additional_employment"]["address"] = {
                                "street": street_match.group(1).strip(),
                                "unit": street_match.group(2).strip() if street_match.group(2) else None
                            }
                        city_state_zip_country_match = re.search(r"City\s+([A-Za-z\s.-]+?)\s+State\s+([A-Z]{2})\s+ZIP\s+([0-9]{5})\s+Country\s+([A-Za-z]+)", add_emp_address_block) # Made non-greedy
                        if city_state_zip_country_match:
                            # Ensure address dictionary is initialized before updating
                            if "address" not in extracted_data["employment_info"]["additional_employment"] or \
                               isinstance(extracted_data["employment_info"]["additional_employment"]["address"], dict): # Check if it's already a dict
                                extracted_data["employment_info"]["additional_employment"]["address"].update({
                                    "city": city_state_zip_country_match.group(1).strip(),
                                    "state": city_state_zip_country_match.group(2).strip(),
                                    "zip": city_state_zip_country_match.group(3).strip(),
                                    "country": city_state_zip_country_match.group(4).strip()
                                })
                            else: # If it's not a dict, reinitialize it
                                extracted_data["employment_info"]["additional_employment"]["address"] = {
                                    "city": city_state_zip_country_match.group(1).strip(),
                                    "state": city_state_zip_country_match.group(2).strip(),
                                    "zip": city_state_zip_country_match.group(3).strip(),
                                    "country": city_state_zip_country_match.group(4).strip()
                                }


                    add_emp_position_match = re.search(r"Position or Title\s+([A-Za-z\s]+)", sec_1c_text_block)
                    if add_emp_position_match:
                        extracted_data["employment_info"]["additional_employment"]["position_title"] = add_emp_position_match.group(1).strip()
                    
                    add_emp_start_date_match = re.search(r"Start Date\s+([0-9/ ]+)\s+\(mm/dd/yyyy\)", sec_1c_text_block)
                    if add_emp_start_date_match:
                        extracted_data["employment_info"]["additional_employment"]["start_date"] = add_emp_start_date_match.group(1).replace(' ', '')
                    
                    add_emp_how_long_match = re.search(r"How long in this line of work\?\s*(\d+)\s*Years\s*(\d+)\s*Months", sec_1c_text_block)
                    if add_emp_how_long_match:
                        extracted_data["employment_info"]["additional_employment"]["how_long_in_work"]["years"] = int(add_emp_how_long_match.group(1))
                        extracted_data["employment_info"]["additional_employment"]["how_long_in_work"]["months"] = int(add_emp_how_long_match.group(2))

                    # Income details for additional employment (using \$ for literal dollar sign)
                    add_emp_base_income_match = re.search(r"Base\s+\$([\d,.]+)/month", sec_1c_text_block)
                    if add_emp_base_income_match:
                        extracted_data["employment_info"]["additional_employment"]["gross_monthly_income"]["base"] = float(add_emp_base_income_match.group(1).replace(',', ''))
                    
                    add_emp_overtime_income_match = re.search(r"Overtime\s+\$([\d,.]+)/month", sec_1c_text_block)
                    if add_emp_overtime_income_match:
                        extracted_data["employment_info"]["additional_employment"]["gross_monthly_income"]["overtime"] = float(add_emp_overtime_income_match.group(1).replace(',', ''))
                    
                    add_emp_bonus_income_match = re.search(r"Bonus\s+\$([\d,.]+)/month", sec_1c_text_block)
                    if add_emp_bonus_income_match:
                        extracted_data["employment_info"]["additional_employment"]["gross_monthly_income"]["bonus"] = float(add_emp_bonus_income_match.group(1).replace(',', ''))
                    
                    add_emp_commission_income_match = re.search(r"Commission\s+\$([\d,.]+)/month", sec_1c_text_block)
                    if add_emp_commission_income_match:
                        extracted_data["employment_info"]["additional_employment"]["gross_monthly_income"]["commission"] = float(add_emp_commission_income_match.group(1).replace(',', ''))
                
            # --- Parsing Section 1e: Income from Other Sources ---
            # This section is typically found after Section 1c and before Section 2
            # Dynamically determine the end of this block using the start of Section 2
            if "section_2" in sections_text:
                income_sources_block_start = full_text.find("Income from Other Sources")
                
                # Use the start of Section 2 as the end delimiter for more dynamism
                income_sources_block_end = section_indices["section_2"]["start"] if "section_2" in section_indices else len(full_text)

                if income_sources_block_start != -1 and income_sources_block_start < income_sources_block_end:
                    income_sources_text = full_text[income_sources_block_start:income_sources_block_end]
                    
                    # Social Security example
                    ss_income_match = re.search(r"Social Security\s+\$([\d,.]+)", income_sources_text) # Changed 'S' to '\$'
                    if ss_income_match:
                        extracted_data["other_income_sources"].append({
                            "source": "Social Security",
                            "monthly_income": float(ss_income_match.group(1).replace(',', ''))
                        })

            # --- Parsing Section 2a: Assets - Bank Accounts, Retirement, and Other Accounts You Have ---
            if "section_2" in sections_text:
                sec2_text = sections_text["section_2"]
                # This section uses tables, so direct regex might be complex.
                # For now, let's parse the provided examples
                
                # Checking account - Replaced hardcoded bank name and account number with general capture groups
                checking_match = re.search(r"Checking\s+([A-Za-z\s.-]+?)\s+([\w\s-]+?)\s+\$([\d,.]+)", sec2_text) # Account num allows spaces
                if checking_match:
                    extracted_data["assets"]["bank_retirement_other"].append({
                        "account_type": "Checking",
                        "financial_institution": checking_match.group(1).strip(),
                        "account_number": checking_match.group(2).strip(),
                        "cash_or_market_value": float(checking_match.group(3).replace(',', ''))
                    })
                
                # Savings account - Replaced hardcoded bank name and account number with general capture groups
                savings_match = re.search(r"Savings\s+([A-Za-z\s.-]+?)\s+([\w\s-]+?)\s+\$([\d,.]+)", sec2_text) # Account num allows spaces, changed 'S' to '\$'
                if savings_match:
                    extracted_data["assets"]["bank_retirement_other"].append({
                        "account_type": "Savings",
                        "financial_institution": savings_match.group(1).strip(),
                        "account_number": savings_match.group(2).strip(),
                        "cash_or_market_value": float(savings_match.group(3).replace(',', ''))
                    })

                # Stocks - Replaced hardcoded financial institution and account number with general capture groups
                stocks_match = re.search(r"Stocks\s+([A-Za-z\s.-]+?)\s+([\w\s-]+?)\s+\$([\d,.]+)", sec2_text) # Account num allows spaces, changed 'S' to '\$'
                if stocks_match:
                    extracted_data["assets"]["bank_retirement_other"].append({
                        "account_type": "Stocks",
                        "financial_institution": stocks_match.group(1).strip(),
                        "account_number": stocks_match.group(2).strip(),
                        "cash_or_market_value": float(stocks_match.group(3).replace(',', ''))
                    })

            # --- Parsing Section 2b: Other Assets and Credits You Have ---
            if "section_2" in sections_text:
                sec2b_text = sections_text["section_2"]
                earnest_money_match = re.search(r"Earnest Money\s+\$([\d,.]+)", sec2b_text)
                if earnest_money_match:
                    extracted_data["assets"]["other_assets_credits"].append({
                        "asset_or_credit_type": "Earnest Money",
                        "cash_or_market_value": float(earnest_money_match.group(1).replace(',', ''))
                    })

            # --- Parsing Section 2c: Liabilities - Credit Cards, Other Debts, and Leases that You Owe ---
            if "section_2" in sections_text:
                sec2c_text = sections_text["section_2"]
                # Installment (first instance) - Replaced hardcoded bank name and account number with general capture groups
                first_installment_liability_match = re.search(r"Installment\s+([A-Za-z\s.-]+?)\s+([\w\s-]+?)\s+(?:(☑|☐)\s*)?\$([\d,.]+)\s+\$([\d,.]+)", sec2c_text) # Added explicit checkbox capture
                if first_installment_liability_match:
                    extracted_data["liabilities"]["credit_cards_debts_leases"].append({
                        "account_type": "Installment",
                        "company_name": first_installment_liability_match.group(1).strip(),
                        "account_number": first_installment_liability_match.group(2).strip(),
                        "unpaid_balance": float(first_installment_liability_match.group(4).replace(',', '')),
                        "monthly_payment": float(first_installment_liability_match.group(5).replace(',', '')),
                        "paid_off_at_closing": True if first_installment_liability_match.group(3) == '☑' else False
                    })
                
                # Revolving - Replaced hardcoded bank name and account number with general capture groups
                revolving_liability_match = re.search(r"Revolving\s+([A-Za-z\s.-]+?)\s+([\w\s-]+?)\s+\$([\d,.]+)\s+(?:(☑|☐)\s*)?\$([\d,.]+)", sec2c_text) # Added explicit checkbox capture
                if revolving_liability_match:
                    extracted_data["liabilities"]["credit_cards_debts_leases"].append({
                        "account_type": "Revolving",
                        "company_name": revolving_liability_match.group(1).strip(),
                        "account_number": revolving_liability_match.group(2).strip(),
                        "unpaid_balance": float(revolving_liability_match.group(3).replace(',', '')),
                        "monthly_payment": float(revolving_liability_match.group(5).replace(',', '')),
                        "paid_off_at_closing": True if revolving_liability_match.group(4) == '☑' else False
                    })
                
                # Installment (second instance) - Replaced hardcoded bank name and account number with general capture groups
                second_installment_liability_match = re.search(r"Installment\s+([A-Za-z\s.-]+?)\s+([A-Za-z0-9-]+?)\s+(?:(☑|☐)\s*)?\$([\d,.]+)\s+\$([\d,.]+)", sec2c_text) # Added explicit checkbox capture
                if second_installment_liability_match:
                    extracted_data["liabilities"]["credit_cards_debts_leases"].append({
                        "account_type": "Installment",
                        "company_name": second_installment_liability_match.group(1).strip(),
                        "account_number": second_installment_liability_match.group(2).strip(),
                        "unpaid_balance": float(second_installment_liability_match.group(4).replace(',', '')),
                        "monthly_payment": float(second_installment_liability_match.group(5).replace(',', '')),
                        "paid_off_at_closing": True if second_installment_liability_match.group(3) == '☑' else False
                    })
            
            # --- Parsing Section 2d: Other Liabilities and Expenses ---
            if "section_2" in sections_text:
                sec2d_text = sections_text["section_2"]
                child_support_match = re.search(r"Child Support\s+\$([\d,.]+)", sec2d_text)
                if child_support_match:
                    extracted_data["liabilities"]["other_liabilities_expenses"].append({
                        "type": "Child Support",
                        "monthly_payment": float(child_support_match.group(1).replace(',', ''))
                    })
                alimony_match = re.search(r"Alimony\s+\$([\d,.]+)", sec2d_text)
                if alimony_match:
                    extracted_data["liabilities"]["other_liabilities_expenses"].append({
                        "type": "Alimony",
                        "monthly_payment": float(alimony_match.group(1).replace(',', ''))
                    })

            # --- Parsing Section 3a: Property You Own ---
            if "section_3" in sections_text:
                sec3a_text = sections_text["section_3"]
                property_address_match = re.search(r"Street\s+([A-Za-z0-9\s.,#-]+?)\s*(?:Unit #\s*([A-Za-z0-9#-]*))?\s*City\s+([A-Za-z\s.-]+?)\s+State\s+([A-Z]{2})\s+ZIP\s+([0-9]{5})\s+Country\s+([A-Za-z]+)", sec3a_text) # Made non-greedy
                if property_address_match:
                    prop_details = {
                        "address": {
                            "street": property_address_match.group(1).strip(),
                            "unit": property_address_match.group(2).strip() if property_address_match.group(2) else None,
                            "city": property_address_match.group(3).strip(),
                            "state": property_address_match.group(4).strip(),
                            "zip": property_address_match.group(5).strip(),
                            "country": property_address_match.group(6).strip()
                        }
                    }
                    
                    value_status_occupancy_match = re.search(r"Property Value\s*\n\$([\d,.]+)\s*Status: Sold,\s*\nPending Sale,\s*\nor Retained\s*\n([A-Za-z\s]+?)\s*Intended Occupancy:\s*\n(Investment|Primary Residence|Second Home|Other)", sec3a_text, re.IGNORECASE) # Made status non-greedy and occupancy specific
                    if value_status_occupancy_match:
                        prop_details["property_value"] = float(value_status_occupancy_match.group(1).replace(',', ''))
                        prop_details["status"] = value_status_occupancy_match.group(2).strip()
                        prop_details["intended_occupancy"] = value_status_occupancy_match.group(3).strip()

                    monthly_expenses_match = re.search(r"Monthly Insurance, Taxes,\s*\nAssociation Dues, etc\.\s*\nif not included in Monthly\s*\nMortgage Payment\s*\n\$([\d,.]+)", sec3a_text)
                    if monthly_expenses_match:
                        prop_details["monthly_insurance_taxes_dues"] = float(monthly_expenses_match.group(1).replace(',', ''))
                    
                    extracted_data["real_estate_owned"].append(prop_details)

                # Mortgage Loans on this Property - Replaced hardcoded bank name, account number, and 1700
                mortgage_on_prop_match = re.search(r"([A-Za-z\s.-]+?)\s+([A-Za-z0-9-]+?)\s+([0-9.]+)\s+\$([\d,.]+)\s+\$([\d,.]+)\s*☑?\s*(Conventional|FHA|VA|USDA|Other)", sec3a_text)
                if mortgage_on_prop_match:
                    # Assuming this mortgage loan is for the first property in the list
                    if extracted_data["real_estate_owned"]:
                        extracted_data["real_estate_owned"][0]["mortgage_loans"].append({ # Use append for multiple mortgages
                            "creditor_name": mortgage_on_prop_match.group(1).strip(),
                            "account_number": mortgage_on_prop_match.group(2).strip(),
                            "monthly_mortgage_payment": float(mortgage_on_prop_match.group(4).replace(',', '')), # Updated index based on new groups
                            "unpaid_balance": float(mortgage_on_prop_match.group(5).replace(',', '')), # Updated index
                            "to_be_paid_off_at_closing": True if '☑' in mortgage_on_prop_match.group(0) else False, # Re-evaluating checkbox
                            "type": mortgage_on_prop_match.group(6).strip()
                        })

            # --- Parsing Section 3b: Additional Property ---
            if "section_3" in sections_text:
                sec3b_text = sections_text["section_3"]
                add_prop_address_match = re.search(r"Street\s+([A-Za-z0-9\s.,#-]+?)\s*(?:Unit #\s*([A-Za-z0-9#-]*))?\s*City\s+([A-Za-z\s.-]+?)\s+State\s+([A-Z]{2})\s+ZIP\s+([0-9]{5})\s+Country\s+([A-Za-z]+)", sec3b_text) # Made non-greedy
                if add_prop_address_match:
                    add_prop_details = {
                        "address": {
                            "street": add_prop_address_match.group(1).strip(),
                            "unit": add_prop_address_match.group(2).strip() if add_prop_address_match.group(2) else None,
                            "city": add_prop_address_match.group(3).strip(),
                            "state": add_prop_address_match.group(4).strip(),
                            "zip": add_prop_address_match.group(5).strip(),
                            "country": add_prop_address_match.group(6).strip()
                        }
                    }
                    add_prop_value_status_occupancy_match = re.search(r"Property Value\s*\n\$([\d,.]+)\s*Status: Sold,\s*\nPending Sale,\s*\nor Retained\s*\n([A-Za-z\s]+?)\s*Intended Occupancy:\s*\n(Investment|Primary Residence|Second Home|Other)", sec3b_text, re.IGNORECASE) # Made status non-greedy and occupancy specific
                    if add_prop_value_status_occupancy_match:
                        add_prop_details["property_value"] = float(add_prop_value_status_occupancy_match.group(1).replace(',', ''))
                        add_prop_details["status"] = add_prop_value_status_occupancy_match.group(2).strip()
                        add_prop_details["intended_occupancy"] = add_prop_value_status_occupancy_match.group(3).strip()
                    
                    add_prop_expenses_income_match = re.search(r"Monthly Insurance, Taxes,\s*\nAssociation Dues, etc\.\s*\nif not included in Monthly\s*\nMortgage Payment\s*\n\$([\d,.]+)\s*Monthly Rental\s*\nIncome\s*\n\$([\d,.]+)\s*For LENDER to calculate:\s*\nNet Monthly Rental Income\s*\n\$([\d,.]+)", sec3b_text)
                    if add_prop_expenses_income_match:
                        add_prop_details["monthly_insurance_taxes_dues"] = float(add_prop_expenses_income_match.group(1).replace(',', ''))
                        add_prop_details["monthly_rental_income"] = float(add_prop_expenses_income_match.group(2).replace(',', ''))
                        add_prop_details["net_monthly_rental_income"] = float(add_prop_expenses_income_match.group(3).replace(',', ''))
                    
                    extracted_data["real_estate_owned"].append(add_prop_details)


            # --- Parsing Section 4a: Loan and Property Information ---
            if "section_4" in sections_text:
                sec4a_text = sections_text["section_4"]
                
                loan_amount_match = re.search(r"Loan Amount\s+\$([\d,.]+)", sec4a_text)
                if loan_amount_match:
                    extracted_data["loan_property_info"]["loan_amount"] = float(loan_amount_match.group(1).replace(',', ''))
                
                if re.search(r"Loan Purpose\s+Purchase\s*☑", sec4a_text):
                    extracted_data["loan_property_info"]["loan_purpose"] = "Purchase"
                elif re.search(r"Loan Purpose\s+Refinance\s*☑", sec4a_text):
                    extracted_data["loan_property_info"]["loan_purpose"] = "Refinance"
                
                prop_address_match = re.search(r"Property Address\s*\nStreet\s+([A-Za-z0-9\s.,#-]+?)\s*(?:Unit #\s*([A-Za-z0-9#-]*))?\s*City\s+([A-Za-z\s.-]+?)\s+State\s+([A-Z]{2})\s+ZIP\s+([0-9]{5})\s*County\s+([A-Za-z\s-]+)", sec4a_text) # Made non-greedy
                if prop_address_match:
                    extracted_data["loan_property_info"]["property_address"] = {
                        "street": prop_address_match.group(1).strip(),
                        "unit": prop_address_match.group(2).strip() if prop_address_match.group(2) else None,
                        "city": prop_address_match.group(3).strip(),
                        "state": prop_address_match.group(4).strip(),
                        "zip": prop_address_match.group(5).strip(),
                        "county": prop_address_match.group(6).strip()
                    }
                
                num_units_match = re.search(r"Number of Units\s*(\d+)", sec4a_text)
                if num_units_match:
                    extracted_data["loan_property_info"]["number_of_units"] = int(num_units_match.group(1))
                
                prop_value_match = re.search(r"Property Value\s+\$([\d,.]+)", sec4a_text)
                if prop_value_match:
                    extracted_data["loan_property_info"]["property_value"] = float(prop_value_match.group(1).replace(',', ''))
                
                # Occupancy (using more precise regex for checkboxes)
                if re.search(r"Primary Residence\s*☑", sec4a_text):
                    extracted_data["loan_property_info"]["occupancy"] = "Primary Residence"
                elif re.search(r"Second Home\s*☑", sec4a_text):
                    extracted_data["loan_property_info"]["occupancy"] = "Second Home"
                elif re.search(r"Investment Property\s*☑", sec4a_text):
                    extracted_data["loan_property_info"]["occupancy"] = "Investment Property"
                
                mixed_use_match = re.search(r"Mixed-Use Property\.[\s\S]*?NO\s*☑", sec4a_text) # Adjusted for checkbox
                if mixed_use_match:
                    extracted_data["loan_property_info"]["mixed_use_property"] = "NO"
                
                manufactured_home_match = re.search(r"Manufactured Home\.[\s\S]*?NO\s*☑", sec4a_text) # Adjusted for checkbox
                if manufactured_home_match:
                    extracted_data["loan_property_info"]["manufactured_home"] = "NO"
            
            # --- Parsing Section 4b: Other New Mortgage Loans on the Property ---
            if "section_4" in sections_text:
                sec4b_text = sections_text["section_4"]
                # Replaced hardcoded "The HELOC Bank" with a general capture group for creditor name
                other_new_mortgage_loan_match = re.search(r"([A-Za-z\s.-]+?)\s*(?:☑|☐)?\s*(?:☑|☐)?\s*(First Lien|Subordinate Lien)\s*[\r\n]+\$([\d,.]+)\s*[\r\n]+\$([\d,.]+)\s*[\r\n]+\$([\d,.]+)", sec4b_text) # Added explicit checkbox capture
                if other_new_mortgage_loan_match:
                    extracted_data["other_new_mortgage_loans"].append({
                        "creditor_name": other_new_mortgage_loan_match.group(1).strip(),
                        "lien_type": other_new_mortgage_loan_match.group(2).strip(),
                        "monthly_payment": float(other_new_mortgage_loan_match.group(3).replace(',', '')),
                        "loan_amount": float(other_new_mortgage_loan_match.group(4).replace(',', '')),
                        "credit_limit": float(other_new_mortgage_loan_match.group(5).replace(',', ''))
                    })

            # --- Parsing Section 4c: Rental Income on the Property You Want to Purchase ---
            if "section_4" in sections_text:
                sec4c_text = sections_text["section_4"]
                rental_income_match = re.search(r"Expected Monthly Rental Income\s*\n\$([\d,.]+)\s*\nFor LENDER to calculate: Expected Net Monthly Rental Income\s*\n\$([\d,.]+)", sec4c_text)
                if rental_income_match:
                    extracted_data["rental_income_on_property"]["expected_monthly_rental_income"] = float(rental_income_match.group(1).replace(',', ''))
                    extracted_data["rental_income_on_property"]["expected_net_monthly_rental_income"] = float(rental_income_match.group(2).replace(',', ''))

            # --- Parsing Section 4d: Gifts or Grants ---
            if "section_4" in sections_text:
                sec4d_text = sections_text["section_4"]
                # Adjusted regex to correctly parse checkboxes and capture source
                grant_match = re.search(r"(Grant|Cash Gift)\s*(?:☐\s*)?☑\s*Deposited\s*(?:☐\s*)?\s*Not Deposited\s*(Community Nonprofit|Relative)\s*\n\$([\d,.]+)", sec4d_text)
                if grant_match:
                    extracted_data["gifts_grants"].append({
                        "asset_type": grant_match.group(1).strip(),
                        "deposited_not_deposited": "Deposited", # Assuming ☑ Deposited is the key
                        "source": grant_match.group(2).strip(),
                        "cash_or_market_value": float(grant_match.group(3).replace(',', ''))
                    })
                
                relative_gift_match = re.search(r"(Grant|Cash Gift)\s*(?:☐\s*)?\s*Deposited\s*(?:☐\s*)?☑\s*Not Deposited\s*(Community Nonprofit|Relative)\s*\n\$([\d,.]+)", sec4d_text)
                if relative_gift_match:
                    extracted_data["gifts_grants"].append({
                        "asset_type": relative_gift_match.group(1).strip(),
                        "deposited_not_deposited": "Not Deposited", # Assuming ☑ Not Deposited is the key
                        "source": relative_gift_match.group(2).strip(),
                        "cash_or_market_value": float(relative_gift_match.group(3).replace(',', ''))
                    })


            # --- Parsing Section 5a & 5b: Declarations ---
            if "section_5" in sections_text:
                sec5_text = sections_text["section_5"]
                
                # Corrected logic for checkboxes using re.search and raw strings
                # Example for "occupy_primary_residence"
                if re.search(r"Intend to occupy the Property as your primary residence\?[\s\S]*?YES\s*☑", sec5_text):
                    extracted_data["declarations"]["occupy_primary_residence"] = "YES"
                elif re.search(r"Intend to occupy the Property as your primary residence\?[\s\S]*?NO\s*☑", sec5_text):
                    extracted_data["declarations"]["occupy_primary_residence"] = "NO"

                # Example for "ownership_interest_in_other_property_past_3_years"
                if re.search(r"Do you have an ownership interest in any other property\?[\s\S]*?YES\s*☑", sec5_text):
                    extracted_data["declarations"]["ownership_interest_in_other_property_past_3_years"] = "YES"
                elif re.search(r"Do you have an ownership interest in any other property\?[\s\S]*?NO\s*☑", sec5_text):
                    extracted_data["declarations"]["ownership_interest_in_other_property_past_3_years"] = "NO"

                property_type_match = re.search(r"\(1\) What type of property did you own:[\s\S]*?(\bPR\b|\bSR\b|\bSH\b|\bIP\b)", sec5_text)
                if property_type_match:
                    extracted_data["declarations"]["property_type_owned"] = property_type_match.group(1).strip()
                
                how_held_title_match = re.search(r"\(2\) How did you hold title to the property:[\s\S]*?(\bS\b|\bSP\b|\bO\b)", sec5_text)
                if how_held_title_match:
                    extracted_data["declarations"]["how_held_title"] = how_held_title_match.group(1).strip()
                
                # Apply similar logic for other YES/NO declarations:
                if re.search(r"Are you affiliated with the Seller of the Property or the employer of the Seller\?[\s\S]*?NO\s*☑", sec5_text):
                    extracted_data["declarations"]["family_business_affiliation_seller"] = "NO"
                elif re.search(r"Are you affiliated with the Seller of the Property or the employer of the Seller\?[\s\S]*?YES\s*☑", sec5_text):
                    extracted_data["declarations"]["family_business_affiliation_seller"] = "YES"

                if re.search(r"Are you borrowing any money for this transaction other than the loan requested in this application\?[\s\S]*?NO\s*☑", sec5_text):
                    extracted_data["declarations"]["borrowing_other_money"] = "NO"
                elif re.search(r"Are you borrowing any money for this transaction other than the loan requested in this application\?[\s\S]*?YES\s*☑", sec5_text):
                    extracted_data["declarations"]["borrowing_other_money"] = "YES"
                    # If YES, try to extract amount
                    amount_match = re.search(r"If YES, amount\s+of other money\s*\n\$([\d,.]+)", sec5_text)
                    if amount_match:
                        extracted_data["declarations"]["amount_of_other_money"] = float(amount_match.group(1).replace(',', ''))


                if re.search(r"Are you applying for a new mortgage loan on this Property with another Lender\?[\s\S]*?NO\s*☑", sec5_text):
                    extracted_data["declarations"]["applying_for_other_mortgage"] = "NO"
                elif re.search(r"Are you applying for a new mortgage loan on this Property with another Lender\?[\s\S]*?YES\s*☑", sec5_text):
                    extracted_data["declarations"]["applying_for_other_mortgage"] = "YES"

                if re.search(r"Are you applying for any new credit \(e\.g\., mortgage, car, credit card\) associated with this Property or your Borrower Information\?[\s\S]*?NO\s*☑", sec5_text):
                    extracted_data["declarations"]["applying_for_new_credit"] = "NO"
                elif re.search(r"Are you applying for any new credit \(e\.g\., mortgage, car, credit card\) associated with this Property or your Borrower Information\?[\s\S]*?YES\s*☑", sec5_text):
                    extracted_data["declarations"]["applying_for_new_credit"] = "YES"
                
                if re.search(r"Is the Property subject to a lien that will not be released at or before closing\?[\s\S]*?NO\s*☑", sec5_text):
                    extracted_data["declarations"]["property_subject_to_lien"] = "NO"
                elif re.search(r"Is the Property subject to a lien that will not be released at or before closing\?[\s\S]*?YES\s*☑", sec5_text):
                    extracted_data["declarations"]["property_subject_to_lien"] = "YES"

                if re.search(r"Will any part of the down payment be provided by a co-signer or guarantor on this loan\?[\s\S]*?NO\s*☑", sec5_text):
                    extracted_data["declarations"]["co_signer_guarantor"] = "NO"
                elif re.search(r"Will any part of the down payment be provided by a co-signer or guarantor on this loan\?[\s\S]*?YES\s*☑", sec5_text):
                    extracted_data["declarations"]["co_signer_guarantor"] = "YES"
                
                if re.search(r"Do you have any outstanding judgments?[\s\S]*?NO\s*☑", sec5_text):
                    extracted_data["declarations"]["outstanding_judgments"] = "NO"
                elif re.search(r"Do you have any outstanding judgments?[\s\S]*?YES\s*☑", sec5_text):
                    extracted_data["declarations"]["outstanding_judgments"] = "YES"

                if re.search(r"Are you currently delinquent on any federal debt?[\s\S]*?NO\s*☑", sec5_text):
                    extracted_data["declarations"]["delinquent_federal_debt"] = "NO"
                elif re.search(r"Are you currently delinquent on any federal debt?[\s\S]*?YES\s*☑", sec5_text):
                    extracted_data["declarations"]["delinquent_federal_debt"] = "YES"
                
                if re.search(r"Are you a party to a lawsuit?[\s\S]*?NO\s*☑", sec5_text):
                    extracted_data["declarations"]["party_to_lawsuit"] = "NO"
                elif re.search(r"Are you a party to a lawsuit?[\s\S]*?YES\s*☑", sec5_text):
                    extracted_data["declarations"]["party_to_lawsuit"] = "YES"
                
                if re.search(r"Have you conveyed title to any Property in lieu of foreclosure in the last 7 years?[\s\S]*?NO\s*☑", sec5_text):
                    extracted_data["declarations"]["conveyed_title_lieu_foreclosure"] = "NO"
                elif re.search(r"Have you conveyed title to any Property in lieu of foreclosure in the last 7 years?[\s\S]*?YES\s*☑", sec5_text):
                    extracted_data["declarations"]["conveyed_title_lieu_foreclosure"] = "YES"

                if re.search(r"Have you completed a pre-foreclosure sale or short sale in the last 7 years?[\s\S]*?NO\s*☑", sec5_text):
                    extracted_data["declarations"]["pre_foreclosure_short_sale"] = "NO"
                elif re.search(r"Have you completed a pre-foreclosure sale or short sale in the last 7 years?[\s\S]*?YES\s*☑", sec5_text):
                    extracted_data["declarations"]["pre_foreclosure_short_sale"] = "YES"

                if re.search(r"Has any Property been foreclosed upon in the last 7 years?[\s\S]*?NO\s*☑", sec5_text):
                    extracted_data["declarations"]["property_foreclosed_upon"] = "NO"
                elif re.search(r"Has any Property been foreclosed upon in the last 7 years?[\s\S]*?YES\s*☑", sec5_text):
                    extracted_data["declarations"]["property_foreclosed_upon"] = "YES"

                if re.search(r"Have you declared bankruptcy within the past 7 years?[\s\S]*?NO\s*☑", sec5_text):
                    extracted_data["declarations"]["declared_bankruptcy"] = "NO"
                elif re.search(r"Have you declared bankruptcy within the past 7 years?[\s\S]*?YES\s*☑", sec5_text):
                    extracted_data["declarations"]["declared_bankruptcy"] = "YES"
                
                # Bankruptcy types
                if extracted_data["declarations"]["declared_bankruptcy"] == "YES":
                    if re.search(r"Chapter 11\s*☑", sec5_text):
                        extracted_data["declarations"]["bankruptcy_types"].append("Chapter 11")
                    if re.search(r"Chapter 7\s*☑", sec5_text):
                        extracted_data["declarations"]["bankruptcy_types"].append("Chapter 7")
                    if re.search(r"Chapter 12\s*☑", sec5_text):
                        extracted_data["declarations"]["bankruptcy_types"].append("Chapter 12")
                    if re.search(r"Chapter 13\s*☑", sec5_text):
                        extracted_data["declarations"]["bankruptcy_types"].append("Chapter 13")

            # --- Parsing Section 7: Military Service ---
            if "section_7" in sections_text:
                sec7_text = sections_text["section_7"]
                if re.search(r"Did you \(or your deceased spouse\) ever serve in the U\.S\. Armed Forces\?[\s\S]*?NO\s*☑", sec7_text):
                    extracted_data["military_service"]["ever_served"] = "NO"
                elif re.search(r"Did you \(or your deceased spouse\) ever serve in the U\.S\. Armed Forces\?[\s\S]*?YES\s*☑", sec7_text):
                    extracted_data["military_service"]["ever_served"] = "YES"
                
                if extracted_data["military_service"]["ever_served"] == "YES":
                    extracted_data["military_service"]["currently_serving"] = bool(re.search(r"Currently serving on active duty\s*☑", sec7_text))
                    extracted_data["military_service"]["retired_discharged_separated"] = bool(re.search(r"Currently retired, discharged, or separated from service\s*☑", sec7_text))
                    extracted_data["military_service"]["non_activated_reserve_national_guard"] = bool(re.search(r"Only period of service was as a non-activated member of the Reserve or National Guard\s*☑", sec7_text))
                    extracted_data["military_service"]["surviving_spouse"] = bool(re.search(r"Surviving spouse\s*☑", sec7_text))

            # --- Parsing Section 8: Demographic Information ---
            if "section_8" in sections_text:
                sec8_text = sections_text["section_8"]
                
                if re.search(r"Hispanic or Latino\s*☑", sec8_text):
                    extracted_data["demographic_info"]["ethnicity"].append("Hispanic or Latino")
                    if re.search(r"Mexican\s*☑", sec8_text):
                        extracted_data["demographic_info"]["ethnicity"].append("Mexican")
                    if re.search(r"Puerto Rican\s*☑", sec8_text):
                        extracted_data["demographic_info"]["ethnicity"].append("Puerto Rican")
                    if re.search(r"Cuban\s*☑", sec8_text):
                        extracted_data["demographic_info"]["ethnicity"].append("Cuban")
                elif re.search(r"Not Hispanic or Latino\s*☑", sec8_text):
                    extracted_data["demographic_info"]["ethnicity"].append("Not Hispanic or Latino")

                if re.search(r"Asian\s*☑", sec8_text):
                    extracted_data["demographic_info"]["race"].append("Asian")
                    if re.search(r"Asian Indian\s*☑", sec8_text):
                        extracted_data["demographic_info"]["race"].append("Asian Indian")
                    if re.search(r"Chinese\s*☑", sec8_text):
                        extracted_data["demographic_info"]["race"].append("Chinese")
                    if re.search(r"Filipino\s*☑", sec8_text):
                        extracted_data["demographic_info"]["race"].append("Filipino")
                    if re.search(r"Japanese\s*☑", sec8_text):
                        extracted_data["demographic_info"]["race"].append("Japanese")
                    if re.search(r"Korean\s*☑", sec8_text):
                        extracted_data["demographic_info"]["race"].append("Korean")
                    if re.search(r"Vietnamese\s*☑", sec8_text):
                        extracted_data["demographic_info"]["race"].append("Vietnamese")
                
                if re.search(r"Black or African American\s*☑", sec8_text):
                    extracted_data["demographic_info"]["race"].append("Black or African American")
                
                if re.search(r"White\s*☑", sec8_text):
                    extracted_data["demographic_info"]["race"].append("White")

                extracted_data["demographic_info"]["sex"] = "Male" if re.search(r"Male\s*☑", sec8_text) else ("Female" if re.search(r"Female\s*☑", sec8_text) else None)
                
                extracted_data["demographic_info"]["do_not_wish_to_provide"]["ethnicity"] = bool(re.search(r"Ethnicity[\s\S]*?I do not wish to provide this information\s*☑", sec8_text))
                extracted_data["demographic_info"]["do_not_wish_to_provide"]["race"] = bool(re.search(r"Race[\s\S]*?I do not wish to provide this information\s*☑", sec8_text))
                extracted_data["demographic_info"]["do_not_wish_to_provide"]["sex"] = bool(re.search(r"Sex[\s\S]*?I do not wish to provide this information\s*☑", sec8_text))
            
            # --- Parsing Section 9: Loan Originator Information ---
            if "section_9" in sections_text:
                sec9_text = sections_text["section_9"]
                
                # Loan Originator Organization Name: non-greedy, lookahead for Address or NMLSR ID
                org_name_match = re.search(r"Loan Originator Organization Name\s+([A-Za-z\s.-]+?)(?=\s*Address|\s*Loan Originator Organization NMLSR ID#)", sec9_text)
                if org_name_match:
                    extracted_data["loan_originator_info"]["organization_name"] = org_name_match.group(1).strip()
                
                # Address: non-greedy, lookahead for NMLSR ID or Email/Phone
                org_address_match = re.search(r"Address\s+([A-Za-z0-9\s,.-]+?)(?=\s*Loan Originator Organization NMLSR ID#|\s*Email|\s*Phone)", sec9_text) 
                if org_address_match:
                    extracted_data["loan_originator_info"]["address"] = org_address_match.group(1).strip()
                
                org_nmlsr_id_match = re.search(r"Loan Originator Organization NMLSR ID#\s*(\d+)", sec9_text)
                if org_nmlsr_id_match:
                    extracted_data["loan_originator_info"]["nmlsr_id"] = org_nmlsr_id_match.group(1).strip()
                
                # Loan Originator Name: non-greedy, lookahead for NMLSR ID or Email/State License ID
                originator_name_match = re.search(r"Loan Originator Name\s+([A-Za-z\s.-]+?)(?=\s*Loan Originator NMLSR ID#|\s*Email|\s*State License ID#)", sec9_text)
                if originator_name_match:
                    extracted_data["loan_originator_info"]["originator_name"] = originator_name_match.group(1).strip()
                
                originator_nmlsr_id_match = re.search(r"Loan Originator NMLSR ID#\s*(\d+)", sec9_text)
                if originator_nmlsr_id_match:
                    extracted_data["loan_originator_info"]["originator_nmlsr_id"] = originator_nmlsr_id_match.group(1).strip()
                
                originator_email_match = re.search(r"Email\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", sec9_text)
                if originator_email_match:
                    extracted_data["loan_originator_info"]["email"] = originator_email_match.group(1).strip()
                
                state_license_id_match = re.search(r"State License ID#\s*(\d+)\s*State License ID#\s*(\d+)", sec9_text) # This might still be tricky if layout varies
                if state_license_id_match:
                    extracted_data["loan_originator_info"]["state_license_id"] = state_license_id_match.group(2).strip() # The second one is for the originator
                
                originator_phone_match = re.search(r"Phone\s+\(?(\d{3})\)?[\s.-]*(\d{3})[\s.-]*(\d{4})", sec9_text) # More flexible phone number format
                if originator_phone_match:
                    extracted_data["loan_originator_info"]["phone"] = f"({originator_phone_match.group(1)}) {originator_phone_match.group(2)}{originator_phone_match.group(3)}"


    except Exception as e:
        print(f"Error extracting data: {e}")
    
    return extracted_data