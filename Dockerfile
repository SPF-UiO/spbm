FROM python:3.6-slim-buster
LABEL maintainer="Thor K. Høgås <thor@roht.no>"

RUN apt update && apt install -y build-essential gettext

WORKDIR /usr/src/app

COPY . ./

RUN pip install --no-cache-dir -r requirements.txt

RUN useradd app &&\
    useradd uwsgi &&\
    mkdir -p logs &&\
    python manage.py collectstatic --no-input --clear &&\
    python manage.py compilemessages

USER app

EXPOSE 8435

ENTRYPOINT ["container/entrypoint.sh"]

CMD ["uwsgi",  "--ini", "container/uwsgi.ini"]
