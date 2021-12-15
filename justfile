set dotenv-load := false
version := `python3 setup.py --version | tr '+' '-'`
default: (dev)

clean:
	rm -rf .pytest_cache build dist *.egg-info


dist: clean
    pip-audit
    python3 setup.py sdist bdist_wheel


publish: dist
	git diff-index --quiet HEAD
	twine upload dist/*
	git tag -a 'v{{version}}' -m 'v{{version}}'
	git push origin v{{version}}


dev:
	uvicorn --reload --port 3000 --log-level warning app.main:server
