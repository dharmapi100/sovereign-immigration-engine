# Sovereign Immigration Engine — convenience targets
# Core needs only python3 + cryptography (stdlib API, no web framework).

PY ?= python3
VERSION ?= 0.2.0

.PHONY: help test demo run bundle docker clean

help:  ## show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-10s\033[0m %s\n", $$1, $$2}'

test:  ## run the whole test suite (stdlib unittest)
	@pass=0; fail=0; \
	for f in $$(find . -name "test_*.py" -not -path "*/dist/*" | sort); do \
		if $(PY) "$$f" >/dev/null 2>&1; then pass=$$((pass+1)); \
		else echo "FAIL $$f"; fail=$$((fail+1)); fi; \
	done; \
	echo "suites: $$pass passed, $$fail failed"; \
	test $$fail -eq 0

demo:  ## run the end-to-end demo
	$(PY) demo.py

run:  ## run the API (port 8787)
	$(PY) services/api/server.py

bundle:  ## build the air-gap deployment bundle
	bash deployment/build_bundle.sh $(VERSION)

docker:  ## build the container image
	docker build -t sovereign-immigration:$(VERSION) .

clean:  ## remove runtime artefacts
	find . -name "__pycache__" -type d -not -path "*/.git/*" -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -f access_audit.log sovereign_audit.db dummy.png test_mask.png 2>/dev/null || true
	rm -rf dist 2>/dev/null || true
	@echo "cleaned"
