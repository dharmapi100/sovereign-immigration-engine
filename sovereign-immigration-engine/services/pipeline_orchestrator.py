import sys
import os
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/kyc-pipeline')
sys.path.insert(0, '/Users/jtjtmoney/Projects/ksgc-sovereign-ai/sovereign-immigration-engine/services/policy-matching')

from ingestion import KYCExtractor
from matcher import PolicyMatcher

class PipelineOrchestrator:
    def __init__(self, key: bytes, rules: dict):
        self.extractor = KYCExtractor(key)
        self.matcher = PolicyMatcher(rules)

    def run_pipeline(self, encrypted_doc: bytes, image_path: str) -> dict:
        data = self.extractor.extract_pii(encrypted_doc, image_path)
        return self.matcher.match_visa(data)
