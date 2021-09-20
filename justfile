set dotenv-load := false
version := `python3 setup.py --version | tr '+' '-'`
default: (dev)

clean:
	rm -rf .pytest_cache build dist *.egg-info


dist: clean
	python3 setup.py sdist bdist_wheel


publish: dist
	git diff-index --quiet HEAD
	twine upload dist/*
	git tag -a '{{version}}' -m 'v{{version}}'
	git push origin v{{version}}


dev:
	uvicorn --port 3000 --log-level warning app.main:server
