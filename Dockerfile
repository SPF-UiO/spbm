FROM python:3.8-slim-buster
LABEL maintainer="Thor K. Høgås <thor@roht.no>"

ARG DEVELOPMENT

ENV DEVELOPMENT=${SPBM_DEBUG:-0} \
	APP_DIR=/usr/src/app \
	POETRY_VERSION=1.0.3 \
	PYTHONFAULTHANDLER=1 \
	PYTHONUNBUFFERED=1 \
	PYTHONHASHSEED=random

RUN apt update &&\
	apt install -y build-essential gettext libpq-dev &&\
	pip install poetry==$POETRY_VERSION &&\
	useradd app &&\
    useradd uwsgi


WORKDIR $APP_DIR

# Copy our Poetry files first to avoid rebuilding our package dependencies when
# we can avoid it.
COPY pyproject.toml poetry.lock $APP_DIR

# If we're creating a development environment version of the container,
# then we'll need the developer dependencies. In our case SPBM_DEBUG works as
# the indicator for that. If it's off, we do not install development packages.
RUN poetry config virtualenvs.create false \
	&& poetry install -E psql $(test "$DEVELOPMENT" == 0 && echo "--no-dev") --no-interaction --no-ansi

COPY . $APP_DIR

RUN mkdir -p $APP_DIR/logs &&\
	python manage.py collectstatic --no-input --clear &&\
    python manage.py compilemessages

USER app

EXPOSE 8000

# Stops Python from buffering strings
ENV PYTHONUNBUFFERED 1

ENTRYPOINT ["container/entrypoint.sh"]

CMD ["gunicorn", "-c", "container/gunicorn.conf.py", "spbm.wsgi:application"]
