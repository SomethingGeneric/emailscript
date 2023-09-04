setup:
	python3 -m venv venv
	venv/bin/pip install -r requirements.txt
	venv/bin/pip install pylint black
test:
	venv/bin/pylint *.py
	venv/bin/black .