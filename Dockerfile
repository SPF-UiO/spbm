FROM debian:jessie
LABEL maintainer "adriah@cyb.no"

RUN apt-get update && apt-get install -y libxslt-dev libxml2-dev libmysqlclient-dev python3 python-dev python3-pip git build-essential libxml2 wget gettext curl uwsgi-plugin-python libpq-dev libxmlsec1-dev

COPY . /app

WORKDIR /app

RUN pip3 install -r requirements.txt

RUN mkdir -p /app; \
    mkdir -p /usr/src/static; \
    mkdir -p /app/logs; \
    groupadd -g 1000 app; \
    useradd -g app -u 1000 app; \
    chown app:app /app /usr/src/static /app/logs

USER app

RUN pip3 install -r requirements.txt

EXPOSE 3031

CMD ["/app/scripts/run_production.sh", "-fg"]
