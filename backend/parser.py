# backend/parser.py
# OCR and Text Parsing Module for Smart Receipt Analyzer

# Dependencies:
# - pytesseract: For OCR processing
# - pdf2image: To convert PDFs to image frames
# - PIL: For image file handling
# - re: For regex-based field extraction
# - datetime: For parsing date formats
# - backend.utils.detect_currency: Custom function to detect currency symbols

import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import re
from datetime import datetime
import pytesseract
from backend.utils import detect_currency

# # Set path to local Tesseract installation (required for Windows)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"



def extract_text(file_path):
    """
    Extracts raw text from a file (PDF, image, or TXT).
    Uses OCR for images/PDFs, direct reading for .txt files.
    """
    if file_path.endswith(".txt"):
        # Step 1: Read .txt file content directly
        with open(file_path, "r", encoding="utf-8") as f:
            raw_text = f.read()
    elif file_path.endswith((".jpg", ".jpeg", ".png")):
        # Step 2: OCR for image
        raw_text = pytesseract.image_to_string(Image.open(file_path))
    elif file_path.endswith(".pdf"):
        # Step 3: Convert PDF to image, then OCR
        pages = convert_from_path(file_path)
        raw_text = ""
        for page in pages:
            raw_text += pytesseract.image_to_string(page)
    else:
        raise ValueError("Unsupported file type")

    return raw_text

# def extract_text(file_path):

#     # Extracts text from a given image or PDF file using OCR.

#     if file_path.endswith(".pdf"):
#         images = convert_from_path(file_path)
#         return "\n".join([pytesseract.image_to_string(img) for img in images])
#     else:
#         img = Image.open(file_path)
#         text = pytesseract.image_to_string(img)

#         print("\n----- OCR TEXT START -----\n", text, "\n----- OCR TEXT END -----\n")
#         return text

def parse_fields(text):
    try:
        text_lower = text.lower()

        # Match vendor using partial/fuzzy keyword match
        known_vendors = {
            "amazon": "Amazon",
            "flipkart": "Flipkart",
            "reliance": "Reliance",
            "big bazaar": "Big Bazaar",
            "super mart": "Amazon Super Mart",
            "dmart": "Dmart",
            "more": "More"
        }

        vendor = "Unknown"
        for key in known_vendors:
            if key in text_lower:
                vendor = known_vendors[key]
                break

        # Match date
        date_match = re.search(r"\d{2}[/-]\d{2}[/-]\d{4}", text) or re.search(r"\d{4}[/-]\d{2}[/-]\d{2}", text)
        if date_match:
            date_str = date_match.group()
            try:
                if "-" in date_str:
                    date = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str.startswith("20") else datetime.strptime(date_str, "%d-%m-%Y").date()
                else:
                    date = datetime.strptime(date_str, "%d/%m/%Y").date()
            except ValueError:
                date = None
        else:
            date = None

        
        # Extract amount (from total or max number)
        amount = extract_amount(text)

        # Detect currency from symbols or text
        currency = detect_currency(text)
        
        # Determine category based on vendor name
        groceries_keywords = ["reliance", "big bazaar", "dmart", "more", "super mart"]
        category = "Groceries" if any(k in vendor.lower() for k in groceries_keywords) else "Others"

        return {
            "vendor": vendor,
            "date": date,
            "amount": amount,
            "category": category,
            "currency": currency
        }

    except Exception as e:
        print("❌ Error in parse_fields:", str(e))
        return {
            "vendor": "Unknown",
            "date": None,
            "amount": 0.0,
            "category": "Others",
            "currency": "INR"
        }


def extract_amount(text: str) -> float:
        # Extracts the amount from OCR text.

    lines = text.splitlines()

    # Prefer lines with 'total' or 'amount'
    for line in lines:
        if re.search(r'total\s+amount|total', line, re.IGNORECASE):
            match = re.search(r'(\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)', line.replace(',', ''))
            if match:
                return float(match.group(1))

    # Fallback: get all numbers and return the largest
    matches = re.findall(r'\d{1,5}(?:\.\d{1,2})?', text)
    if matches:
        amounts = [float(m) for m in matches]
        return max(amounts)

    return 0.0

