.PHONY: docs
init:
		pip install -r requirements.txt
ci:
		pytest tests --junitxml=report.xml
test:
		tox -p
cov:
		pytest --verbose --cov-report term --cov-report xml --cov=xhs tests/
build_wheel:
		python3 setup.py sdist bdist_wheel
		rm -fr build .egg xhs.egg-info
upload:
		make build_wheel
		twine upload dist/*
docs:
		cd docs && make clean html && start ./_build/html/index.html
