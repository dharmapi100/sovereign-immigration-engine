import sys
import os
_ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.isdir(os.path.join(_ROOT, 'services')) and os.path.dirname(_ROOT) != _ROOT:
    _ROOT = os.path.dirname(_ROOT)
sys.path.insert(0, os.path.join(_ROOT, 'services/kyc-pipeline'))
sys.path.insert(0, os.path.join(_ROOT, 'services/policy-matching'))

from ingestion import KYCExtractor

class PipelineOrchestrator:
    def __init__(self, key: bytes, visa_rules: dict, policy_rules: dict):
        self.extractor = KYCExtractor(key, visa_rules, policy_rules)

    def run_pipeline(self, encrypted_doc: bytes, image_path: str) -> dict:
        return self.extractor.extract_pii(encrypted_doc, image_path)
