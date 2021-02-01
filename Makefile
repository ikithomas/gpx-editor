
venv:
	python3 -m venv venv

test:
	pytest

pip:
	pip3 install -r requirements.txt
