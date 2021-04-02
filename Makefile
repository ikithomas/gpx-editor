.PHONY: venv test pip

venv:
	python3 -m venv venv

test:
	venv/bin/pytest

pip:
	pip3 install -r requirements.txt
