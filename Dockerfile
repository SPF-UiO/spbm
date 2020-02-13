FROM python:3.6-slim-buster
LABEL maintainer="Thor K. Høgås <thor@roht.no>"

ENV APP_DIR /usr/src/app

RUN apt update && apt install -y build-essential gettext

WORKDIR $APP_DIR

COPY requirements.txt $APP_DIR

RUN pip install --no-cache-dir -r requirements.txt

COPY . $APP_DIR

RUN useradd app &&\
    useradd uwsgi &&\
    mkdir -p $APP_DIR/logs &&\
    python manage.py collectstatic --no-input --clear &&\
    python manage.py compilemessages

USER app

EXPOSE 8435

ENTRYPOINT ["container/entrypoint.sh"]

CMD ["uwsgi",  "--ini", "container/uwsgi.ini"]
