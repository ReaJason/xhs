.PHONY: docs
init:
		pip install -r requirements.txt
test:
		pytest tests
upload:
		python setup.py sdist bdist_wheel
		twine upload dist/*
		rm -fr build dist .egg xhs.egg-info
docs:
		cd docs && make html
