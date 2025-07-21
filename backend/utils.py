import re

def detect_currency(text: str) -> str:
    """Detect currency from receipt text using simple rules."""
    text = text.lower()
    if re.search(r'\$', text) or 'usd' in text:
        return "USD"
    elif re.search(r'€', text) or 'eur' in text:
        return "EUR"
    elif re.search(r'£', text) or 'gbp' in text:
        return "GBP"
    elif re.search(r'₹', text) or 'inr' in text or 'rs' in text:
        return "INR"
    elif re.search(r'AED|د\.إ', text, re.IGNORECASE):
        return "AED"
    else:
        return "INR"  # Default fallback
