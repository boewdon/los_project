# src/data_models.py
from dataclasses import dataclass, field
from typing import List, Dict, Optional

@dataclass
class Address:
    street: Optional[str] = None
    unit: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    how_long_years: Optional[int] = None
    how_long_months: Optional[int] = None
    housing_expense: Optional[str] = None # e.g., "Own", "Rent ($X/month)", "No primary housing expense"

@dataclass
class Employment:
    employer_name: Optional[str] = None
    position_title: Optional[str] = None
    start_date: Optional[str] = None # Consider datetime.date for real applications
    time_in_line_of_work: Optional[Dict[str, int]] = field(default_factory=lambda: {"years": None, "months": None})
    base_income: Optional[float] = None
    overtime_income: Optional[float] = None
    bonus_income: Optional[float] = None
    commission_income: Optional[float] = None
    military_entitlements: Optional[float] = None
    other_income: Optional[float] = None # For 1b. Other income from employment


@dataclass
class Borrower:
    name: Optional[str] = None
    alternate_names: Optional[str] = None
    social_security_number: Optional[str] = None
    date_of_birth: Optional[str] = None # Consider datetime.date for real applications
    citizenship: Optional[str] = None # e.g., "U.S. Citizen", "Permanent Resident Alien"
    marital_status: Optional[str] = None
    dependents: Dict[str, Optional[int]] = field(default_factory=lambda: {"number": None, "ages": None}) # You mentioned dependents but example doesn't show one
    contact_info: Dict[str, Optional[str]] = field(default_factory=lambda: {
        "home_phone": None, "cell_phone": None, "work_phone": None, "email": None
    })
    current_address: Address = field(default_factory=Address)
    current_employment: Employment = field(default_factory=Employment)
    # Add other fields as you extract them (former address, assets, liabilities, etc.)


@dataclass
class Loan:
    loan_number: Optional[str] = None
    agency_case_number: Optional[str] = None
    loan_amount: Optional[float] = None
    loan_purpose: Optional[str] = None
    property_address: Address = field(default_factory=Address)
    property_value: Optional[float] = None
    occupancy: Optional[str] = None
    
    # Add other loan-specific fields as needed