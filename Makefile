bootstrap:
	pip install -r requirements.txt

lint:
	flake8 orion test

test:
	PYTHONPATH=. python -m unittest discover -s test -v

cover:
	PYTHONPATH=. coverage run --source=orion -m unittest discover -s test -v
	coverage report -m

serve:
	PYTHONPATH=. python orion/server.py

init-db:
	PYTHONPATH=. python orion/scripts/db_init.py

.PHONY: bootstrap lint test cover
