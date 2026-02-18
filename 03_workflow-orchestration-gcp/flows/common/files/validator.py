def validate_phone(phone):
    """Simple phone validator - shared utility"""
    digits = ''.join(filter(str.isdigit, phone))
    return len(digits) >= 10

if __name__ == "__main__":
    print(f"Phone valid: {validate_phone('+1-555-123-4567')}")