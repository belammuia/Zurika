.RECIPEPREFIX = >
DC  = docker compose
RUN = $(DC) run --rm web python manage.py

.PHONY: up down build restart logs check test migrations migrate seed shell

up:
> $(DC) up -d
down:
> $(DC) down
build:
> $(DC) build
restart:
> $(DC) restart web worker beat
logs:
> $(DC) logs -f web worker beat
check:
> $(RUN) check
test:
> $(RUN) test $(app)
migrations:
> $(RUN) makemigrations
migrate:
> $(RUN) migrate
seed:
> $(RUN) seed_zurika
shell:
> $(RUN) shell
