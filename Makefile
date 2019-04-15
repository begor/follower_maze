run:
	PYTHONPATH=. python3.7 follower_maze/runner.py

test:
	python3.7 -m unittest discover tests