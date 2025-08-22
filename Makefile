.PHONY: help install install-dev test lint format clean run-api run-streamlit setup

# Default target
help:
	@echo "Student Learning Framework - Available Commands:"
	@echo ""
	@echo "Setup:"
	@echo "  setup          - Initial setup (install dependencies, setup pre-commit)"
	@echo "  install        - Install production dependencies"
	@echo "  install-dev    - Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  format         - Format code with black and isort"
	@echo "  lint           - Run linting checks"
	@echo "  test           - Run tests"
	@echo "  test-cov       - Run tests with coverage"
	@echo ""
	@echo "Running:"
	@echo "  run-api        - Start the FastAPI server"
	@echo "  run-streamlit  - Start the Streamlit app"
	@echo "  run-cli        - Run the CLI interface"
	@echo ""
	@echo "Maintenance:"
	@echo "  clean          - Clean up generated files"
	@echo "  pre-commit     - Install pre-commit hooks"

# Setup
setup: install-dev
	@echo "Setting up pre-commit hooks..."
	pre-commit install
	@echo "Setup complete! 🎉"

install:
	@echo "Installing production dependencies..."
	pip install -r requirements.txt

install-dev:
	@echo "Installing development dependencies..."
	pip install -r requirements-dev.txt

# Code quality
format:
	@echo "Formatting code..."
	black .
	isort .

lint:
	@echo "Running linting checks..."
	flake8 .
	mypy src/ --ignore-missing-imports
	bandit -r src/ -f json -o bandit-report.json

# Testing
test:
	@echo "Running tests..."
	pytest tests/ -v

test-cov:
	@echo "Running tests with coverage..."
	pytest tests/ --cov=src --cov-report=html --cov-report=term

# Running applications
run-api:
	@echo "Starting FastAPI server..."
	cd web_app && python -m uvicorn web_app.routes:app --reload --host 127.0.0.1 --port 8005

run-streamlit:
	@echo "Starting Streamlit app..."
	cd streamlit_app && streamlit run main.py

run-cli:
	@echo "Running CLI interface..."
	python main.py --all

# Maintenance
clean:
	@echo "Cleaning up..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf bandit-report.json
	@echo "Cleanup complete!"

pre-commit:
	@echo "Installing pre-commit hooks..."
	pre-commit install
