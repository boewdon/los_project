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
    county: Optional[str] = None
    country: Optional[str] = None
    how_long_years: Optional[int] = None
    how_long_months: Optional[int] = None
    housing_expense: Optional[str] = None

@dataclass
class ContactInfo:
    home_phone: Optional[str] = None
    cell_phone: Optional[str] = None
    work_phone: Optional[str] = None
    email: Optional[str] = None

@dataclass
class DependentsInfo:
    number: Optional[int] = None
    ages: Optional[int] = None # Assuming a single field for ages as per parser

@dataclass
class GrossMonthlyIncome:
    base: Optional[float] = None
    overtime: Optional[float] = None
    bonus: Optional[float] = None
    commission: Optional[float] = None
    military_entitlements: Optional[float] = None
    other: Optional[float] = None
    total: Optional[float] = None

@dataclass
class Employment:
    employer_name: Optional[str] = None
    phone: Optional[str] = None
    gross_monthly_income: GrossMonthlyIncome = field(default_factory=GrossMonthlyIncome)
    address: Address = field(default_factory=Address)
    position_title: Optional[str] = None
    start_date: Optional[str] = None
    how_long_in_work: Dict[str, Optional[int]] = field(default_factory=dict)
    employed_by_family_member: Optional[bool] = None
    business_owner_or_self_employed: Optional[bool] = None
    ownership_share_less_25: Optional[bool] = None
    ownership_share_25_or_more: Optional[bool] = None
    monthly_income_loss: Optional[float] = None

@dataclass
class OtherIncomeSource:
    source: Optional[str] = None
    monthly_income: Optional[float] = None

@dataclass
class BankAccount:
    account_type: Optional[str] = None
    financial_institution: Optional[str] = None
    account_number: Optional[str] = None
    cash_or_market_value: Optional[float] = None

@dataclass
class OtherAssetCredit:
    asset_or_credit_type: Optional[str] = None
    cash_or_market_value: Optional[float] = None

@dataclass
class Liability:
    account_type: Optional[str] = None
    company_name: Optional[str] = None
    account_number: Optional[str] = None
    unpaid_balance: Optional[float] = None
    monthly_payment: Optional[float] = None
    paid_off_at_closing: Optional[bool] = None

@dataclass
class OtherLiabilityExpense:
    type: Optional[str] = None
    monthly_payment: Optional[float] = None

@dataclass
class MortgageLoanOnProperty:
    creditor_name: Optional[str] = None
    account_number: Optional[str] = None
    monthly_mortgage_payment: Optional[float] = None
    unpaid_balance: Optional[float] = None
    to_be_paid_off_at_closing: Optional[bool] = None
    type: Optional[str] = None
    credit_limit: Optional[float] = None

@dataclass
class RealEstateProperty:
    address: Address = field(default_factory=Address)
    property_value: Optional[float] = None
    status: Optional[str] = None
    intended_occupancy: Optional[str] = None
    monthly_insurance_taxes_dues: Optional[float] = None
    monthly_rental_income: Optional[float] = None
    net_monthly_rental_income: Optional[float] = None
    mortgage_loans: List[MortgageLoanOnProperty] = field(default_factory=list)

@dataclass
class Declarations:
    occupy_primary_residence: Optional[str] = None
    ownership_interest_in_other_property_past_3_years: Optional[str] = None
    property_type_owned: Optional[str] = None
    how_held_title: Optional[str] = None
    family_business_affiliation_seller: Optional[str] = None
    borrowing_other_money: Optional[str] = None
    amount_of_other_money: Optional[float] = None
    applying_for_other_mortgage: Optional[str] = None
    applying_for_new_credit: Optional[str] = None
    property_subject_to_lien: Optional[str] = None
    co_signer_guarantor: Optional[str] = None
    outstanding_judgments: Optional[str] = None
    delinquent_federal_debt: Optional[str] = None
    party_to_lawsuit: Optional[str] = None
    conveyed_title_lieu_foreclosure: Optional[str] = None
    pre_foreclosure_short_sale: Optional[str] = None
    property_foreclosed_upon: Optional[str] = None
    declared_bankruptcy: Optional[str] = None
    bankruptcy_types: List[str] = field(default_factory=list)

