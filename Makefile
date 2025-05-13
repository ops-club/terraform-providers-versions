.PHONY: install build clean

install:
	pip install -r requirements.txt 
	pip install -r requirements-dev.txt

build:
	pyinstaller terraform_analyzer.spec --clean --noconfirm

clean:
	rm -rf build dist
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete