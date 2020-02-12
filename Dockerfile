FROM python:3.6-slim-buster
LABEL Maintainer "Thor K. Høgås <thor@roht.no>"

#RUN apt-get update && apt-get install -y libxslt-dev libxml2-dev git build-essential libxml2 wget gettext curl uwsgi-plugin-python libpq-dev libxmlsec1-dev
RUN apt update && apt install -y build-essential

WORKDIR /usr/src/app

COPY . ./

RUN useradd uwsgi; \
	mkdir -p /usr/src/static; \
    mkdir -p logs

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 3031

CMD ["scripts/entrypoint.sh"]