@dataclass
class MilitaryServiceInfo:
    ever_served: Optional[str] = None
    currently_serving: Optional[bool] = None
    retired_discharged_separated: Optional[bool] = None
    non_activated_reserve_national_guard: Optional[bool] = None
    surviving_spouse: Optional[bool] = None

@dataclass
class DemographicInfo:
    ethnicity: List[str] = field(default_factory=list)
    race: List[str] = field(default_factory=list)
    sex: Optional[str] = None
    do_not_wish_to_provide: Dict[str, Optional[bool]] = field(default_factory=dict)

@dataclass
class Borrower:
    name: Optional[str] = None
    alternate_names: Optional[str] = None
    social_security_number: Optional[str] = None
    date_of_birth: Optional[str] = None
    citizenship: Optional[str] = None
    marital_status: Optional[str] = None
    dependents: DependentsInfo = field(default_factory=DependentsInfo)
    contact_info: ContactInfo = field(default_factory=ContactInfo)
    current_address: Address = field(default_factory=Address)
    current_employment: Employment = field(default_factory=Employment)
    additional_employment: List[Employment] = field(default_factory=list)
    other_income_sources: List[OtherIncomeSource] = field(default_factory=list)
    assets_bank_retirement_other: List[BankAccount] = field(default_factory=list)
    assets_other_assets_credits: List[OtherAssetCredit] = field(default_factory=list)
    liabilities_credit_cards_debts_leases: List[Liability] = field(default_factory=list)
    liabilities_other_liabilities_expenses: List[OtherLiabilityExpense] = field(default_factory=list)
    real_estate_owned: List[RealEstateProperty] = field(default_factory=list)
    declarations: Declarations = field(default_factory=Declarations)
    military_service: MilitaryServiceInfo = field(default_factory=MilitaryServiceInfo)
    demographic_info: DemographicInfo = field(default_factory=DemographicInfo)

@dataclass
class LoanOriginatorInfo:
    organization_name: Optional[str] = None
    address: Optional[str] = None
    nmlsr_id: Optional[str] = None
    originator_name: Optional[str] = None
    originator_nmlsr_id: Optional[str] = None
    email: Optional[str] = None
    state_license_id: Optional[str] = None
    phone: Optional[str] = None

@dataclass
class NewMortgageLoan:
    creditor_name: Optional[str] = None
    lien_type: Optional[str] = None
    monthly_payment: Optional[float] = None
    loan_amount: Optional[float] = None
    credit_limit: Optional[float] = None

@dataclass
class RentalIncomeOnProperty:
    expected_monthly_rental_income: Optional[float] = None
    expected_net_monthly_rental_income: Optional[float] = None

@dataclass
class GiftGrant:
    asset_type: Optional[str] = None
    deposited_not_deposited: Optional[str] = None
    source: Optional[str] = None
    cash_or_market_value: Optional[float] = None

@dataclass
class Loan:
    loan_amount: Optional[float] = None
    loan_purpose: Optional[str] = None
    property_address: Address = field(default_factory=Address)
    number_of_units: Optional[int] = None
    property_value: Optional[float] = None
    occupancy: Optional[str] = None
    mixed_use_property: Optional[str] = None
    manufactured_home: Optional[str] = None
    other_new_mortgage_loans: List[NewMortgageLoan] = field(default_factory=list)
    rental_income_on_property: RentalIncomeOnProperty = field(default_factory=RentalIncomeOnProperty)
    gifts_grants: List[GiftGrant] = field(default_factory=list)
    loan_originator_info: LoanOriginatorInfo = field(default_factory=LoanOriginatorInfo)

@dataclass
class URLAData:
    """Main container for all extracted URLA data."""
    borrower: Borrower = field(default_factory=Borrower)
    loan: Loan = field(default_factory=Loan)