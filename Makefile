.PHONY: docs
init:
		pip install -r requirements.txt
ci:
		pytest tests --junitxml=report.xml
test:
		tox -p
cov:
		pytest --verbose --cov-report term --cov-report xml --cov=xhs tests/
upload:
		python setup.py sdist bdist_wheel
		twine upload dist/*
		rm -fr build dist .egg xhs.egg-info
docs:
		cd docs && make clean html && start ./_build/html/index.html
