PYTHON = python3
MAIN = a_maze_ing.py
CONFIG = config.txt

install:
	$(PYTHON) -m pip install build flake8 mypy

run:
	$(PYTHON) $(MAIN) $(CONFIG)

debug:
	$(PYTHON) -m pdb $(MAIN) $(CONFIG)

clean:
	rm -rf __pycache__
	rm -rf */__pycache__
	rm -rf .mypy_cache
	rm -rf .pytest_cache
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -rf */*.egg-info

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

build:
	$(PYTHON) -m build