import json

class PolicyMatcher:
    def __init__(self, policy_rules: dict):
        self.rules = policy_rules

    def match_visa(self, applicant_data: dict) -> dict:
        # Matches PII against visa criteria (PIPA compliant)
        score = 0
        for rule, threshold in self.rules.items():
            val = applicant_data.get(rule, 0)
            if isinstance(val, (int, float)) and val >= threshold:
                score += 1
        
        return {
            "eligible": score >= len(self.rules),
            "score": score,
            "visa_type": "D-10-2"
        }
