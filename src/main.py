# src/main.py
import os
import json
import dataclasses # <--- ADDED THIS IMPORT
from src.pdf_parser import extract_borrower_personal_info
from src.data_models import URLAData, Borrower, Employment, Address, ContactInfo, DependentsInfo, GrossMonthlyIncome, OtherIncomeSource, BankAccount, OtherAssetCredit, Liability, OtherLiabilityExpense, MortgageLoanOnProperty, RealEstateProperty, NewMortgageLoan, RentalIncomeOnProperty, GiftGrant, Declarations, MilitaryServiceInfo, DemographicInfo, LoanOriginatorInfo, Loan # Import all necessary dataclasses

def process_urla_pdf(pdf_file_name: str):
    """
    Processes a single URLA PDF to extract borrower and loan information
    and populate the data model.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pdf_path = os.path.join(project_root, "Data", pdf_file_name) # Ensure 'Data' directory is capitalized if that's its actual name

    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at '{pdf_path}'")
        print(f"Current working directory: {os.getcwd()}")
        print("Please ensure 'URLA.pdf' is in the 'Data/' directory relative to your project root.")
        return

    print(f"Processing PDF: '{pdf_path}'")

    # Extract all data as a dictionary
    extracted_dict = extract_borrower_personal_info(pdf_path)

    # --- Populate the URLAData data model ---
    urla_data = URLAData()

    # Populate Borrower Information
    if "borrower_info" in extracted_dict:
        borrower_data = extracted_dict["borrower_info"]
        urla_data.borrower.name = borrower_data.get("name")
        urla_data.borrower.alternate_names = borrower_data.get("alternate_names")
        urla_data.borrower.social_security_number = borrower_data.get("social_security_number")
        urla_data.borrower.date_of_birth = borrower_data.get("date_of_birth")
        urla_data.borrower.citizenship = borrower_data.get("citizenship")
        urla_data.borrower.marital_status = borrower_data.get("marital_status")

        if "dependents" in borrower_data and borrower_data["dependents"]:
            urla_data.borrower.dependents = DependentsInfo(
                number=borrower_data["dependents"].get("number"),
                ages=borrower_data["dependents"].get("ages")
            )

        if "contact_info" in borrower_data and borrower_data["contact_info"]:
            urla_data.borrower.contact_info = ContactInfo(
                home_phone=borrower_data["contact_info"].get("home_phone"),
                cell_phone=borrower_data["contact_info"].get("cell_phone"),
                work_phone=borrower_data["contact_info"].get("work_phone"),
                email=borrower_data["contact_info"].get("email")
            )

        if "current_address" in borrower_data and borrower_data["current_address"]:
            urla_data.borrower.current_address = Address(
                street=borrower_data["current_address"].get("street"),
                unit=borrower_data["current_address"].get("unit"),
                city=borrower_data["current_address"].get("city"),
                state=borrower_data["current_address"].get("state"),
                zip_code=borrower_data["current_address"].get("zip"), # Changed from zip to zip_code
                country=borrower_data["current_address"].get("country"),
                how_long_years=borrower_data["current_address"].get("how_long_years"),
                how_long_months=borrower_data["current_address"].get("how_long_months"),
                housing_expense=borrower_data["current_address"].get("housing_expense")
            )
        # Add former_address, mailing_address if your parser extracts them

    # Populate Employment Information
    if "employment_info" in extracted_dict:
        emp_info = extracted_dict["employment_info"]
        
        if "current_employment" in emp_info and emp_info["current_employment"]:
            current_emp_data = emp_info["current_employment"]
            current_employment = Employment(
                employer_name=current_emp_data.get("employer_name"),
                phone=current_emp_data.get("phone"),
                position_title=current_emp_data.get("position_title"),
                start_date=current_emp_data.get("start_date"),
                employed_by_family_member=current_emp_data.get("employed_by_family_member"),
                business_owner_or_self_employed=current_emp_data.get("business_owner_or_self_employed"),
                ownership_share_less_25=current_emp_data.get("ownership_share_less_25"),
                ownership_share_25_or_more=current_emp_data.get("ownership_share_25_or_more"),
                monthly_income_loss=current_emp_data.get("monthly_income_loss")
            )
            if "how_long_in_work" in current_emp_data and current_emp_data["how_long_in_work"]:
                current_employment.how_long_in_work = current_emp_data["how_long_in_work"]
            if "gross_monthly_income" in current_emp_data and current_emp_data["gross_monthly_income"]:
                current_employment.gross_monthly_income = GrossMonthlyIncome(
                    base=current_emp_data["gross_monthly_income"].get("base"),
                    overtime=current_emp_data["gross_monthly_income"].get("overtime"),
                    bonus=current_emp_data["gross_monthly_income"].get("bonus"),
                    commission=current_emp_data["gross_monthly_income"].get("commission"),
                    military_entitlements=current_emp_data["gross_monthly_income"].get("military_entitlements"),
                    other=current_emp_data["gross_monthly_income"].get("other"),
                    total=current_emp_data["gross_monthly_income"].get("total")
                )
            if "address" in current_emp_data and current_emp_data["address"]:
                current_employment.address = Address(
                    street=current_emp_data["address"].get("street"),
                    unit=current_emp_data["address"].get("unit"),
                    city=current_emp_data["address"].get("city"),
                    state=current_emp_data["address"].get("state"),
                    zip_code=current_emp_data["address"].get("zip"),
                    country=current_emp_data["address"].get("country")
                )
            urla_data.borrower.current_employment = current_employment
        
        if "additional_employment" in emp_info and emp_info["additional_employment"]:
            # Assuming additional_employment in the parser returns a single dict for Amazon.
            # If it could return multiple, loop through it.
            add_emp_data = emp_info["additional_employment"]
            additional_employment = Employment(
                employer_name=add_emp_data.get("employer_name"),
                phone=add_emp_data.get("phone"),
                position_title=add_emp_data.get("position_title"),
                start_date=add_emp_data.get("start_date"),
            )
            if "how_long_in_work" in add_emp_data and add_emp_data["how_long_in_work"]:
                additional_employment.how_long_in_work = add_emp_data["how_long_in_work"]
            if "gross_monthly_income" in add_emp_data and add_emp_data["gross_monthly_income"]:
                additional_employment.gross_monthly_income = GrossMonthlyIncome(
                    base=add_emp_data["gross_monthly_income"].get("base"),
                    overtime=add_emp_data["gross_monthly_income"].get("overtime"),
                    bonus=add_emp_data["gross_monthly_income"].get("bonus"),
                    commission=add_emp_data["gross_monthly_income"].get("commission"),
                    military_entitlements=add_emp_data["gross_monthly_income"].get("military_entitlements"),
                    other=add_emp_data["gross_monthly_income"].get("other"),
                    total=add_emp_data["gross_monthly_income"].get("total")
                )
            if "address" in add_emp_data and add_emp_data["address"]:
                additional_employment.address = Address(
                    street=add_emp_data["address"].get("street"),
                    unit=add_emp_data["address"].get("unit"),
                    city=add_emp_data["address"].get("city"),
                    state=add_emp_data["address"].get("state"),
                    zip_code=add_emp_data["address"].get("zip"),
                    country=add_emp_data["address"].get("country")
                )
            urla_data.borrower.additional_employment.append(additional_employment)


    # Populate Other Income Sources
    if "other_income_sources" in extracted_dict:
        for item in extracted_dict["other_income_sources"]:
            urla_data.borrower.other_income_sources.append(OtherIncomeSource(**item))

    # Populate Assets
    if "assets" in extracted_dict:
        assets_data = extracted_dict["assets"]
        if "bank_retirement_other" in assets_data:
            for item in assets_data["bank_retirement_other"]:
                urla_data.borrower.assets_bank_retirement_other.append(BankAccount(**item))
        if "other_assets_credits" in assets_data:
            for item in assets_data["other_assets_credits"]:
                urla_data.borrower.assets_other_assets_credits.append(OtherAssetCredit(**item))

    # Populate Liabilities
    if "liabilities" in extracted_dict:
        liabilities_data = extracted_dict["liabilities"]
        if "credit_cards_debts_leases" in liabilities_data:
            for item in liabilities_data["credit_cards_debts_leases"]:
                urla_data.borrower.liabilities_credit_cards_debts_leases.append(Liability(**item))
        if "other_liabilities_expenses" in liabilities_data:
            for item in liabilities_data["other_liabilities_expenses"]:
                urla_data.borrower.liabilities_other_liabilities_expenses.append(OtherLiabilityExpense(**item))

    # Populate Real Estate Owned
    if "real_estate_owned" in extracted_dict:
        for prop_data in extracted_dict["real_estate_owned"]:
            re_property = RealEstateProperty()
            if "address" in prop_data and prop_data["address"]:
                re_property.address = Address(
                    street=prop_data["address"].get("street"),
                    unit=prop_data["address"].get("unit"),
                    city=prop_data["address"].get("city"),
                    state=prop_data["address"].get("state"),
                    zip_code=prop_data["address"].get("zip"),
                    country=prop_data["address"].get("country")
                )
            re_property.property_value = prop_data.get("property_value")
            re_property.status = prop_data.get("status")
            re_property.intended_occupancy = prop_data.get("intended_occupancy")
            re_property.monthly_insurance_taxes_dues = prop_data.get("monthly_insurance_taxes_dues")
            re_property.monthly_rental_income = prop_data.get("monthly_rental_income")
            re_property.net_monthly_rental_income = prop_data.get("net_monthly_rental_income")
            
            if "mortgage_loans" in prop_data and prop_data["mortgage_loans"]:
                for loan_data in prop_data["mortgage_loans"]:
                    re_property.mortgage_loans.append(MortgageLoanOnProperty(**loan_data))

            urla_data.borrower.real_estate_owned.append(re_property)

    # Populate Loan and Property Information
    if "loan_property_info" in extracted_dict:
        loan_prop_info = extracted_dict["loan_property_info"]
        urla_data.loan.loan_amount = loan_prop_info.get("loan_amount")
        urla_data.loan.loan_purpose = loan_prop_info.get("loan_purpose")
        if "property_address" in loan_prop_info and loan_prop_info["property_address"]:
            urla_data.loan.property_address = Address(
                street=loan_prop_info["property_address"].get("street"),
                unit=loan_prop_info["property_address"].get("unit"),
                city=loan_prop_info["property_address"].get("city"),
                state=loan_prop_info["property_address"].get("state"),
                zip_code=loan_prop_info["property_address"].get("zip"),
                county=loan_prop_info["property_address"].get("county")
            )
        urla_data.loan.number_of_units = loan_prop_info.get("number_of_units")
        urla_data.loan.property_value = loan_prop_info.get("property_value")
        urla_data.loan.occupancy = loan_prop_info.get("occupancy")
        urla_data.loan.mixed_use_property = loan_prop_info.get("mixed_use_property")
        urla_data.loan.manufactured_home = loan_prop_info.get("manufactured_home")

    # Populate Other New Mortgage Loans
    if "other_new_mortgage_loans" in extracted_dict:
        for item in extracted_dict["other_new_mortgage_loans"]:
            urla_data.loan.other_new_mortgage_loans.append(NewMortgageLoan(**item))
    
    # Populate Rental Income on Property
    if "rental_income_on_property" in extracted_dict and extracted_dict["rental_income_on_property"]:
        urla_data.loan.rental_income_on_property = RentalIncomeOnProperty(
            expected_monthly_rental_income=extracted_dict["rental_income_on_property"].get("expected_monthly_rental_income"),
            expected_net_monthly_rental_income=extracted_dict["rental_income_on_property"].get("expected_net_monthly_rental_income")
        )

    # Populate Gifts or Grants
    if "gifts_grants" in extracted_dict:
        for item in extracted_dict["gifts_grants"]:
            urla_data.loan.gifts_grants.append(GiftGrant(**item))

    # Populate Declarations
    if "declarations" in extracted_dict and extracted_dict["declarations"]:
        declarations_data = extracted_dict["declarations"]
        urla_data.borrower.declarations = Declarations(
            occupy_primary_residence=declarations_data.get("occupy_primary_residence"),
            ownership_interest_in_other_property_past_3_years=declarations_data.get("ownership_interest_in_other_property_past_3_years"),
            property_type_owned=declarations_data.get("property_type_owned"),
            how_held_title=declarations_data.get("how_held_title"),
            family_business_affiliation_seller=declarations_data.get("family_business_affiliation_seller"),
            borrowing_other_money=declarations_data.get("borrowing_other_money"),
            amount_of_other_money=declarations_data.get("amount_of_other_money"),
            applying_for_other_mortgage=declarations_data.get("applying_for_other_mortgage"),
            applying_for_new_credit=declarations_data.get("applying_for_new_credit"),
            property_subject_to_lien=declarations_data.get("property_subject_to_lien"),
            co_signer_guarantor=declarations_data.get("co_signer_guarantor"),
            outstanding_judgments=declarations_data.get("outstanding_judgments"),
            delinquent_federal_debt=declarations_data.get("delinquent_federal_debt"),
            party_to_lawsuit=declarations_data.get("party_to_lawsuit"),
            conveyed_title_lieu_foreclosure=declarations_data.get("conveyed_title_lieu_foreclosure"),
            pre_foreclosure_short_sale=declarations_data.get("pre_foreclosure_short_sale"),
            property_foreclosed_upon=declarations_data.get("property_foreclosed_upon"),
            declared_bankruptcy=declarations_data.get("declared_bankruptcy"),
            bankruptcy_types=declarations_data.get("bankruptcy_types", [])
        )

    # Populate Military Service
    if "military_service" in extracted_dict and extracted_dict["military_service"]:
        military_data = extracted_dict["military_service"]
        urla_data.borrower.military_service = MilitaryServiceInfo(
            ever_served=military_data.get("ever_served"),
            currently_serving=military_data.get("currently_serving"),
            retired_discharged_separated=military_data.get("retired_discharged_separated"),
            non_activated_reserve_national_guard=military_data.get("non_activated_reserve_national_guard"),
            surviving_spouse=military_data.get("surviving_spouse")
        )

    # Populate Demographic Information
    if "demographic_info" in extracted_dict and extracted_dict["demographic_info"]:
        demo_data = extracted_dict["demographic_info"]
        urla_data.borrower.demographic_info = DemographicInfo(
            ethnicity=demo_data.get("ethnicity", []),
            race=demo_data.get("race", []),
            sex=demo_data.get("sex")
        )
        if "do_not_wish_to_provide" in demo_data and demo_data["do_not_wish_to_provide"]:
            urla_data.borrower.demographic_info.do_not_wish_to_provide = demo_data["do_not_wish_to_provide"]

    # Populate Loan Originator Information
    if "loan_originator_info" in extracted_dict and extracted_dict["loan_originator_info"]:
        lo_data = extracted_dict["loan_originator_info"]
        urla_data.loan.loan_originator_info = LoanOriginatorInfo(
            organization_name=lo_data.get("organization_name"),
            address=lo_data.get("address"),
            nmlsr_id=lo_data.get("nmlsr_id"),
            originator_name=lo_data.get("originator_name"),
            originator_nmlsr_id=lo_data.get("originator_nmlsr_id"),
            email=lo_data.get("email"),
            state_license_id=lo_data.get("state_license_id"),
            phone=lo_data.get("phone")
        )


    print("\n--- Extracted Data (as structured dataclass objects) ---")
    # To pretty print the entire dataclass object, you can convert it to a dictionary
    # and then use json.dumps. This requires a small helper function for nested dataclasses.
    def dataclass_to_dict(obj):
        if isinstance(obj, (int, float, str, bool)) or obj is None:
            return obj
        if isinstance(obj, list):
            return [dataclass_to_dict(elem) for elem in obj]
        if isinstance(obj, dict):
            return {k: dataclass_to_dict(v) for k, v in obj.items()}
        # Corrected logic for dataclasses: iterate over field objects
        if dataclasses.is_dataclass(obj):
            return {f.name: dataclass_to_dict(getattr(obj, f.name)) for f in dataclasses.fields(obj)}
        return obj

    print(json.dumps(dataclass_to_dict(urla_data), indent=4))

    print("\n--- Extraction and Data Model Population Complete ---")

if __name__ == "__main__":
    urla_filename = "URLA.pdf"
    process_urla_pdf(urla_filename)