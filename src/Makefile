test:
	mypy .
	pylint blog
	pylint shit
	bandit -r .
	python3 manage.py test

trans:
	python3 manage.py makemessages --locale en
