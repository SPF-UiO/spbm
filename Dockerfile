FROM python:3.6-slim-buster
LABEL maintainer="Thor K. Høgås <thor@roht.no>"

#RUN apt-get update && apt-get install -y libxslt-dev libxml2-dev git build-essential libxml2 wget gettext curl uwsgi-plugin-python libpq-dev libxmlsec1-dev
RUN apt update && apt install -y build-essential gettext

WORKDIR /usr/src/app

COPY . ./

RUN pip install --no-cache-dir -r requirements.txt

RUN useradd uwsgi &&\
    mkdir -p logs &&\
	python manage.py collectstatic --no-input --clear &&\
	python manage.py compilemessages

EXPOSE 3031

ENTRYPOINT ["container/entrypoint.sh"]

CMD ["uwsgi",  "--ini", "container/uwsgi.ini"]
