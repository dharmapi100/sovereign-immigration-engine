import json

class VisaValidator:
    def __init__(self, visa_rules: dict):
        self.visa_rules = visa_rules

    def validate_application(self, applicant_pii: dict) -> dict:
        # PIPA compliant policy validation
        is_valid = True
        missing_fields = []
        for field, required in self.visa_rules.items():
            if required and field not in applicant_pii:
                is_valid = False
                missing_fields.append(field)
        
        return {
            "valid": is_valid,
            "missing": missing_fields
        }
