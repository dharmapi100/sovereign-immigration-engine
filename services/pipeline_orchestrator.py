import sys
import os
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/kyc-pipeline')
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/policy-matching')

from ingestion import KYCExtractor

class PipelineOrchestrator:
    def __init__(self, key: bytes, visa_rules: dict, policy_rules: dict):
        self.extractor = KYCExtractor(key, visa_rules, policy_rules)

    def run_pipeline(self, encrypted_doc: bytes, image_path: str) -> dict:
        return self.extractor.extract_pii(encrypted_doc, image_path)
