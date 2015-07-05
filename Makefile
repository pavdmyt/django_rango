test:
	python manage.py test rango

coverage:
	coverage run ./manage.py test
	coverage report

clean:
	find . -type f -name '*.py[co]' -delete
	rm -f .coverage
