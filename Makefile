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
	flake8 src

.PHONY: clean
clean: ## Clean dist
	rm -rf dist MANIFEST

.PHONY: release
release: clean ## Release package to PyPI
	python setup.py sdist
	twine upload dist/robotframework-wiremock-$(VERSION).tar.gz

.PHONY: version/tag
version/tag: ## Tag HEAD with new version tag
	git tag -a $(VERSION) -m "$(VERSION)"

.PHONY: docs
docs: ## Generate library docs
	python -m robot.libdoc src/WireMockLibrary ../tyrjola.github.io/docs/robotframework-wiremock-$(VERSION).html
	ln -sf robotframework-wiremock-$(VERSION).html ../tyrjola.github.io/docs/robotframework-wiremock.html
	git -C ../tyrjola.github.io add .
	git -C ../tyrjola.github.io commit -m "robotframework-wiremock-$(VERSION)"
