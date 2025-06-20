# src/main.py
import os
from src.pdf_parser import extract_borrower_personal_info
from src.data_models import Borrower # You'll add Loan later, and likely populate Borrower object later

def process_urla_pdf(pdf_file_name: str):
    """
    Processes a single URLA PDF to extract borrower and loan information.
    """
    # Construct the file path relative to the project root
    # os.path.dirname(__file__) gets the directory of the current file (main.py)
    # os.path.abspath gets the absolute path
    # os.path.join safely joins path components
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    pdf_path = os.path.join(project_root, "data", pdf_file_name)

    # Correcting the path to be relative if you're running from the project root
    # If your pdf_path variable was literally `pdf_path = 'Data/URLA.pdf'`
    # and you're running main.py from the project root, then it might be looking in `your_project_name/Data/URLA.pdf`.
    # Let's ensure the path is robustly handled, assuming `main.py` is in `src/`.
    
    # Check if the PDF file exists at the constructed path
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at '{pdf_path}'")
        print(f"Current working directory: {os.getcwd()}")
        print("Please ensure 'URLA.pdf' is in the 'data/' directory relative to your project root.")
        return

    print(f"Processing PDF: '{pdf_path}'")

    # Extract borrower personal info
    borrower_data = extract_borrower_personal_info(pdf_path)
    
    print("\n--- Extracted Borrower Personal Information ---")
    
    # Print the entire dictionary
    import json
    print(json.dumps(borrower_data, indent=4)) # Use json.dumps for pretty printing the dictionary

    print("\n--- Extraction Complete ---")

if __name__ == "__main__":
    urla_filename = "URLA.pdf" # Make sure this matches your PDF file name in the data folder
    process_urla_pdf(urla_filename)