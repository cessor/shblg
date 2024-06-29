.DEFAULT_GOAL := help
.PHONY: help
# Source (So cool, thanks): https://daniel.feldroy.com/posts/autodocumenting-makefiles
define HELP_TEXT
import re,sys;print('\n'.join(("%-10s %s"%match.groups() for line in sys.stdin if(match:=re.match(r'^([a-zA-Z_-]+):.*?##(.*)$$',line)))))
endef
export HELP_TEXT

DESCRIPTION="Make targets for shblg"

help:  ## Print this help
	@echo
	@echo $(DESCRIPTION)
	@echo
	@python -c "$$HELP_TEXT" < $(MAKEFILE_LIST)

qa:  ## Run tests
	mypy .
	pylint blog
	pylint shit
	bandit -r .
	python3 manage.py test

trans:  ## Generate *.po files for translation to English
	python3 manage.py makemessages --locale en
