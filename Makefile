bootstrap:
	pip install -r requirements.txt

lint:
	flake8 orion test

test:
	PYTHONPATH=. python -m unittest discover -s test -v

serve:
	PYTHONPATH=. python orion/server.py

.PHONY: bootstrap lint test
