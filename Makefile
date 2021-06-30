VERSION = $(shell python3 setup.py --version | tr '+' '-')
.DEFAULT_GOAL := dev

clean:
	rm -rf .pytest_cache build dist *.egg-info


dist: clean
	python3 setup.py sdist bdist_wheel


upload: dist
	test -z "$(git status --porcelain)" # don't upload if the repo is dirty
	twine upload dist/*
	git tag -a 'v$(VERSION)' -m 'v$(VERSION)'
	git push origin v$(VERSION)


dev:
	uvicorn --reload --port 3000 --log-level warning app.main:server
