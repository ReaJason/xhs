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
		python -m build
		rm -fr build .egg xhs.egg-info
upload:
		make build_wheel
		twine upload dist/*
docs:
		cd docs && make clean html && open ./_build/html/index.html
