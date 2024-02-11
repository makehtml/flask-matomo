.DEFAULT: test

PLATFORM := ${shell uname -o}


ifeq (${VIRTUAL_ENV},)
  INVENV = poetry run
else
  INVENV =
endif

${info Platform: ${PLATFORM}}


.PHONY: help
help:
	@echo "usage:"
	@echo ""
	@echo "dev | install-dev"
	@echo "   setup development environment"
	@echo ""
	@echo "install-ci"
	@echo "   setup CI environment"
	@echo ""
	@echo "test | run-all-tests"
	@echo "   run all tests"
	@echo ""
	@echo "run-doc-tests"
	@echo "   run all tests"
	@echo ""
	@echo "test-w-coverage [cov_report]"
	@echo "   run all tests with coverage collection"
	@echo "   cov_report=COV-REPORT	forwarded to pytest-cov. Defaults to 'term-missing'."
	@echo ""
	@echo "lint"
	@echo "   lint the code"
	@echo ""
	@echo "type-check"
	@echo "   check types"
	@echo ""
	@echo "fmt"
	@echo "   run formatter on all code"
	@echo ""
	@echo "bumpversion [part=PART]"
	@echo "   bumps the given PART of the version"
	@echo "   this will bump the version, commit and tag with the new version"
	@echo "   part=PART	can be patch, minor or major. Defaults to patch."
	@echo ""
	@echo "publish [branch=BRANCH]"
	@echo "   pushes the given BRANCH with tags for starting CI-publish"
	@echo "   branch=BRANCH	the branch to publish from. Defaults to main."
	@echo ""

dev: install-dev
install-dev:
	poetry install --without ci

# setup CI environment
install-ci: install-dev
	poetry install --only ci

unit_test_dirs := tests
e2e_test_dirs := tests
all_test_dirs := tests

default_cov := "--cov=flask_matomo2"
cov_report := "term-missing"
cov := ${default_cov}

tests := ${unit_test_dirs}
all_tests := ${all_test_dirs}

.PHONY: test
test:
	${INVENV} pytest -vv ${tests}

.PHONY: test-w-coverage
test-w-coverage:
	${INVENV} pytest -vv ${cov} --cov-report=${cov_report} ${all_tests}

.PHONY: lint
lint:
	${INVENV} ruff ${flags} flask_matomo2 tests

.PHONY: serve-docs
serve-docs:
	cd docs && ${INVENV} mkdocs serve && cd -

.PHONY: type-check
type-check:
	${INVENV} mypy --config-file mypy.ini -p flask_matomo2

branch := "main"
.PHONY: publish
publish:
	git push origin ${branch} --tags

.PHONY: clean clean-pyc
clean: clean-pyc
clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

.PHONY: fmt
fmt:
	${INVENV} black .

# test if code is formatted
.PHONY: check-fmt
check-fmt:
	${INVENV} black . --check

part := "patch"

bumpversion:
	${INVENV} bumpversion ${part}

build:
	poetry build

tests/requirements.txt: pyproject.toml
	poetry export --with=dev --without-hashes --output=$@
