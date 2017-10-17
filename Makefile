WIREMOCK = wiremock
TESTER = tester

VERSION ?= $(shell grep -o "\([0-9]\+\.\)\+[0-9]\+" src/WireMockLibrary/version.py)

.DEFAULT_GOAL := help
.PHONY: help
help: ## Print help
	@echo "------------------------------------------------------------------------"
	@echo "WireMock Robot Framework Library"
	@echo "------------------------------------------------------------------------"
	@awk -F ":.*##" '/:.*##/ && ! /\t/ {printf "\033[36m%-25s\033[0m%s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.PHONY: setup
setup: ## Setup dev environment
	sudo pip install -r requirements.txt

.PHONY: wiremock/run
wiremock/run: ## Run wiremock
	ROBOT_ARGS=$(ROBOT_ARGS) docker-compose up -d $(WIREMOCK)

.PHONY: wiremock/stop
wiremock/stop: ## Stop wiremock
	docker-compose down

.PHONY: tester/test
tester/test: ## Run integration tests
	docker-compose up --build --force-recreate $(TESTER)

.PHONY: lint
lint: ## Run static code analysis
	flake8

.PHONY: release
release: ## Release package to PyPI
	python setup.py sdist
	twine upload dist/robotframework-wiremock-$(VERSION).tar.gz

.PHONY: version/tag
version/tag: ## Tag HEAD with new version tag
	git tag -a $(VERSION) -m "$(VERSION)"
