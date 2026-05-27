help:
	@echo "Usage: make <target>"
	@echo "  setup-roles                       Setup initial roles"
	@echo "  i18n-extract                      Extracts the texts from the code"
	@echo "  i18n-compile                      Compiles the translations"
	@echo "  celery                            Starts the celery and beat worker"
	@echo "  pytest                            Run pytest"
	@echo "  gitlog                            Show commits since last week"


# Commands

setup-roles:
	python manage.py setup_roles

pytest:
	pytest -n auto

gitlog:
	git log --since="7 days ago" --until="now" --reverse --pretty=format:"%ad - %s" --date=short

celery:
	celery -A config worker --beat --scheduler django --loglevel=DEBUG

i18n-extract:
	python manage.py makemessages --settings=config.settings -l en -l es

i18n-compile:
	python manage.py compilemessages  --settings=config.settings -l en -l es
