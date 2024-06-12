.PHONY: all init format lint build build_frontend install_frontend run_frontend run_backend dev help tests coverage

all: help
log_level ?= debug
host ?= 0.0.0.0
port ?= 7860
env ?= .env
open_browser ?= true
path = src/backend/base/dfapp/frontend
workers ?= 1

codespell:
	@poetry install --with spelling
	poetry run codespell --toml pyproject.toml

fix_codespell:
	@poetry install --with spelling
	poetry run codespell --toml pyproject.toml --write

setup_poetry:
	pipx install poetry

add:
	@echo 'Adding dependencies'
ifdef devel
	cd src/backend/base && poetry add --group dev $(devel)
endif

ifdef main
	poetry add $(main)
endif

ifdef base
	cd src/backend/base && poetry add $(base)
endif

init:
	@echo 'Installing backend dependencies'
	make install_backend
	@echo 'Installing frontend dependencies'
	make install_frontend

coverage:
	poetry run pytest --cov \
		--cov-config=.coveragerc \
		--cov-report xml \
		--cov-report term-missing:skip-covered \
		--cov-report lcov:coverage/lcov-pytest.info

# allow passing arguments to pytest
tests:
	poetry run pytest tests --instafail -ra -n auto -m "not api_key_required" $(args)


format:
	poetry run ruff check . --fix
	poetry run ruff format .
	cd src/frontend && npm run format

lint:
	poetry run mypy --namespace-packages -p "dfapp"

install_frontend:
	cd src/frontend && npm install

install_frontendci:
	cd src/frontend && npm ci

install_frontendc:
	cd src/frontend && rm -rf node_modules package-lock.json && npm install

run_frontend:
	@-kill -9 `lsof -t -i:3000`
	cd src/frontend && npm start

tests_frontend:
ifeq ($(UI), true)
		cd src/frontend && npx playwright test --ui --project=chromium
else
		cd src/frontend && npx playwright test --project=chromium
endif

run_cli:
	@echo 'Running the CLI'
	@make install_frontend > /dev/null
	@echo 'Install backend dependencies'
	@make install_backend > /dev/null
	@echo 'Building the frontend'
	@make build_frontend > /dev/null
ifdef env
	@make start env=$(env) host=$(host) port=$(port) log_level=$(log_level)
else
	@make start host=$(host) port=$(port) log_level=$(log_level)
endif

run_cli_debug:
	@echo 'Running the CLI in debug mode'
	@make install_frontend > /dev/null
	@echo 'Building the frontend'
	@make build_frontend > /dev/null
	@echo 'Install backend dependencies'
	@make install_backend > /dev/null
ifdef env
	@make start env=$(env) host=$(host) port=$(port) log_level=debug
else
	@make start host=$(host) port=$(port) log_level=debug
endif

start:
	@echo 'Running the CLI'

ifeq ($(open_browser),false)
	@make install_backend && poetry run dfapp run --path $(path) --log-level $(log_level) --host $(host) --port $(port) --env-file $(env) --no-open-browser
else
	@make install_backend && poetry run dfapp run --path $(path) --log-level $(log_level) --host $(host) --port $(port) --env-file $(env)
endif



setup_devcontainer:
	make init
	make build_frontend
	poetry run dfapp --path src/frontend/build

setup_env:
	@sh ./scripts/setup/update_poetry.sh 1.8.2
	@sh ./scripts/setup/setup_env.sh

frontend:
	make install_frontend
	make run_frontend

frontendc:
	make install_frontendc
	make run_frontend

install_backend:
	@echo 'Installing backend dependencies'
	@poetry install
	@poetry run pre-commit install

backend:
	@echo 'Setting up the environment'
	@make setup_env
	make install_backend
	@-kill -9 $(lsof -t -i:7860)
ifdef login
	@echo "Running backend autologin is $(login)";
	DFAPP_AUTO_LOGIN=$(login) poetry run uvicorn --factory dfapp.main:create_app --host 0.0.0.0 --port 7860 --reload --env-file .env --loop asyncio --workers $(workers)
else
	@echo "Running backend respecting the .env file";
	poetry run uvicorn --factory dfapp.main:create_app --host 0.0.0.0 --port 7860 --reload --env-file .env  --loop asyncio --workers $(workers)
endif

build_and_run:
	@echo 'Removing dist folder'
	@make setup_env
	rm -rf dist
	rm -rf src/backend/base/dist
	make build
	poetry run pip install dist/*.tar.gz
	poetry run dfapp run

build_and_install:
	@echo 'Removing dist folder'
	rm -rf dist
	rm -rf src/backend/base/dist
	make build && poetry run pip install dist/*.whl && pip install src/backend/base/dist/*.whl --force-reinstall

build_frontend:
	cd src/frontend && CI='' npm run build
	rm -rf src/backend/base/dfapp/frontend
	cp -r src/frontend/build src/backend/base/dfapp/frontend

build:
	@echo 'Building the project'
	@make setup_env
ifdef base
	make install_frontendci
	make build_frontend
	make build_dfapp_base
endif

ifdef main
	make build_dfapp
endif

build_dfapp_base:
	cd src/backend/base && poetry build
	rm -rf src/backend/base/dfapp/frontend

build_dfapp_backup:
	poetry lock && poetry build

build_dfapp:
	cd ./scripts && poetry run python update_dependencies.py
	poetry lock
	poetry build
ifdef restore
	mv pyproject.toml.bak pyproject.toml
	mv poetry.lock.bak poetry.lock
endif

dev:
	make install_frontend
ifeq ($(build),1)
		@echo 'Running docker compose up with build'
		docker compose $(if $(debug),-f docker-compose.debug.yml) up --build
else
		@echo 'Running docker compose up without build'
		docker compose $(if $(debug),-f docker-compose.debug.yml) up
endif

lock_base:
	cd src/backend/base && poetry lock

lock_dfapp:
	poetry lock

lock:
# Run both in parallel
	@echo 'Locking dependencies'
	cd src/backend/base && poetry lock
	poetry lock

publish_base:
	cd src/backend/base && poetry publish

publish_dfapp:
	poetry publish

publish:
	@echo 'Publishing the project'
ifdef base
	make publish_base
endif

ifdef main
	make publish_dfapp
endif

help:
	@echo '----'
	@echo 'format              - run code formatters'
	@echo 'lint                - run linters'
	@echo 'install_frontend    - install the frontend dependencies'
	@echo 'build_frontend      - build the frontend static files'
	@echo 'run_frontend        - run the frontend in development mode'
	@echo 'run_backend         - run the backend in development mode'
	@echo 'build               - build the frontend static files and package the project'
	@echo 'publish             - build the frontend static files and package the project and publish it to PyPI'
	@echo 'dev                 - run the project in development mode with docker compose'
	@echo 'tests               - run the tests'
	@echo 'coverage            - run the tests and generate a coverage report'
	@echo '----'
