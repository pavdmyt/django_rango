flake:
	flake8 rango/tests/

test: flake
	python manage.py test -v 2

coverage:
	coverage run --source='.' manage.py test -v 2
	coverage report

clean:
	find . -type f -name '*.py[co]' -delete
	rm -f .coverage
